#!/usr/bin/env python3
"""
Test script for conversation memory API endpoints
"""

import json
import sys
import time
from urllib.request import Request, urlopen
from urllib.error import URLError

BASE_URL = "http://localhost:1234"

def test_health():
    """Test health check endpoint"""
    print("\n1️⃣  Testing Health Endpoint...")
    try:
        req = Request(f"{BASE_URL}/health", method="GET")
        with urlopen(req) as response:
            data = json.loads(response.read().decode())
            print(f"   ✅ Status: {data['status']}")
            return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_chat():
    """Test chat endpoint with session"""
    print("\n2️⃣  Testing Chat Endpoint...")
    try:
        payload = {
            "content": "Hello, what can you help me with?",
            "session_id": "test-session-001"
        }
        
        req = Request(
            f"{BASE_URL}/api/chat",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        with urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            print(f"   ✅ Message: {data['message'][:100]}...")
            print(f"   ✅ Session ID: {data['session_id']}")
            print(f"   ✅ From Cache: {data['from_cache']}")
            return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_session_stats():
    """Test session statistics endpoint"""
    print("\n3️⃣  Testing Session Stats Endpoint...")
    try:
        req = Request(f"{BASE_URL}/api/sessions/stats", method="GET")
        with urlopen(req) as response:
            data = json.loads(response.read().decode())
            print(f"   ✅ Active Sessions: {data['active_sessions']}")
            return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_memory_stats():
    """Test memory statistics for a session"""
    print("\n4️⃣  Testing Memory Stats Endpoint...")
    try:
        req = Request(f"{BASE_URL}/api/sessions/test-session-001/memory-stats", method="GET")
        with urlopen(req) as response:
            data = json.loads(response.read().decode())
            print(f"   ✅ Message Count: {data['message_count']}")
            print(f"   ✅ Buffer Length: {data['buffer_length']}")
            print(f"   ✅ Summary: {data['summary'][:100]}...")
            return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_cache_stats():
    """Test cache statistics endpoint"""
    print("\n5️⃣  Testing Cache Stats Endpoint...")
    try:
        req = Request(f"{BASE_URL}/api/cache-stats", method="GET")
        with urlopen(req) as response:
            data = json.loads(response.read().decode())
            print(f"   ✅ Cache stats retrieved")
            print(f"   ✅ Keys: {list(data.keys())[:3]}")
            return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Conversation Memory API Test Suite")
    print("=" * 60)
    
    results = []
    results.append(("Health Check", test_health()))
    
    if results[0][1]:  # If health check passed
        time.sleep(0.5)
        results.append(("Chat Endpoint", test_chat()))
        time.sleep(0.5)
        results.append(("Session Stats", test_session_stats()))
        time.sleep(0.5)
        results.append(("Memory Stats", test_memory_stats()))
        time.sleep(0.5)
        results.append(("Cache Stats", test_cache_stats()))
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<40} {status}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 60)
    
    sys.exit(0 if passed == total else 1)
