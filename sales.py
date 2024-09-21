import datetime
import json
import os

sales_file = 'sales.json'
sales_report = []

def load_sales():
    if os.path.exists(sales_file):
        with open(sales_file, 'r') as file:
            return json.load(file)
    return []

def save_sales(order, total, customer_id, customer_name):
    sale = {
        'order': order,
        'total': total,
        'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'customer_id': customer_id,
        'customer_name': customer_name
    }
    sales_report = load_sales()
    sales_report.append(sale)
    
    with open(sales_file, 'w') as file:
        json.dump(sales_report, file, indent=4)

def generate_sales_report():
    sales_report = load_sales()
    
    if sales_report:
        print("\n--- Sales Report ---")
        total_sales = 0
        for sale in sales_report:
            print(f"Order: {sale['order']}, Total: ${sale['total']:.2f}, Date: {sale['date']}, Customer: {sale['customer_name']} (ID: {sale['customer_id']})")
            total_sales += sale['total']
        print(f"\nTotal Sales: ${total_sales:.2f}")
    else:
        print("No sales data available.")
