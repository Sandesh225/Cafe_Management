inventory = {
    'Coffee': 50,
    'Tea': 50,
    'Sandwich': 30,
    'Cake': 20
}

def check_inventory(item, quantity):
    """Check if the item is available in stock."""
    if item in inventory and inventory[item] >= quantity:
        return True
    else:
        print(f"Insufficient stock for {item}. Only {inventory.get(item, 0)} left.")
        return False

def update_inventory(order):
    """Update the inventory after an order is placed."""
    for item, quantity in order.items():
        if item in inventory:
            inventory[item] -= quantity
            print(f"Updated {item} stock: {inventory[item]} remaining.")
