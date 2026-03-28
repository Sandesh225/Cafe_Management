from utils import print_error, OutofStockError
from typing import Dict
import db

# Load inventory at module level
inventory = db.get_inventory()

def check_inventory(item: str, quantity: int) -> bool:
    """Check if the item is available in stock. Raises OutofStockError if not."""
    # Refresh inventory from DB to ensure real-time data
    global inventory
    inventory = db.get_inventory()
    
    stock = inventory.get(item, {}).get("qty", 0)
    if stock >= quantity:
        return True
    raise OutofStockError(f"Insufficient stock for {item}. Only {stock} remaining.")

def update_inventory(order: Dict[str, int]) -> None:
    """Update the inventory after an order is placed and save to database."""
    global inventory
    inventory = db.get_inventory() # Refresh
    
    for item, quantity in order.items():
        if item in inventory:
            inventory[item]['qty'] -= quantity
    
    # Save updated inventory to DB
    db.save_inventory(inventory)

