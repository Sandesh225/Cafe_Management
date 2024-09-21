import json
import os
from menu import menu

orders_file = 'orders.json'

def take_order():
    """Take an order from the customer."""
    order = {}
    while True:
        item = input("\nEnter the item to order (or type 'done' to finish): ").capitalize()
        if item == 'Done':
            break
        elif item in menu:
            while True:
                try:
                    quantity = int(input(f"How many {item}(s) would you like? "))
                    if quantity <= 0:
                        print("Please enter a positive number.")
                    else:
                        break
                except ValueError:
                    print("Invalid input. Please enter a valid number.")
            order[item] = order.get(item, 0) + quantity
        else:
            print(f"Item {item} not available.")
    return order

def calculate_total(order):
    """Calculate the total cost of the order."""
    return sum(menu[item] * quantity for item, quantity in order.items())

def load_previous_orders():
    """Load previous orders from a JSON file."""
    if os.path.exists(orders_file):
        with open(orders_file, 'r') as file:
            return json.load(file)
    return []

def save_order(order, total):
    """Save the current order to the orders JSON file."""
    previous_orders = load_previous_orders()
    previous_orders.append({"order": order, "total": total})
    with open(orders_file, 'w') as file:
        json.dump(previous_orders, file, indent=4)
