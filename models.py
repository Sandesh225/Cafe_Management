from pydantic import BaseModel, Field, RootModel
from typing import List, Dict, Optional
from datetime import datetime

class MenuItem(BaseModel):
    """Model representing a single item in the cafe menu."""
    name: str
    price: float = Field(gt=0, description="Price must be greater than zero")

class InventoryItem(BaseModel):
    """Model representing stock levels for an item."""
    name: str
    stock: int = Field(ge=0, description="Stock cannot be negative")

class Order(BaseModel):
    """Model representing a customer order."""
    items: Dict[str, int] = Field(..., description="Dictionary of item names and quantities")
    total: float = Field(ge=0)
    date: datetime = Field(default_factory=datetime.now)

class Customer(BaseModel):
    """Model representing a customer and their loyalty status."""
    id: str
    name: str
    orders: List[Dict[str, int]] = Field(default_factory=list)
    loyalty_points: int = Field(default=0, ge=0)

class MenuData(BaseModel):
    """Model for the menu JSON file."""
    items: Dict[str, float]

class InventoryData(BaseModel):
    """Model for the inventory JSON file."""
    items: Dict[str, int]

class CustomerData(BaseModel):
    items: Dict[str, Customer]

class SalesData(RootModel):
    """Model for the sales JSON file (list of orders)."""
    root: List[Order]

