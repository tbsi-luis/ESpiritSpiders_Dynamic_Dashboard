# Testing Guide - Conversation Memory API

## Prerequisites

- Backend running: `python -m uvicorn app.main:app --reload --port 1234`
- Terminal with curl or similar HTTP client

## Quick Test Commands

### 1. Health Check (Always Start Here)

```bash
curl http://localhost:1234/health
```

**Expected Response:**
```json
{"status":"ok"}
```

---

### 2. Send First Message

```bash
curl -X POST http://localhost:1234/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "content": "What is the capital of France?",
    "session_id": "user-session-001"
  }'
```

**Expected Response:**
```json
{
  "message": "The capital of France is Paris...",
  "html": "<p>The capital of France is Paris...</p>",
  "from_cache": false,
  "session_id": "user-session-001"
}
```

**Key Points:**
- `from_cache`: false (first request, not in cache)
- `session_id`: Returned so you can track it
- `message` and `html`: The bot's response

---

### 3. Send Follow-up Message (Context Test) ⭐

```bash
curl -X POST http://localhost:1234/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "content": "What is its population?",
    "session_id": "user-session-001"
  }'
```

**Expected Response:**
```json
{
  "message": "The population of Paris is approximately...",
  "html": "<p>The population of Paris is approximately...</p>",
  "from_cache": false,
  "session_id": "user-session-001"
}
```

**Proof of Context:**
- Bot understood "its" = Paris (from previous message)
- Bot maintains conversation state
- No need to repeat "What is the population of Paris"

---

### 4. New Session (No Context)

```bash
curl -X POST http://localhost:1234/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "content": "What is its population?",
    "session_id": "user-session-002"
  }'
```

**Expected Response:**
```json
{
  "message": "I don't have context about what 'it' refers to...",
  "html": "...",
  "from_cache": false,
  "session_id": "user-session-002"
}
```

**This Proves:**
- Different session IDs have separate memory
- Without context, bot asks for clarification
- Sessions are properly isolated

---

### 5. Check Session Statistics

```bash
curl http://localhost:1234/api/sessions/stats
```

**Expected Response:**
```json
{
  "active_sessions": 2,
  "description": "Number of active conversation sessions with memory"
}
```

---

### 6. Check Session Memory Details

```bash
curl http://localhost:1234/api/sessions/user-session-001/memory-stats
```

**Expected Response:**
```json
{
  "session_id": "user-session-001",
  "message_count": 2,
  "buffer_length": 245,
  "summary": "USER: What is the capital of France?\nASSISTANT: The capital of France is..."
}
```

**What This Shows:**
- `message_count`: 2 (user's two messages + bot's responses)
- `buffer_length`: Total characters in conversation
- `summary`: First 200 chars of conversation history

---

### 7. Clear Session History

```bash
curl -X DELETE http://localhost:1234/api/sessions/user-session-001/history
```

**Expected Response:**
```json
{
  "message": "Conversation history cleared for session user-session-001"
}
```

**Verify Cleared:**
```bash
curl http://localhost:1234/api/sessions/user-session-001/memory-stats
```

Response will show:
```json
{
  "session_id": "user-session-001",
  "message_count": 0,
  "buffer_length": 0,
  "summary": ""
}
```

---

### 8. Clear All Sessions

```bash
curl -X DELETE http://localhost:1234/api/sessions/history/all
```

**Expected Response:**
```json
{
  "message": "All conversation histories cleared"
}
```

**Verify:**
```bash
curl http://localhost:1234/api/sessions/stats
```

Should now show:
```json
{
  "active_sessions": 0,
  "description": "Number of active conversation sessions with memory"
}
```

---

### 9. Cache Statistics

```bash
curl http://localhost:1234/api/cache-stats
```

**Expected Response:**
```json
{
  "total_cached": 2,
  "cache_size_kb": 15.2,
  "most_common_queries": ["What is...", "What about..."],
  ...
}
```

---

## Test Script (Full Workflow)

Save this as `test_workflow.sh`:

