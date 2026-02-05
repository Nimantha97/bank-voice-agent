import sys
sys.path.insert(0, '.')

from app.agent import classify_intent, process_message

print("=" * 60)
print("TESTING PHASE 3: AI AGENT CORE")
print("=" * 60)

# Test 1: Intent Classification
print("\n[TEST 1] Intent Classification")
test_messages = [
    "I lost my credit card",
    "What's my account balance?",
    "I want to open a new account",
    "I can't login to the app",
    "My transfer failed",
    "I want to close my account"
]

for msg in test_messages:
    intent = classify_intent(msg)
    print(f"  '{msg}' -> {intent}")

# Test 2: Card Issue Flow (Unverified)
print("\n[TEST 2] Card Issue Flow (Unverified)")
result = process_message("I lost my card", None, False)
print(f"  Response: {result['response']}")
print(f"  Requires Verification: {result.get('requires_verification', False)}")

# Test 3: Account Servicing (Verified)
print("\n[TEST 3] Account Servicing - Balance Check (Verified)")
result = process_message("What's my balance?", "CUST001", True)
print(f"  Response: {result['response']}")
print(f"  Flow: {result.get('flow')}")

# Test 4: Transaction History
print("\n[TEST 4] Account Servicing - Transaction History (Verified)")
result = process_message("Show me my recent transactions", "CUST001", True)
print(f"  Response: {result['response'][:100]}...")

# Test 5: Simple Flow Routing
print("\n[TEST 5] Simple Flow Routing")
result = process_message("I want to open a new account", None, False)
print(f"  Response: {result['response']}")
print(f"  Flow: {result.get('flow')}")

print("\n" + "=" * 60)
print("PHASE 3 TESTS COMPLETE")
print("=" * 60)
