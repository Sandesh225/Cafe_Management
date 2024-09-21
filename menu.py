menu = {
    'Coffee': 3.5,
    'Tea': 2.5,
    'Sandwich': 5.0,
    'Cake': 4.0
}

def display_menu():
    """Display the available menu items."""
    print("\n--- Cafe Menu ---")
    for item, price in menu.items():
        print(f"{item}: ${price:.2f}")
