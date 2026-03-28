import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Any, Union

DB_PATH = "cafe.db"

# --- CONNECTION ---
def get_connection():
    """Returns a sqlite3 connection with dict row factory."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# Global connection for module-level use
db_conn = get_connection()

# --- SCHEMA INITIALIZATION ---
def init_db():
    """Create tables if they don't exist."""
    cursor = db_conn.cursor()
    
    # Tables
    cursor.executescript("""
    DROP TABLE IF EXISTS customers;
    CREATE TABLE customers (
        id TEXT PRIMARY KEY,
        name TEXT,
        loyalty_points INTEGER,
        orders_json TEXT,
        created_at TEXT
    );
    
    CREATE TABLE IF NOT EXISTS orders (
        order_id TEXT PRIMARY KEY,
        customer_id TEXT,
        table_id TEXT,
        staff_id TEXT,
        total REAL,
        discount REAL,
        timestamp TEXT,
        items_json TEXT
    );
    
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT,
        total REAL,
        discount REAL,
        timestamp TEXT
    );
    
    CREATE TABLE IF NOT EXISTS inventory (
        item TEXT PRIMARY KEY,
        qty INTEGER,
        reorder_threshold INTEGER
    );
    
    CREATE TABLE IF NOT EXISTS staff (
        id TEXT PRIMARY KEY,
        name TEXT,
        pin_hash TEXT,
        role TEXT,
        active INTEGER
    );
    
    CREATE TABLE IF NOT EXISTS shifts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        staff_id TEXT,
        event TEXT,
        timestamp TEXT
    );
    
    CREATE TABLE IF NOT EXISTS tables_ (
        id TEXT PRIMARY KEY,
        label TEXT,
        seats INTEGER,
        status TEXT,
        current_order_id TEXT,
        opened_at TEXT
    );
    
    CREATE TABLE IF NOT EXISTS kitchen (
        ticket_id TEXT PRIMARY KEY,
        order_id TEXT,
        table_label TEXT,
        items_json TEXT,
        status TEXT,
        created_at TEXT,
        updated_at TEXT
    );
    
    CREATE TABLE IF NOT EXISTS menu (
        item TEXT PRIMARY KEY,
        price REAL,
        category TEXT
    );
    """)
    db_conn.commit()

init_db()

# --- MIGRATION HELPER ---
def migrate_from_json():
    """Migrate data from JSON files to SQLite and rename files to .bak."""
    json_to_table = {
        'customers.json': ('customers', lambda d: d.values() if isinstance(d, dict) else d),
        'inventory.json': ('inventory', lambda d: [{'item': k, 'qty': v} for k, v in d.get('items', {}).items()] if 'items' in d else []),
        'menu.json': ('menu', lambda d: [{'item': k, 'price': v, 'category': 'General'} for k, v in d.get('items', {}).items()] if 'items' in d else []),
        'staff.json': ('staff', lambda d: d.values() if isinstance(d, dict) else d),
        'sales.json': ('orders', lambda d: d if isinstance(d, list) else d.get('transactions', [])),
        'shifts.json': ('shifts', lambda d: d),
        'tables.json': ('tables_', lambda d: d),
        'kitchen_queue.json': ('kitchen', lambda d: d)
    }
    
    print("--- Starting JSON to SQLite Migration ---")
    for filename, (table, transform) in json_to_table.items():
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                
                records = transform(data)
                count = 0
                for record in records:
                    # Specific fixes for table names or nested data
                    if table == 'orders' and 'items' in record:
                         record['items_json'] = json.dumps(record.pop('items'))
                    if table == 'kitchen' and 'items' in record:
                         record['items_json'] = json.dumps(record.pop('items'))
                         
                    if upsert(table, record):
                        count += 1
                
                print(f"Migrated {count} records from {filename} into {table}.")
                os.rename(filename, f"{filename}.bak")
                print(f"Renamed {filename} to {filename}.bak")
            except Exception as e:
                print(f"Error migrating {filename}: {e}")
    print("--- Migration Finished ---")

# --- GENERIC CRUD ---
def get_all(table: str) -> List[Dict]:
    """Fetch all rows from a table."""
    cursor = db_conn.cursor()
    cursor.execute(f"SELECT * FROM {table}")
    return [dict(row) for row in cursor.fetchall()]

def get_one(table: str, pk_col: str, pk_val: Any) -> Optional[Dict]:
    """Fetch a single row by primary key."""
    cursor = db_conn.cursor()
    cursor.execute(f"SELECT * FROM {table} WHERE {pk_col} = ?", (pk_val,))
    row = cursor.fetchone()
    return dict(row) if row else None

