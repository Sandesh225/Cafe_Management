from datetime import datetime, timedelta, date
from typing import List, Dict, Optional, Any, Union
import json
from collections import Counter
import staff  # For can_do check and role info
from rich.console import Console # For dashboard
from rich.table import Table # For dashboard
import db

console_rich = Console()

def show_manager_dashboard(staff_record: dict) -> None:
    """Legacy wrapper for the manager dashboard, now showing the Daily Summary."""
    console_rich.print(f"\n[bold magenta]📊 Manager Dashboard | Viewed by: {staff_record['name']}[/bold magenta]")
    daily_summary()

# --- HELPER FUNCTIONS ---

def parse_utc(ts: str) -> datetime:
    """Parse ISO 8601 UTC timestamp, handling 'Z' and '+00:00'."""
    if ts.endswith('Z'):
        ts = ts.replace('Z', '+00:00')
    return datetime.fromisoformat(ts)

def filter_by_date(records: list, target_date: date) -> list:
    """Filter records by a specific date."""
    return [r for r in records if parse_utc(r['timestamp']).date() == target_date]

def filter_by_week(records: list, target_date: date) -> list:
    """Filter records by the Mon-Sun week containing target_date."""
    start_of_week = target_date - timedelta(days=target_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    return [r for r in records if start_of_week <= parse_utc(r['timestamp']).date() <= end_of_week]

def filter_by_month(records: list, year: int, month: int) -> list:
    """Filter records by a specific year and month."""
    return [r for r in records if parse_utc(r['timestamp']).year == year and parse_utc(r['timestamp']).month == month]

# --- REPORTS ---

def daily_summary(date_obj: Optional[date] = None) -> None:
    """REPORT 1: Daily Summary with comparison to previous day."""
    if date_obj is None:
        date_obj = datetime.utcnow().date()
    
    sales = db.get_sales()
    today_sales = filter_by_date(sales, date_obj)
    prev_sales = filter_by_date(sales, date_obj - timedelta(days=1))
    
    def get_stats(records):
        total_orders = len(records)
        gross = sum(r['total'] + r.get('discount', 0) for r in records)
        discounts = sum(r.get('discount', 0) for r in records)
        net = sum(r['total'] for r in records)
        aov = net / total_orders if total_orders > 0 else 0
        return total_orders, gross, discounts, net, aov

    t_count, t_gross, t_disc, t_net, t_aov = get_stats(today_sales)
    p_count, p_gross, p_disc, p_net, p_aov = get_stats(prev_sales)
    
    revenue_change = ((t_net - p_net) / p_net * 100) if p_net > 0 else 100 if t_net > 0 else 0

    print(f"\n--- DAILY SUMMARY: {date_obj} ---")
    print(f"{'Metric':<25} {'Value':<15}")
    print("-" * 40)
    print(f"{'Total Orders':<25} {t_count:<15}")
    print(f"{'Gross Revenue':<25} ${t_gross:<14.2f}")
    print(f"{'Total Discounts':<25} ${t_disc:<14.2f}")
    print(f"{'Net Revenue':<25} ${t_net:<14.2f}")
    print(f"{'Avg Order Value':<25} ${t_aov:<14.2f}")
    print("-" * 40)
    print(f"{'vs Previous Day':<25} {revenue_change:+.1f}% revenue")

def top_selling(date_obj: Optional[date] = None, period: str = "day", top_n: int = 10) -> None:
    """REPORT 2: Top Selling Items."""
    if date_obj is None:
        date_obj = datetime.utcnow().date()
    
    orders_all = db.get_orders()
    if period == "day":
        orders = filter_by_date(orders_all, date_obj)
    elif period == "week":
        orders = filter_by_week(orders_all, date_obj)
    else: # month
        orders = filter_by_month(orders_all, date_obj.year, date_obj.month)
    
    item_stats = {} # name -> qty
    total_qty = 0
    
    for order in orders:
        items = json.loads(order.get('items_json', '[]'))
        if isinstance(items, dict):
            for name, qty in items.items():
                item_stats[name] = item_stats.get(name, 0) + qty
                total_qty += qty
        else:
            for item in items:
                name = item['name']
                qty = item['qty']
                item_stats[name] = item_stats.get(name, 0) + qty
                total_qty += qty
                
    sorted_items = sorted(list(item_stats.items()), key=lambda x: x[1], reverse=True)[:top_n]

    print(f"\n--- TOP SELLING ITEMS ({period.upper()}): {date_obj} ---")
    print(f"{'Rank':<5} {'Item Name':<20} {'Qty Sold':<10} {'% of Total':<10}")
    print("-" * 50)
    for i, (name, qty) in enumerate(sorted_items, 1):
        pct = (qty / total_qty * 100) if total_qty > 0 else 0
        print(f"{i:<5} {name:<20} {qty:<10} {pct:>8.1f}%")

def peak_hours(date_obj: Optional[date] = None, period: str = "day") -> None:
    """REPORT 3: Peak Hours Bar Chart."""
    if date_obj is None:
        date_obj = datetime.utcnow().date()
    
    sales_all = db.get_sales()
    if period == "day":
        sales = filter_by_date(sales_all, date_obj)
    else: # week
        sales = filter_by_week(sales_all, date_obj)
        
    buckets = [0] * 24
    revenue_buckets = [0.0] * 24
    
    for s in sales:
        hour = parse_utc(s['timestamp']).hour
        buckets[hour] += 1
        revenue_buckets[hour] += s['total']
        
    max_val = max(buckets) if any(buckets) else 1
    
    indexed_buckets = sorted(list(enumerate(buckets)), key=lambda x: x[1], reverse=True)
    top_3_hours = [idx for idx, val in indexed_buckets[:3] if val > 0]

    print(f"\n--- PEAK HOURS ({period.upper()}): {date_obj} ---")
    for h in range(24):
        bar_count = int((buckets[h] / max_val) * 30) if max_val > 0 else 0
        bar = "█" * bar_count
        
        prefix = "\033[32m" if h in top_3_hours else ""
        suffix = "\033[0m" if h in top_3_hours else ""
        
        print(f"{h:02d}:00 {prefix}{bar:<30}{suffix} {buckets[h]:>3} orders (${revenue_buckets[h]:>7.2f})")

def staff_shift_report(date_obj: Optional[date] = None, period: str = "day") -> None:
    """REPORT 4: Staff Shift Report."""
    if date_obj is None:
        date_obj = datetime.utcnow().date()
        
    shifts_all = db.get_shifts()
    staff_all = db.get_staff()
    staff_lookup = {s['id']: s for s in staff_all}

    if period == "day":
        shifts = [s for s in shifts_all if parse_utc(s['timestamp']).date() == date_obj]
    else: # week
        start_of_week = date_obj - timedelta(days=date_obj.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        shifts = [s for s in shifts_all if start_of_week <= parse_utc(s['timestamp']).date() <= end_of_week]

    staff_hours = {} # id -> {name, role, count, total_seconds, last_login}
    
    shifts.sort(key=lambda x: x['timestamp'])
    
    for s in shifts:
        s_id = s['staff_id']
        if s_id not in staff_hours:
            s_info = staff_lookup.get(s_id, {"name": s_id, "role": "N/A"})
            staff_hours[s_id] = {"name": s_info['name'], "role": s_info['role'], "count": 0, "total_seconds": 0, "last_login": None}
        
        if s['event'] == "login":
            staff_hours[s_id]['last_login'] = parse_utc(s['timestamp'])
            staff_hours[s_id]['count'] += 1
        elif s['event'] == "logout" and staff_hours[s_id]['last_login']:
            diff = parse_utc(s['timestamp']) - staff_hours[s_id]['last_login']
            staff_hours[s_id]['total_seconds'] += diff.total_seconds()
            staff_hours[s_id]['last_login'] = None

    print(f"\n--- STAFF SHIFT REPORT ({period.upper()}): {date_obj} ---")
    print(f"{'Staff Name':<15} {'Role':<10} {'Shifts':<8} {'Total Hours':<12}")
    print("-" * 50)
    for s_id, data in staff_hours.items():
        h = int(data['total_seconds'] // 3600)
        m = int((data['total_seconds'] % 3600) // 60)
        time_str = f"{h:02d}:{m:02d}"
        if data['last_login']:
            time_str += " (OPEN)"
        print(f"{data['name']:<15} {data['role']:<10} {data['count']:<8} {time_str:<12}")

# --- MENU ---

def report_menu(current_staff: dict) -> None:
    """Manager report menu."""
    if not staff.can_do(current_staff, "reports"):
        raise PermissionError("Access Denied: You do not have permission to view reports.")

    while True:
        print("\n--- 📊 REPORTS MENU ---")
        print("[1] Daily Summary")
        print("[2] Top Selling Items")
        print("[3] Peak Hours")
        print("[4] Staff Shift Report")
        print("[Q] Back")
        
        choice = input("\nSelect a report: ").strip().lower()
        if choice == 'q':
            break
            
        if choice not in ['1', '2', '3', '4']:
            print("Invalid choice.")
            continue
            
        date_input = input("Date YYYY-MM-DD (Enter for Today): ").strip()
        try:
            date_obj = datetime.strptime(date_input, "%Y-%m-%d").date() if date_input else datetime.utcnow().date()
        except ValueError:
            print("Invalid date format.")
            continue
            
        if choice in ['2', '3', '4']:
            period = input("Period (day/week/month): ").strip().lower()
            if period not in ['day', 'week', 'month']:
                print("Invalid period.")
                continue
        
        if choice == '1':
            daily_summary(date_obj)
        elif choice == '2':
            top_selling(date_obj, period)
        elif choice == '3':
            if period == 'month':
                print("Peak hours only supports 'day' or 'week'.")
                continue
            peak_hours(date_obj, period)
        elif choice == '4':
            if period == 'month':
                print("Shift report only supports 'day' or 'week'.")
                continue
            staff_shift_report(date_obj, period)
            
        input("\nPress Enter to return to Report Menu...")
