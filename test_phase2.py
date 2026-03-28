import staff
import tables
import kitchen
import json
import os

def run_test():
    print("--- Starting Phase 2 Integration Test ---")
    
    # 1. Authenticate as admin
    s = staff.authenticate('admin', '1234')
    if not s or s['role'] != 'manager':
        print("FAIL: Admin authentication failed")
        return
    print("PASS: Admin authentication")

    # 2. Init tables
    tables.init_default_tables()
    if not os.path.exists('tables.json'):
        print("FAIL: tables.json not created")
        return
    print("PASS: Table initialization")

    # 3. Assign T2 to order ORD-TEST
    success = tables.assign_table('T2', 'ORD-TEST')
    if not success:
        # Maybe T2 is already occupied from a previous manual run?
        # Force it free first
        tables.free_table('T2')
        success = tables.assign_table('T2', 'ORD-TEST')
        if not success:
            print("FAIL: Could not assign T2")
            return
    
    # Verify T2 is occupied
    all_tables = tables.load_tables()
    t2 = next((t for t in all_tables if t['id'] == 'T2'), None)
    if not t2 or t2['status'] != 'occupied':
        print(f"FAIL: T2 status is {t2.get('status')} instead of occupied")
        return
    print("PASS: Table assignment")

    # 4. Create kitchen ticket
    fake_order = {'order_id': 'ORD-TEST', 'items': [{'name': 'Latte', 'qty': 1}]}
    ticket = kitchen.add_ticket(fake_order, 'T2')
    if not ticket or ticket['status'] != 'queued':
        print("FAIL: Kitchen ticket creation")
        return
    print("PASS: Kitchen ticket creation")

    # 5. Update ticket status
    ticket_id = ticket['ticket_id']
    kitchen.update_status(ticket_id, "in_progress")
    
    queue = kitchen.load_queue()
    updated_ticket = next((tk for tk in queue if tk['ticket_id'] == ticket_id), None)
    if not updated_ticket or updated_ticket['status'] != 'in_progress':
        print(f"FAIL: Ticket status is {updated_ticket.get('status')} instead of in_progress")
        return
    print("PASS: Kitchen ticket status update")

    # 6. Free table
    tables.free_table('T2')
    all_tables = tables.load_tables()
    t2 = next((t for t in all_tables if t['id'] == 'T2'), None)
    if not t2 or t2['status'] != 'free':
        print("FAIL: Table T2 not freed")
        return
    print("PASS: Table release")

    print("\nALL PHASE 2 INTEGRATION TESTS PASSED! ✅")

if __name__ == "__main__":
    run_test()
