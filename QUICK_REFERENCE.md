# Quick Reference Card - Conversation Memory

## 📋 What Changed?

| Component | What's New |
|-----------|-----------|
| **Models** | `session_id` field added to `ChatMessage` |
| **Memory** | NEW `memory.py` file for session management |
| **Services** | `session_id` parameter added to functions |
| **API** | 4 new endpoints for session management |

---

## 🔗 API Quick Reference

### Chat Endpoint
```bash
POST /api/chat
Content-Type: application/json

{
  "content": "Your message here",
  "session_id": "optional-uuid"
}

Response:
{
  "message": "Response text",
  "html": "<div>...</div>",
  "from_cache": false,
  "session_id": "abc-123-def"
}
```

### Session Management
```bash
# Get session statistics
GET /api/sessions/stats

# Get specific session memory stats
GET /api/sessions/{session_id}/memory-stats

# Clear specific session
DELETE /api/sessions/{session_id}/history

# Clear all sessions
DELETE /api/sessions/history/all
```

---

## 🐍 Python Code Changes

### Old Way (Lost Context)
```python
# Every request independent
bot_response = await analyze_user_intent(user_message)
```

### New Way (Preserves Context)
```python
# Full session context
bot_response = await analyze_user_intent(user_message, session_id)
```

---

## 💻 Frontend Integration

### Store Session ID
```typescript
const sessionId = sessionStorage.getItem('sessionId') || generateUUID();
sessionStorage.setItem('sessionId', sessionId);
```

### Send Message with Session
```typescript
const response = await fetch('/api/chat', {
  method: 'POST',
  body: JSON.stringify({
    content: userInput,
    session_id: sessionId
  })
});
```

---

## 📊 Data Flow

```
Request with session_id
    ↓
Memory Manager retrieves history
    ↓
History + new message sent to OpenAI
    ↓
OpenAI has full context
    ↓
Response stored in memory
    ↓
Next request has more context
```

---

## 🧠 Memory Features

| Feature | How It Works |
|---------|-------------|
| **Auto Memory** | Created automatically on first message |
| **History** | Last 10 messages kept for context |
| **Summarization** | Old messages auto-compressed by LangChain |
| **Per-Session** | Each session has isolated memory |
| **Cleanup** | Manual cleanup via endpoints |

---

## ⚡ Common Tasks

### Check if memory working
```bash
# See how many messages are stored
curl http://localhost:1234/api/sessions/abc-123/memory-stats

# Response includes message count and summary
{
  "message_count": 5,
  "buffer_length": 1234,
  "summary": "User asked about..."
}
```

### Clear conversation
```bash
# Backend-side
DELETE /api/sessions/abc-123/history

# Frontend-side
sessionStorage.removeItem('sessionId')
```

### New conversation
```typescript
// Clear and reset
sessionStorage.removeItem('sessionId');
const newSessionId = generateUUID();
sessionStorage.setItem('sessionId', newSessionId);
```

---

## ⚠️ Important Notes

1. **Session ID**
   - Auto-generated if not provided
   - Should be persistent per conversation
   - Use `sessionStorage` or `localStorage`

2. **Memory Size**
   - Last 10 messages included per request
   - Older messages auto-summarized
   - Prevents token overflow

3. **Persistence**
   - In-memory storage (lost on restart)
   - For production: migrate to PostgreSQL

4. **Costs**
   - Longer history = higher OpenAI API costs
   - Trade-off: Better responses vs lower cost

---

## 🧪 Testing Checklist

- [ ] First message sends successfully
- [ ] Response contains session_id
- [ ] Second message references first message
- [ ] Memory stats show correct count
- [ ] Can clear specific session
- [ ] New session doesn't share history
- [ ] Frontend session ID persists

---

## 📁 Files Overview

| File | Purpose |
|------|---------|
| `models.py` | Data models with session support |
| `memory.py` | Session memory management |
| `services.py` | Business logic with context |
| `main.py` | API endpoints |
| `CONVERSATION_MEMORY_SETUP.md` | Full setup guide |
| `FRONTEND_SESSION_INTEGRATION.md` | Frontend instructions |
| `BEFORE_AFTER_COMPARISON.md` | Detailed changes |

---

## 🚀 Getting Started

1. **Backend Ready**: ✅ All changes complete
2. **Test**: Run provided curl commands
3. **Frontend**: Update API client to send `session_id`
4. **Verify**: Check context preservation in multi-turn conversation

---

## 🔍 Debugging Tips

**Memory not persisting?**
- Check session_id is same in requests
- Verify backend is running
- Check logs for errors

**OpenAI still losing context?**
- Confirm session_id is being sent
- Check `/api/sessions/{id}/memory-stats`
- Look for database query keywords

**High API costs?**
- The 10-message limit reduces this
- Consider conversation pruning
- Monitor with memory-stats endpoint

---

## 📞 Quick Links

- Setup: See `CONVERSATION_MEMORY_SETUP.md`
- Frontend: See `FRONTEND_SESSION_INTEGRATION.md`
- Changes: See `BEFORE_AFTER_COMPARISON.md`
- Summary: See `IMPLEMENTATION_SUMMARY.md`

---

**Status**: ✅ Ready to Use
**Testing Recommended**: Yes
**Backward Compatible**: Yes (session_id is optional)
