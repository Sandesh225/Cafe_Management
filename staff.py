import hashlib
from typing import Dict, List, Optional
from datetime import datetime
import db

# Allowed actions per role
ROLE_PERMISSIONS = {
    "manager": ["order", "menu_edit", "inventory_edit", "reports", "staff_manage"],
    "barista": ["order", "view_inventory"],
    "cashier": ["order", "reports"]
}

def load_staff() -> dict:
    """Load staff data from database, creating a default admin if none exist."""
    staff_list = db.get_staff()
    if not staff_list:
        default_admin = {
            "id": "admin",
            "name": "Admin",
            "pin_hash": hash_pin("1234"),
            "role": "manager",
            "active": 1
        }
        db.save_staff_record(default_admin)
        return {"admin": default_admin}

    return {s['id']: dict(s) for s in staff_list}

def save_staff(data: dict) -> None:
    """Save all staff records to database."""
    for record in data.values():
        db.save_staff_record(record)

def hash_pin(pin: str) -> str:
    """Hash a PIN using SHA-256."""
    return hashlib.sha256(pin.encode()).hexdigest()

def authenticate(staff_id: str, pin: str) -> Optional[dict]:
    """Authenticate a staff member by ID and PIN. Returns staff record or None."""
    staff_data = load_staff()
    staff_rec = staff_data.get(staff_id)
    if staff_rec and staff_rec.get("active") and staff_rec.get("pin_hash") == hash_pin(pin):
        return staff_rec
    return None

def can_do(staff_rec: dict, action: str) -> bool:
    """Check if a staff member is allowed to perform a specific action."""
    role = staff_rec.get("role")
    return action in ROLE_PERMISSIONS.get(role, [])

def add_staff(manager: dict, new_staff: dict) -> bool:
    """Add a new staff member. Only managers can perform this action."""
    if manager.get("role") != "manager":
        return False
    
    staff_data = load_staff()
    staff_id = new_staff.get("id")
    if staff_id in staff_data:
        return False  # Staff ID already exists
    
    # Ensure PIN is hashed before saving if it's passed as plain text
    if "pin" in new_staff:
        new_staff["pin_hash"] = hash_pin(new_staff.pop("pin"))
    
    if "active" not in new_staff:
        new_staff["active"] = 1
        
    db.save_staff_record(new_staff)
    return True

def log_shift(staff_id: str, event: str) -> None:
    """Log a shift event (login/logout) to database."""
    db.log_shift_db(staff_id, event)
