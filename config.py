import os
from typing import List, Tuple

# Default settings
DEFAULT_CONFIG = {
    "DB_PATH": "cafe.db",
    "TAX_RATE": "0.0",
    "CURRENCY_SYMBOL": "$",
    "LOW_STOCK_THRESHOLD": "10",
    "LOYALTY_TIERS": "0:0,10:5,20:10,30:15",
    "API_PORT": "5000",
    "LOG_LEVEL": "WARNING"
}

def load_env() -> dict:
    """Read .env file manually from project root."""
    config = DEFAULT_CONFIG.copy()
    env_path = ".env"
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    config[key.strip()] = value.strip()
    return config

# Single CONFIG dict
CONFIG = load_env()

def get(key: str) -> str:
    return CONFIG.get(key, DEFAULT_CONFIG.get(key, ""))

def get_float(key: str) -> float:
    try:
        return float(get(key))
    except ValueError:
        return float(DEFAULT_CONFIG.get(key, 0.0))

def get_int(key: str) -> int:
    try:
        return int(get(key))
    except ValueError:
        return int(DEFAULT_CONFIG.get(key, 0))

def get_loyalty_tiers() -> List[Tuple[int, int]]:
    """Returns sorted list of (points, discount_pct) tuples."""
    raw = get("LOYALTY_TIERS")
    tiers = []
    try:
        for pair in raw.split(","):
            pts, disc = pair.split(":")
            tiers.append((int(pts), int(disc)))
    except (ValueError, AttributeError):
        return [(0,0), (10,5), (20,10), (30,15)]
    return sorted(tiers, key=lambda x: x[0])
