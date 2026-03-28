# ☕ Premium Cafe Management System - Run Guide

Version: 2.1 (Phase 3)

## 🚀 How to Run

1.  **Dependencies**: Ensure you have Python 3.8+ and the required packages installed:
    ```bash
    pip install pydantic rich
    ```

2.  **Launch**:
    ```bash
    python cafe.py
    ```

## 🔐 Default Credentials
The system starts with a login gate. Use the following default admin credentials:
- **Staff ID**: `admin`
- **PIN**: `1234`

## 📂 System Modules
- **Ordering (1)**: Take customer orders, assign tables (T1-T8), and send KOT (Kitchen Order Tickets).
- **Manager Mode (2)**: View high-level daily revenue and stock alerts.
- **Reports (R)**: Advanced analytics (Daily Summary, Top Sellers, Peak Hours, Staff Shifts).
- **Kitchen View (K)**: Real-time order tracking and status updates (In Progress -> Ready -> Served).

## 📊 Phase 3 Features
- **Daily Summary**: Tracks gross/net revenue vs previous day.
- **Top Sellers**: Shows which items contribute most to your sales.
- **Peak Hours**: Discover when your cafe is busiest with ASCII heatmaps.
- **Staff Shifts**: Automated time-tracking of logins and logouts.

## 🛠 Troubleshooting
- **Missing Files**: On first run, the system will create skeleton JSON files (`staff.json`, `inventory.json`, etc.).
- **Permissions**: If you cannot see the "Reports" option, ensure your staff role is set to `manager` in `staff.json`.
- **Errors**: Check `utils.py` for custom exception logic if the system blocks an order (e.g., `OutofStockError`).
