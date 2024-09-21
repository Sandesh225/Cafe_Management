from menu import display_menu
from orders import take_order, calculate_total, save_order, load_previous_orders
from utils import print_receipt, generate_sales_report, save_sales
from customer import add_new_customer, add_order, apply_loyalty_discount, load_customers, save_customers
from inventory import check_inventory, update_inventory

def cafe_management():
    # Load previous orders and customers at the start of the system
    customers = load_customers()
    previous_orders = load_previous_orders()

    if previous_orders:
        print("\n--- Previous Orders ---")
        for i, order in enumerate(previous_orders, 1):
            print(f"Order {i}: {order['order']}, Total: ${order['total']:.2f}")
    else:
        print("\nNo previous orders found.")

    while True:
        print("\n--- Welcome to the Cafe ---")
        display_menu()

        # Ask for customer ID and handle customer-related tasks
        customer_id = input("Enter customer ID: ").strip()
        customer_name = input("Enter customer name: ").strip()

        # Add new customer or verify existing customer
        add_new_customer(customer_id, customer_name)

        # Take the order from the customer
        order = take_order()

        if not order:
            print("No order placed.")
        else:
            # Check inventory for each item
            if not all(check_inventory(item, qty) for item, qty in order.items()):
                print("Order cannot be placed due to insufficient stock.")
                continue

            # Calculate total and apply loyalty discounts
            total = calculate_total(order)
            total_with_discount = apply_loyalty_discount(customer_id, total)

            # Print the receipt
            print_receipt(order, total_with_discount)

            # Save order, update customer data, and update inventory
            save_order(order, total_with_discount)
            add_order(order, customer_id)
            update_inventory(order)

            # Save sales data
            save_sales(order, total_with_discount)

        # Ask if the user wants to continue
        if input("\nWould you like to order again? (yes/no): ").lower() != 'yes':
            print("Thank you for visiting!")
            break

    # Save customer data before exiting
    save_customers()

if __name__ == "__main__":
    cafe_management()
