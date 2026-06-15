import db
from menu import menu
from utils import console, print_error
from models import Order
from typing import Dict
from datetime import datetime

def get_sales_list():
    """Load sales from database."""
    return db.get_sales()

def take_order() -> Dict[str, int]:
    """Take an order from the customer."""
    order_items = {}
    while True:
        console.print("\n[bold cyan]Enter the item to order (or type 'done' to finish):[/bold cyan] ", end="")
        item = input().strip().capitalize()
        
        if item == 'Done':
            break
        elif item in menu:
            while True:
                try:
                    console.print(f"[bold cyan]How many {item}(s) would you like?[/bold cyan] ", end="")
                    quantity = int(input().strip())
                    if quantity <= 0:
                        print_error("Please enter a positive number.")
                    else:
                        break
                except ValueError:
                    print_error("Invalid input. Please enter a valid number.")
            order_items[item] = order_items.get(item, 0) + quantity
        else:
            print_error(f"Item '{item}' not available on the menu.")
            
    return order_items

def calculate_total(order_items: Dict[str, int]) -> float:
    """Calculate the total cost of the order."""
    return sum(menu[item] * quantity for item, quantity in order_items.items())

def save_order(order_items: Dict[str, int], total: float, payment_method: str = "Cash") -> None:
    """Save the current order to the database."""
    from uuid import uuid4
    order_id = f"ORD-{str(uuid4())[:8]}"
    new_order = {
        "order_id": order_id,
        "total": total,
        "payment_method": payment_method,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "items": order_items
    }
    db.save_order(new_order)

def load_previous_orders() -> list:
    """Return all historical orders."""
    return db.get_orders()

