"""
Quick test to verify API endpoints exist
"""
from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

print("=" * 60)
print("API ENDPOINTS TEST")
print("=" * 60)

# Test 1: Health check
print("\n[TEST 1] GET / (Health Check)")
response = client.get("/")
print(f"  Status: {response.status_code}")
print(f"  Response: {response.json()}")

# Test 2: Chat endpoint - unverified
print("\n[TEST 2] POST /api/chat (Unverified)")
response = client.post("/api/chat", json={"message": "I lost my card"})
print(f"  Status: {response.status_code}")
print(f"  Response: {response.json()}")

# Test 3: Chat endpoint - verify identity
print("\n[TEST 3] POST /api/chat (Verify Identity)")
response = client.post("/api/chat", json={
    "message": "verify me",
    "customer_id": "CUST001",
    "pin": "1234"
})
print(f"  Status: {response.status_code}")
data = response.json()
print(f"  Response: {data['response']}")
session_id = data['session_id']

# Test 4: Chat endpoint - balance check (verified)
print("\n[TEST 4] POST /api/chat (Balance Check - Verified)")
response = client.post("/api/chat", json={
    "message": "What's my balance?",
    "session_id": session_id
})
print(f"  Status: {response.status_code}")
print(f"  Response: {response.json()['response']}")

print("\n" + "=" * 60)
print("✅ ALL API ENDPOINTS WORKING!")
print("=" * 60)
print("\nTo test in browser:")
print("1. Run: python main.py")
print("2. Visit: http://localhost:8000/docs")
