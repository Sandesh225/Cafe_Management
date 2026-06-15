from menu import display_menu, menu
from orders import take_order, calculate_total, save_order, load_previous_orders
from utils import (
    print_receipt, print_error, print_success, print_info, console, 
    OutofStockError, CustomerNotFoundError
)
from customer import (
    add_new_customer, add_order_to_customer, apply_loyalty_discount
)
from inventory import check_inventory, update_inventory
import reports
import kitchen
from reports import show_manager_dashboard
from datetime import datetime
from typing import Optional
import staff
import tables
import sys
from rich.panel import Panel

def login_gate() -> Optional[dict]:
    """Force staff login before accessing the system. Returns staff record or exits."""
    attempts = 0
    while attempts < 3:
        console.clear()
        console.print(Panel.fit(
            "[bold highlight]🔐 Staff Login Required[/bold highlight]",
            border_style="highlight"
        ))
        staff_id = input("\nEnter Staff ID: ").strip()
        pin = input("Enter PIN: ").strip()
        
        current_staff = staff.authenticate(staff_id, pin)
        if current_staff:
            staff.log_shift(staff_id, "login")
            print_success(f"Login successful! Welcome, {current_staff['name']}.")
            return current_staff
        else:
            attempts += 1
            print_error(f"Invalid ID or PIN. {3 - attempts} attempts remaining.")
            input("\nPress Enter to try again...")
            
    print_error("Too many failed attempts. Access denied.")
    sys.exit()

def main_loop():
    """Main application loop with authentication gate."""
    current_staff = login_gate()
    
    while True:
        console.clear()
        console.print(Panel.fit(
            f"[bold magenta]☕ Premium Cafe System | Logged in: {current_staff['name']}[/bold magenta]",
            border_style="magenta"
        ))
        
        print_info("1. Customer Order")
        
        # Reports and Manager Mode are for authorized staff
        if staff.can_do(current_staff, "reports"):
            print_info("2. Manager Mode")
            print_info("R. Reports")
            
        # Kitchen View is only for baristas and managers
        if current_staff['role'] in ['manager', 'barista']:
            print_info("K. Kitchen View")
            
        print_info("3. Exit (Q)")
        
        choice = input("\nSelect an option: ").strip().lower()
        
        if choice == '1':
            handle_customer_order()
        elif choice == '2':
            if staff.can_do(current_staff, "reports"):
                show_manager_dashboard(current_staff)
            else:
                print_error("Permission denied: You do not have access to manager dashboard.")
            input("\nPress Enter to return to main menu...")
        elif choice == 'r':
            try:
                reports.report_menu(current_staff)
            except PermissionError as e:
                print_error(str(e))
                input("\nPress Enter to return...")
        elif choice == 'k':
            kitchen.kitchen_view(current_staff)

        elif choice in ['3', 'q']:
            staff.log_shift(current_staff['id'], "logout")
            print_success("Session ended. Data saved. Goodbye!")
            break
        else:
            print_error("Invalid choice.")
            input("\nPress Enter to try again...")


def handle_payment(total: float) -> str:
    """Handle customer payment and return payment method."""
    print_info(f"\nTotal Amount Due: ${total:.2f}")
    print("Select Payment Method:")
    print("1. Cash | 2. Card | 3. Mobile Pay")
    choice = input("Choice (default Cash): ").strip()
    return {"1": "Cash", "2": "Card", "3": "Mobile Pay"}.get(choice, "Cash")

def handle_customer_order():
    """Handle the end-to-end customer ordering process with table & kitchen integration."""
    try:
        # Table Selection
        tables.display_tables()
        free_tables = tables.get_free_tables()
        if not free_tables:
            print_error("No free tables available!")
            return
            
        table_id = input("\nSelect Table ID (e.g., T1): ").strip().upper()
        match = [t for t in free_tables if t['id'] == table_id]
        if not match:
            print_error("Invalid or occupied table selection.")
            return
        table_label = match[0]['label']

        # Customer Identification
        customer_id = input("Enter customer ID: ").strip()
        if not customer_id:
            print_error("Customer ID is required.")
            return

        customer_name = input("Enter customer name: ").strip()
        add_new_customer(customer_id, customer_name)

        # Show Menu
        display_menu()

        # Take Order
        order_items = take_order()
        if not order_items:
            print_info("No items selected. Cancelling order.")
            return

        # Validate Inventory
        for item, qty in order_items.items():
            check_inventory(item, qty)

        # Calculate Total and Discounts
        total = calculate_total(order_items)
        final_total = apply_loyalty_discount(customer_id, total)

        # Finalize Order
        print_receipt(order_items, menu, final_total)
        
        confirm = input("\nConfirm order? (yes/no): ").lower()
        if confirm == 'yes':
            # Payment Step
            payment_method = handle_payment(final_total)
            
            # Assign table to order (using a temporary order ID or just a placeholder)
            order_id = f"ORD-{datetime.now().strftime('%H%M%S')}"
            tables.assign_table(table_id, order_id)
            
            save_order(order_items, final_total, payment_method)
            add_order_to_customer(customer_id, order_items)
            update_inventory(order_items)
            
            # Send to Kitchen
            order_dict = {"order_id": order_id, "items": order_items}
            ticket = kitchen.add_ticket(order_dict, table_label)
            
            print_success(f"Order {order_id} placed! Table: {table_id}")
            print_info(f"KOT sent → {ticket['ticket_id']}")
            
            # Now free it since the "bill was printed" and confirmed? 
            tables.free_table(table_id)
        else:
            print_info("Order cancelled.")

    except OutofStockError as e:
        print_error(str(e))
    except CustomerNotFoundError as e:
        print_error(str(e))
    except Exception as e:
        print_error(f"An unexpected error occurred: {e}")
    
    input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print_info("\nSystem shutdown requested. Saving data...")
        print_success("Data saved. Goodbye!")

