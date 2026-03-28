import uuid
import json
from datetime import datetime
from typing import List, Dict, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import db

console = Console()

def load_queue() -> List[dict]:
    """Load the kitchen queue from database."""
    rows = db.get_queue()
    for r in rows:
        if 'items_json' in r:
            r['items'] = json.loads(r.pop('items_json'))
    return rows

def save_queue(data: List[dict]) -> None:
    """Save all tickets to database (batch)."""
    for ticket in data:
        db.save_ticket(ticket)

def add_ticket(order: dict, table_label: str) -> dict:
    """Create a new kitchen ticket and add it to the queue."""
    ticket = {
        "ticket_id": str(uuid.uuid4())[:8],
        "order_id": order.get("order_id", "N/A"),
        "table_label": table_label,
        "items": order.get("items", []),
        "status": "queued",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "updated_at": datetime.utcnow().isoformat() + "Z"
    }
    db.save_ticket(ticket)
    return ticket

def update_status(ticket_id: str, new_status: str) -> bool:
    """Update the status of a kitchen ticket."""
    ticket = db.get_one('kitchen', 'ticket_id', ticket_id)
    if ticket:
        ticket = dict(ticket) # Convert sqlite3.Row to dict
        ticket["status"] = new_status
        ticket["updated_at"] = datetime.utcnow().isoformat() + "Z"
        # Load items back as dict so save_ticket can re-serialize to items_json
        if 'items_json' in ticket:
             ticket['items'] = json.loads(ticket.pop('items_json'))
        return db.save_ticket(ticket)
    return False

def get_active_tickets() -> List[dict]:
    """Return tickets that haven't been served yet."""
    return [t for t in load_queue() if t["status"] != "served"]

def display_queue() -> None:
    """Display the kitchen queue board."""
    tickets = get_active_tickets()
    if not tickets:
        console.print("[yellow]Kitchen queue is empty.[/yellow]")
        return

    table = Table(title="🍳 Kitchen Status Board", show_header=True, header_style="bold magenta")
    table.add_column("Ticket ID", style="cyan")
    table.add_column("Table", justify="center")
    table.add_column("Items")
    table.add_column("Status", justify="center")
    table.add_column("Age (min)", justify="right")

    now = datetime.utcnow()
    for t in tickets:
        # Handle timestamp parsing with 'Z'
        ts_str = t["created_at"].replace('Z', '+00:00')
        created_at = datetime.fromisoformat(ts_str).replace(tzinfo=None)
        age_min = int((now - created_at).total_seconds() / 60)
        
        age_style = "yellow" if age_min > 10 else "white"
        items = t.get("items", [])
        if isinstance(items, dict):
            items_str = ", ".join([f"{qty}x {name}" for name, qty in items.items()])
        else:
            items_str = ", ".join([f"{item.get('qty', 1)}x {item.get('name', 'Item')}" for item in items])

        table.add_row(
            t["ticket_id"],
            t["table_label"],
            items_str,
            t["status"],
            f"[{age_style}]{age_min}[/{age_style}]"
        )
    
    console.print(table)

def kitchen_view(current_staff: dict) -> None:
    """Interactive kitchen management loop."""
    if current_staff.get("role") not in ["manager", "barista"]:
        console.print("[bold red]Access Denied: Only Managers and Baristas can access Kitchen View.[/bold red]")
        input("\nPress Enter to return...")
        return

    while True:
        console.clear()
        console.print(Panel.fit("👨‍🍳 Kitchen View", border_style="cyan"))
        display_queue()
        
        print("\nOptions: [ID] to update status, [Q] to exit")
        choice = input("Select Ticket ID or Option: ").strip().lower()
        
        if choice == 'q':
            break
            
        ticket = db.get_one('kitchen', 'ticket_id', choice)
        if ticket:
            print(f"\nUpdating Ticket {ticket['ticket_id']} (Current: {ticket['status']})")
            print("1. In Progress | 2. Ready | 3. Served | 4. Cancel")
            status_choice = input("Select new status (1-4): ").strip()
            
            status_map = {"1": "in_progress", "2": "ready", "3": "served", "4": "queued"}
            if status_choice in status_map:
                update_status(ticket["ticket_id"], status_map[status_choice])
                console.print(f"[success]Ticket {ticket['ticket_id']} updated to {status_map[status_choice]}.[/success]")
            else:
                console.print("[error]Invalid status choice.[/error]")
            input("\nPress Enter to continue...")
        else:
            console.print("[error]Ticket ID not found.[/error]")
            input("\nPress Enter to continue...")
