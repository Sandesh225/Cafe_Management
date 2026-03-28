import db
from rich.table import Table
from utils import console

# Load menu from database
def get_raw_menu() -> dict:
    db_menu = db.get_menu()
    # Extract {name: price} for compatibility with orders.py
    return {name: data['price'] for name, data in db_menu.items()}

menu = get_raw_menu()

def display_menu() -> None:
    """Display the available menu items using a formatted Rich Table."""
    table = Table(title="[bold magenta]☕ Cafe Menu[/bold magenta]", show_header=True, header_style="bold cyan")
    table.add_column("Item", style="cyan", no_wrap=True)
    table.add_column("Price", justify="right", style="green")

    for item, price in menu.items():
        table.add_row(item, f"${price:.2f}")

    console.print(table)

