from typing import List, Dict, Optional
from datetime import datetime
import db

def load_tables() -> List[dict]:
    """Load tables from database."""
    return db.get_tables()

def save_tables(data: List[dict]) -> None:
    """Save all tables to database."""
    for record in data:
        db.save_table(record)

def get_free_tables() -> List[dict]:
    """Return a list of tables that are currently free."""
    tables = load_tables()
    return [t for t in tables if t.get("status") == "free"]

def assign_table(table_id: str, order_id: str) -> bool:
    """Assign a table to an order and mark as occupied."""
    table = db.get_one('tables_', 'id', table_id)
    if table and table["status"] == "free":
        table["status"] = "occupied"
        table["current_order_id"] = order_id
        table["opened_at"] = datetime.utcnow().isoformat() + "Z"
        return db.save_table(dict(table))
    return False

def free_table(table_id: str) -> bool:
    """Mark a table as free."""
    table = db.get_one('tables_', 'id', table_id)
    if table:
        table["status"] = "free"
        table["current_order_id"] = None
        table["opened_at"] = None
        return db.save_table(dict(table))
    return False

def display_tables() -> None:
    """Display tables in an ASCII grid format."""
    tables = load_tables()
    if not tables:
        print("No tables configured.")
        return

    print("\n--- Cafe Tables Grid ---")
    for i, t in enumerate(tables):
        status_symbol = "🟢" if t["status"] == "free" else "🔴" if t["status"] == "occupied" else "🟡"
        print(f"[{t['label']}] Seats: {t['seats']} {status_symbol}", end="\t")
        if (i + 1) % 4 == 0:
            print()
    print("\n------------------------")

def init_default_tables(count: int = 8) -> None:
    """Initialize default tables if none exist."""
    if not db.get_tables():
        for i in range(1, count + 1):
            db.save_table({
                "id": f"T{i}",
                "label": f"T{i}",
                "seats": 4,
                "status": "free",
                "current_order_id": None,
                "opened_at": None
            })
