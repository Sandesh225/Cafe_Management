import json
import os

customers = {}

def load_customers():
    """Load existing customers from the file, or return an empty dict if none exists."""
    if os.path.exists("customers.json"):
        with open("customers.json", "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}  # Return empty dictionary if the file is corrupt
    return {}

def save_customers():
    """Save customer data without overwriting the existing data."""
    with open("customers.json", "w") as file:
        json.dump(customers, file, indent=4)
        print("Customer data saved.")

def add_new_customer(customer_id, name):
    """Add new customer if they do not exist in the system."""
    customers_data = load_customers()
    if customer_id not in customers_data:
        customers[customer_id] = {'name': name, 'orders': [], 'loyalty_points': 0}
        print(f'Customer {name} added successfully.')
    else:
        print(f'Customer ID {customer_id} already exists.')

def add_order(order, customer_id):
    """Add order and update loyalty points for existing customers."""
    if customer_id in customers:
        customers[customer_id]['orders'].append(order)
        customers[customer_id]['loyalty_points'] += 1
        print(f"Order {order} added for {customers[customer_id]['name']}.")

def apply_loyalty_discount(customer_id, total_amount):
    """Apply a discount based on loyalty points (1 point per order, 10 points = 10% off)."""
    if customer_id in customers:
        points = customers[customer_id]['loyalty_points']
        discount = min(points // 10, 50)  # Max discount 50%
        discounted_total = total_amount * (1 - discount / 100)
        print(f"Loyalty Discount Applied: {discount}% off")
        return discounted_total
    return total_amount
