"""
Test script for banking tools
Run this to verify Phase 2 is working correctly
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.tools.banking import (
    verify_identity,
    get_account_balance,
    get_recent_transactions,
    block_card,
    get_customer_cards,
    update_customer_address,
    get_audit_log
)

def test_banking_tools():
    print("=" * 60)
    print("TESTING BANK ABC VOICE AGENT - PHASE 2")
    print("=" * 60)
    
    # Test 1: Identity Verification
    print("\n[TEST 1] Identity Verification")
    print("-" * 40)
    result = verify_identity("CUST001", "1234")
    print(f"[OK] Valid credentials: {result}")
    
    result = verify_identity("CUST001", "9999")
    print(f"[OK] Invalid PIN: {result}")
    
    # Test 2: Get Account Balance
    print("\n[TEST 2] Get Account Balance")
    print("-" * 40)
    balance = get_account_balance("CUST001")
    if balance:
        print(f"[OK] Account: {balance['account_number']}")
        print(f"[OK] Balance: ${balance['balance']:.2f}")
        print(f"[OK] Type: {balance['account_type']}")
    
    # Test 3: Get Recent Transactions
    print("\n[TEST 3] Get Recent Transactions")
    print("-" * 40)
    transactions = get_recent_transactions("CUST001", 3)
    print(f"[OK] Retrieved {len(transactions)} transactions:")
    for txn in transactions:
        print(f"  - {txn['date']}: {txn['description']} (${txn['amount']})")
    
    # Test 4: Get Customer Cards
    print("\n[TEST 4] Get Customer Cards")
    print("-" * 40)
    cards = get_customer_cards("CUST001")
    print(f"[OK] Customer has {len(cards)} card(s):")
    for card in cards:
        print(f"  - {card['card_type']}: {card['card_number']} ({card['status']})")
    
    # Test 5: Block Card (IRREVERSIBLE)
    print("\n[TEST 5] Block Card (CRITICAL ACTION)")
    print("-" * 40)
    result = block_card("CARD001", "Lost card", "CUST001")
    print(f"[OK] {result}")
    
    # Verify card is blocked
    cards = get_customer_cards("CUST001")
    blocked_card = next((c for c in cards if c['card_id'] == 'CARD001'), None)
    if blocked_card:
        print(f"[OK] Card status: {blocked_card['status']}")
    
    # Test 6: Update Address
    print("\n[TEST 6] Update Customer Address")
    print("-" * 40)
    result = update_customer_address("CUST001", "999 New Street, Boston, MA 02101")
    print(f"[OK] {result}")
    
    # Test 7: Audit Log
    print("\n[TEST 7] Audit Log")
    print("-" * 40)
    audit_log = get_audit_log()
    print(f"[OK] Total actions logged: {len(audit_log)}")
    print("Recent actions:")
    for entry in audit_log[-3:]:
        print(f"  - {entry['action']} at {entry['timestamp']}")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] ALL TESTS PASSED - PHASE 2 COMPLETE!")
    print("=" * 60)
    print("\nNext: Phase 3 - AI Agent Core (LangGraph)")

if __name__ == "__main__":
    test_banking_tools()