def upsert(table: str, record: Dict) -> bool:
    """Insert or replace a record in a table."""
    columns = list(record.keys())
    placeholders = ", ".join(["?"] * len(columns))
    col_str = ", ".join(columns)
    
    sql = f"INSERT OR REPLACE INTO {table} ({col_str}) VALUES ({placeholders})"
    try:
        db_conn.execute(sql, tuple(record.values()))
        db_conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error during upsert into {table}: {e}")
        db_conn.rollback()
        return False

def delete(table: str, pk_col: str, pk_val: Any) -> bool:
    """Delete a record from a table."""
    sql = f"DELETE FROM {table} WHERE {pk_col} = ?"
    try:
        db_conn.execute(sql, (pk_val,))
        db_conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error during delete from {table}: {e}")
        db_conn.rollback()
        return False

def query(sql: str, params: tuple = ()) -> List[Dict]:
    """Execute arbitrary read-only query."""
    cursor = db_conn.cursor()
    cursor.execute(sql, params)
    return [dict(row) for row in cursor.fetchall()]

# --- DOMAIN-SPECIFIC INTERFACE ---
def get_customer(customer_id: str) -> Optional[Dict]:
    data = get_one('customers', 'id', customer_id)
    if data:
        data = dict(data)
        if 'orders_json' in data:
            data['orders'] = json.loads(data.pop('orders_json'))
        return data
    return None

def save_customer(customer: Dict) -> bool:
    if 'orders' in customer and not isinstance(customer['orders'], str):
        customer['orders_json'] = json.dumps(customer.pop('orders'))
    if 'loyalty_points' not in customer and 'points' in customer:
        customer['loyalty_points'] = customer.pop('points')
    return upsert('customers', customer)

def get_inventory() -> Dict:
    rows = get_all('inventory')
    return {r['item']: {"qty": r['qty'], "reorder_threshold": r.get('reorder_threshold', 10)} for r in rows}

def save_inventory(inventory: Dict) -> bool:
    success = True
    for item, data in inventory.items():
        record = {
            "item": item,
            "qty": data.get("qty", data) if isinstance(data, dict) else data,
            "reorder_threshold": data.get("reorder_threshold", 10) if isinstance(data, dict) else 10
        }
        if not upsert('inventory', record): success = False
    return success

def get_orders(date: Optional[str] = None) -> List[Dict]:
    if date:
        return query("SELECT * FROM orders WHERE timestamp LIKE ?", (f"{date}%",))
    return get_all('orders')

def save_order(order: Dict) -> bool:
    # Ensure items are JSON string
    if 'items' in order and not isinstance(order['items'], str):
        order['items_json'] = json.dumps(order.pop('items'))
    
    if upsert('orders', order):
        # Also append to sales table
        sales_record = {
            "order_id": order['order_id'],
            "total": order['total'],
            "discount": order.get('discount', 0),
            "timestamp": order['timestamp']
        }
        return upsert('sales', sales_record)
    return False

def get_sales(start: Optional[str] = None, end: Optional[str] = None) -> List[Dict]:
    if start and end:
        return query("SELECT * FROM sales WHERE timestamp BETWEEN ? AND ?", (start, end))
    return get_all('sales')

def get_staff() -> List[Dict]:
    # Original staff.py expects a dict keyed by ID, but user prompt says list[dict]
    # I will stick to list[dict] as requested for Step 1
    return get_all('staff')

def save_staff_record(record: Dict) -> bool:
    return upsert('staff', record)

def get_shifts(start: Optional[str] = None, end: Optional[str] = None) -> List[Dict]:
    if start and end:
        return query("SELECT * FROM shifts WHERE timestamp BETWEEN ? AND ?", (start, end))
    return get_all('shifts')

def log_shift_db(staff_id: str, event: str) -> bool:
    record = {
        "staff_id": staff_id,
        "event": event,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    return upsert('shifts', record)

def get_tables() -> List[Dict]:
    return get_all('tables_')

def save_table(table: Dict) -> bool:
    return upsert('tables_', table)

def get_queue() -> List[Dict]:
    return get_all('kitchen')

def save_ticket(ticket: Dict) -> bool:
    if 'items' in ticket and not isinstance(ticket['items'], str):
        ticket['items_json'] = json.dumps(ticket.pop('items'))
    return upsert('kitchen', ticket)

def get_menu() -> Dict:
    rows = get_all('menu')
    return {r['item']: {"price": r['price'], "category": r.get('category', 'General')} for r in rows}

def save_menu_item(item: str, price: float, category: str) -> bool:
    return upsert('menu', {"item": item, "price": price, "category": category})