```bash
#!/bin/bash

SESSION_ID="test-$(date +%s)"
BASE_URL="http://localhost:1234"

echo "=== Testing Conversation Memory API ==="
echo "Session ID: $SESSION_ID"
echo ""

# Test 1: Health
echo "1. Testing health endpoint..."
curl -s $BASE_URL/health | jq .
echo ""

# Test 2: First message
echo "2. Sending first message..."
RESPONSE=$(curl -s -X POST $BASE_URL/api/chat \
  -H "Content-Type: application/json" \
  -d "{\"content\": \"Hello! What's your name?\", \"session_id\": \"$SESSION_ID\"}")
echo "$RESPONSE" | jq .
echo ""

# Test 3: Follow-up message (WITH context)
echo "3. Sending follow-up message (should have context)..."
RESPONSE=$(curl -s -X POST $BASE_URL/api/chat \
  -H "Content-Type: application/json" \
  -d "{\"content\": \"Can you tell me more about yourself?\", \"session_id\": \"$SESSION_ID\"}")
echo "$RESPONSE" | jq .
echo ""

# Test 4: Check memory
echo "4. Checking session memory stats..."
curl -s $BASE_URL/api/sessions/$SESSION_ID/memory-stats | jq .
echo ""

# Test 5: Statistics
echo "5. Checking active sessions..."
curl -s $BASE_URL/api/sessions/stats | jq .
echo ""

echo "=== Tests Complete ==="
```

Run with:
```bash
chmod +x test_workflow.sh
./test_workflow.sh
```

---

## PowerShell Version

Save as `test_workflow.ps1`:

```powershell
$SESSION_ID = "test-$(Get-Date -Format 'yyyyMMddHHmmss')"
$BASE_URL = "http://localhost:1234"

Write-Host "=== Testing Conversation Memory API ===" -ForegroundColor Green
Write-Host "Session ID: $SESSION_ID"
Write-Host ""

# Test 1: Health
Write-Host "1. Testing health endpoint..." -ForegroundColor Yellow
Invoke-RestMethod -Uri "$BASE_URL/health" -Method Get | ConvertTo-Json | Write-Host

# Test 2: First message
Write-Host "2. Sending first message..." -ForegroundColor Yellow
$payload = @{
    content = "Hello! What's your name?"
    session_id = $SESSION_ID
} | ConvertTo-Json

Invoke-RestMethod -Uri "$BASE_URL/api/chat" -Method Post -Body $payload -ContentType "application/json" | ConvertTo-Json | Write-Host

# Test 3: Follow-up
Write-Host "3. Sending follow-up message (should have context)..." -ForegroundColor Yellow
$payload = @{
    content = "Can you tell me more about yourself?"
    session_id = $SESSION_ID
} | ConvertTo-Json

Invoke-RestMethod -Uri "$BASE_URL/api/chat" -Method Post -Body $payload -ContentType "application/json" | ConvertTo-Json | Write-Host

# Test 4: Check memory
Write-Host "4. Checking session memory stats..." -ForegroundColor Yellow
Invoke-RestMethod -Uri "$BASE_URL/api/sessions/$SESSION_ID/memory-stats" -Method Get | ConvertTo-Json | Write-Host

Write-Host "=== Tests Complete ===" -ForegroundColor Green
```

---

## Expected Behavior Summary

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Health check | Status: ok |
| 2 | First message | Response + message_count increases |
| 3 | Follow-up message | Bot understands context ("What is its population?") |
| 4 | Check memory | Shows 2 messages in buffer |
| 5 | New session message | Bot doesn't have context ("its" = unclear) |
| 6 | Check new session | Separate memory from first session |

---

## Troubleshooting

**Q: "Connection refused" error**
- A: Make sure backend is running: `python -m uvicorn app.main:app --reload --port 1234`

**Q: Empty response**
- A: Check that OpenAI API key is set in `.env` file

**Q: "Message count not increasing"**
- A: Messages are stored in memory but may not increment on cached responses
- Check `from_cache` flag in response

**Q: Session memory cleared unexpectedly**
- A: Backend restart clears all in-memory sessions
- Use database persistence for production

---

## Next: Frontend Integration

Once API tests pass, update your frontend:

```typescript
// Send message with session
const response = await fetch('/api/chat', {
  method: 'POST',
  body: JSON.stringify({
    content: userInput,
    session_id: sessionId  // ← Key for conversation tracking
  })
});

const data = await response.json();
console.log(data.message);  // Bot's response
console.log(data.session_id); // Track this session
```

---

**Happy Testing!** 🎉
