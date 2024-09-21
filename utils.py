from menu import menu
import json
import datetime

def print_receipt(order, total):
    """Print the receipt for the customer's order."""
    print("\n--- Receipt ---")
    for item, quantity in order.items():
        print(f"{item} x{quantity}: ${menu[item] * quantity:.2f}")
    print(f"Total: ${total:.2f}")

def save_sales(order, total):
    """Save the sales data to a JSON file."""
    sales_data = {
        'order': order,
        'total': total,
        'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open("sales.json", "a") as file:
        json.dump(sales_data, file)
        file.write("\n")

def generate_sales_report():
    """Generate a report of total sales."""
    try:
        with open("sales.json", "r") as file:
            sales = file.readlines()
        total_sales = sum(json.loads(sale)["total"] for sale in sales)
        print(f"\nTotal Sales: ${total_sales:.2f}")
    except FileNotFoundError:
        print("No sales data found.")
