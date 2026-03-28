from utils import print_error, print_success, CustomerNotFoundError
from models import Customer
from typing import Dict, Optional
import db
import config

def get_customer(customer_id: str) -> Customer:
    """Retrieve a customer by ID from database. Raises CustomerNotFoundError if not found."""
    data = db.get_customer(customer_id)
    if not data:
        raise CustomerNotFoundError(f"Customer with ID {customer_id} not found.")
    return Customer(**data)

def add_new_customer(customer_id: str, name: str) -> None:
    """Add new customer if they do not exist in the system."""
    data = db.get_customer(customer_id)
    if not data:
        new_cust = Customer(id=customer_id, name=name)
        db.save_customer(new_cust.model_dump())
        print_success(f"Customer {name} added successfully.")
    else:
        print_success(f"Welcome back, {data['name']}!")

def add_order_to_customer(customer_id: str, order_items: Dict[str, int]) -> None:
    """Add order and update loyalty points for customers."""
    customer = get_customer(customer_id)
    customer.orders.append(order_items)
    customer.loyalty_points += 1
    db.save_customer(customer.model_dump())

def apply_loyalty_discount(customer_id: str, total_amount: float) -> float:
    """Apply a discount based on loyalty tiers from config."""
    try:
        customer = get_customer(customer_id)
        points = customer.loyalty_points
        
        tiers = config.get_loyalty_tiers()
        discount = 0
        for tier_pts, tier_disc in reversed(tiers):
            if points >= tier_pts:
                discount = tier_disc
                break
        
        if discount > 0:
            discounted_total = total_amount * (1 - discount / 100)
            from utils import console
            console.print(f"[success]Loyalty Discount Applied: {discount}% off![/success]")
            return discounted_total
    except CustomerNotFoundError:
        pass
    return total_amount
