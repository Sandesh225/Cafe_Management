import json
import os
from typing import Any, Dict, List, Type, TypeVar, Union
from pydantic import BaseModel, ValidationError
from rich.console import Console, Group
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme

# Define a custom theme for the Cafe
cafe_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "highlight": "bold magenta",
})

console = Console(theme=cafe_theme)

T = TypeVar("T", bound=BaseModel)

def load_json_data(file_path: str, model: Type[T], default_data: Any) -> T:
    """
    Load data from a JSON file and validate it using a Pydantic model.
    Generates a template file if it doesn't exist.
    """
    if not os.path.exists(file_path):
        save_json_data(file_path, default_data)
        return model.model_validate(default_data) if hasattr(model, 'model_validate') else model(**default_data)

    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return model.model_validate(data)
    except (FileNotFoundError, json.JSONDecodeError, ValidationError) as e:
        console.print(f"[error]Error loading {file_path}: {e}[/error]")
        # Return default data if loading fails
        return model.model_validate(default_data)

def save_json_data(file_path: str, data: Union[BaseModel, Any]) -> None:
    """Save data to a JSON file, handling both Pydantic models and raw data."""
    try:
        with open(file_path, 'w') as file:
            if isinstance(data, BaseModel):
                file.write(data.model_dump_json(indent=4))
            else:
                json.dump(data, file, indent=4)
    except Exception as e:
        console.print(f"[bold red]Failed to save data to {file_path}: {e}[/bold red]")

def print_receipt(order_items: Dict[str, int], menu: Dict[str, float], total: float) -> None:
    """Print a styled receipt using Rich Panel and Table."""
    table = Table(show_header=True, header_style="bold magenta", box=None)
    table.add_column("Item", style="cyan")
    table.add_column("Qty", justify="right")
    table.add_column("Price", justify="right")
    table.add_column("Subtotal", justify="right")

    for item, qty in order_items.items():
        price = menu.get(item, 0.0)
        subtotal = price * qty
        table.add_row(item, str(qty), f"${price:.2f}", f"${subtotal:.2f}")

    totals_text = Text()
    totals_text.append(f"\n" + "-"*30 + "\n", style="dim")
    totals_text.append(f"Total: ${total:.2f}", style="bold green")

    receipt_group = Group(table, totals_text)
    console.print(Panel(receipt_group, title="[bold magenta]OFFICIAL RECEIPT[/bold magenta]", expand=False, border_style="magenta"))

def print_error(message: str) -> None:
    """Print an error message in bold red."""
    console.print(f"[bold red]ERROR: {message}[/bold red]")

def print_success(message: str) -> None:
    """Print a success message in green."""
    console.print(f"[bold green]{message}[/bold green]")

def print_info(message: str) -> None:
    """Print an info message in cyan."""
    console.print(f"[bold cyan]{message}[/bold cyan]")

class OutofStockError(Exception):
    """Custom exception when an item is out of stock."""
    pass

class CustomerNotFoundError(Exception):
    """Custom exception when a customer is not found."""
    pass
