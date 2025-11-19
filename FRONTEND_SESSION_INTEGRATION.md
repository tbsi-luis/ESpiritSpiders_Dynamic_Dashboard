# Frontend Integration Guide - Conversation Memory

## Quick Start

### 1. Update Your API Client

Modify `frontend/src/services/apiClient.ts` to handle sessions:

```typescript
import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = 'http://localhost:1234';
const SESSION_STORAGE_KEY = 'chatSessionId';

class APIClient {
  private instance: AxiosInstance;
  private sessionId: string;

  constructor() {
    this.instance = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    // Retrieve or create session ID
    this.sessionId = this.getOrCreateSessionId();
  }

  private getOrCreateSessionId(): string {
    let sessionId = sessionStorage.getItem(SESSION_STORAGE_KEY);
    if (!sessionId) {
      sessionId = this.generateUUID();
      sessionStorage.setItem(SESSION_STORAGE_KEY, sessionId);
    }
    return sessionId;
  }

  private generateUUID(): string {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      const r = (Math.random() * 16) | 0;
      const v = c === 'x' ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  }

  async sendMessage(content: string) {
    return this.instance.post('/api/chat', {
      content,
      session_id: this.sessionId,
    });
  }

  async getSessionStats() {
    return this.instance.get(`/api/sessions/${this.sessionId}/memory-stats`);
  }

  async clearSessionHistory() {
    return this.instance.delete(`/api/sessions/${this.sessionId}/history`);
  }

  getSessionId(): string {
    return this.sessionId;
  }

  resetSession(): void {
    sessionStorage.removeItem(SESSION_STORAGE_KEY);
    this.sessionId = this.getOrCreateSessionId();
  }
}

export default new APIClient();
```

### 2. Update Your Chat Component

Example for `frontend/src/components/ChatbotBoard.tsx`:

```typescript
import React, { useState, useEffect } from 'react';
import apiClient from '../services/apiClient';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export const ChatbotBoard: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState('');

  useEffect(() => {
    // Get session ID on mount
    setSessionId(apiClient.getSessionId());
  }, []);

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    // Add user message to UI
    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await apiClient.sendMessage(input);
      
      // Add bot response to UI
      const botMessage: Message = {
        role: 'assistant',
        content: response.data.message,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, botMessage]);

      // Render HTML content if available
      if (response.data.html) {
        // Render response.data.html in your dashboard
        console.log('HTML Content:', response.data.html);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, there was an error processing your message.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleClearHistory = async () => {
    if (window.confirm('Clear conversation history?')) {
      try {
        await apiClient.clearSessionHistory();
        setMessages([]);
        console.log('Conversation history cleared');
      } catch (error) {
        console.error('Error clearing history:', error);
      }
    }
  };

  const handleNewSession = () => {
    apiClient.resetSession();
    setSessionId(apiClient.getSessionId());
    setMessages([]);
  };

  return (
    <div className="chatbot-board">
      <div className="chat-header">
        <h2>Chat Assistant</h2>
        <div className="session-info">
          <small>Session: {sessionId.substring(0, 8)}...</small>
        </div>
        <div className="chat-actions">
          <button onClick={handleClearHistory} disabled={messages.length === 0}>
            Clear History
          </button>
          <button onClick={handleNewSession}>New Session</button>
        </div>
      </div>

      <div className="messages-container">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <strong>{msg.role === 'user' ? 'You' : 'Assistant'}:</strong>
            <p>{msg.content}</p>
            <small>{msg.timestamp.toLocaleTimeString()}</small>
          </div>
        ))}
        {loading && <div className="message loading">Processing...</div>}
      </div>

      <div className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          placeholder="Type your message..."
          disabled={loading}
        />
        <button onClick={handleSendMessage} disabled={loading || !input.trim()}>
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatbotBoard;
```

### 3. Styling (CSS)

Add to `frontend/src/App.css`:

```css
.chatbot-board {
  display: flex;
  flex-direction: column;
  height: 100%;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
}

.chat-header {
  background: #f5f5f5;
  padding: 16px;
  border-bottom: 1px solid #ddd;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-header h2 {
  margin: 0;
  flex: 1;
}

.session-info {
  margin: 0 16px;
  color: #666;
}

.chat-actions {
  display: flex;
  gap: 8px;
}

.chat-actions button {
  padding: 8px 12px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.chat-actions button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #fafafa;
}

.message {
  margin-bottom: 12px;
  padding: 12px;
  border-radius: 4px;
  background: white;
  border-left: 4px solid #007bff;
}

.message.user {
  background: #e3f2fd;
  border-left-color: #1976d2;
  margin-left: 20%;
}

.message.assistant {
  background: white;
  border-left-color: #4caf50;
  margin-right: 20%;
}

.message strong {
  display: block;
  color: #333;
  margin-bottom: 4px;
}

.message p {
  margin: 0;
  color: #666;
  line-height: 1.4;
}

.message small {
  display: block;
  color: #999;
  font-size: 11px;
  margin-top: 4px;
}

.message.loading {
  font-style: italic;
  color: #999;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.input-area {
  display: flex;
  padding: 16px;
  gap: 8px;
  border-top: 1px solid #ddd;
  background: #f5f5f5;
}

.input-area input {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  font-family: inherit;
}

.input-area input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.1);
}

.input-area button {
  padding: 10px 20px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

.input-area button:hover:not(:disabled) {
  background: #0056b3;
}

.input-area button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

## Key Features

✅ **Automatic Session Management** - Session ID persisted in sessionStorage
✅ **Message History** - Maintains local message history UI
✅ **Clear History** - Clear server-side memory
✅ **New Session** - Start fresh conversation
✅ **Status Indicators** - Shows session ID and loading state
✅ **Responsive Design** - Works on all screen sizes

## API Response Format

The backend returns:
```json
{
  "message": "Response text",
  "html": "<div>...</div>",
  "from_cache": false,
  "session_id": "abc-123-def"
}
```

## Session Management

- **Session ID**: Unique identifier for each conversation thread
- **Storage**: `sessionStorage` (cleared on browser tab close)
- **Options**:
  - Use `localStorage` for persistent sessions across browser restarts
  - Use `sessionStorage` for session-specific chats (recommended)

## Testing in Browser Console

```javascript
// Get session ID
sessionStorage.getItem('chatSessionId')

// Manually send message
fetch('http://localhost:1234/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    content: 'Hello',
    session_id: sessionStorage.getItem('chatSessionId')
  })
}).then(r => r.json()).then(console.log)

// Get memory stats
fetch(`http://localhost:1234/api/sessions/${sessionStorage.getItem('chatSessionId')}/memory-stats`)
  .then(r => r.json()).then(console.log)
```

## Notes

- Frontend maintains its own message history UI (separate from backend memory)
- Backend memory ensures context even if frontend refreshes
- Session ID can be manually set for testing specific conversations
- Each browser tab can have different session IDs
