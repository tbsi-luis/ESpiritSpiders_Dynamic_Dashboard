# Dynamic Dashboard - Complete Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React + TypeScript)             │
│                   http://localhost:5173                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  DynamicDashboard.tsx                    │   │
│  │              (Main Page - State Manager)                 │   │
│  │                                                           │   │
│  │  - Manages dashboardData state                           │   │
│  │  - Passes data to CanvasDashboard                        │   │
│  │  - Receives callback from ChatbotBoard                   │   │
│  └──────────────────────────────────────────────────────────┘   │
│       ▲                                      ▼                     │
│       │                                      │                     │
│       │ onDashboardGenerated(data)           │ dashboardData       │
│       │                                      │                     │
│  ┌────────────────────┐         ┌───────────────────────────┐   │
│  │  ChatbotBoard.tsx  │         │  CanvasDashboard.tsx      │   │
│  │   (Chat UI)        │         │   (Chart Rendering)       │   │
│  │                    │         │                           │   │
│  │ - User input       │         │ - Renders bar charts      │   │
│  │ - Chat display     │         │ - Renders line charts     │   │
│  │ - API calls        │         │ - Renders pie charts      │   │
│  │ - Emit dashboard   │         │ - Renders area charts     │   │
│  │   data             │         │ - Handles data display    │   │
│  └────────────────────┘         └───────────────────────────┘   │
│       │                                                            │
│       │ apiClient.sendChatMessage(message)                       │
│       │                                                            │
└───────┼────────────────────────────────────────────────────────┘
        │
        │ HTTP POST /api/chat
        │ JSON: { content: "user message" }
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI + Python)                     │
│                   http://localhost:8000                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   main.py (FastAPI)                      │   │
│  │                                                           │   │
│  │  POST /api/chat                GET /api/dashboard/sample │   │
│  └──────────────────────────────────────────────────────────┘   │
│       │                                                            │
│       ▼                                                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              services/services.py                         │   │
│  │                                                           │   │
│  │  - parse_user_intent()                                   │   │
│  │    └─► OpenAI API (gpt-3.5-turbo)                        │   │
│  │    └─► Returns dashboard spec JSON                       │   │
│  │                                                           │   │
│  │  - generate_sample_data()                                │   │
│  │    └─► Creates mock data based on spec                   │   │
│  │                                                           │   │
│  │  - get_bot_response()                                    │   │
│  │    └─► Orchestrates above functions                      │   │
│  └──────────────────────────────────────────────────────────┘   │
│       │                                                            │
│       ▼                                                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │            models/models.py (Pydantic)                   │   │
│  │                                                           │   │
│  │  - ChatMessage                                           │   │
│  │  - DashboardSpec                                         │   │
│  │  - DashboardResponse                                     │   │
│  └──────────────────────────────────────────────────────────┘   │
│       │                                                            │
└───────┼────────────────────────────────────────────────────────┘
        │
        │ HTTP Response
        │ JSON: {
        │   message: "I've created a dashboard for you...",
        │   dashboard_spec: {
        │     title: "Sales Dashboard",
        │     charts: [...],
        │     ...
        │   },
        │   data: {
        │     sales_by_region: [...],
        │     top_products: [...],
        │     ...
        │   }
        │ }
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│                 FRONTEND - Chart Rendering                        │
│                                                                   │
│  CanvasDashboard receives data and renders:                      │
│  - Loops through dashboard_spec.charts                           │
│  - For each chart:                                               │
│    ├─► Gets data from data[chart.dataKey]                        │
│    ├─► Determines chart.type (bar/line/pie/area)                 │
│    └─► Renders using Recharts component                          │
│                                                                   │
│  Result: Interactive, dynamic dashboard displayed!               │
└─────────────────────────────────────────────────────────────────┘
```

## File Structure with Connections

```
DynamicDashboard/
│
├── backend/
│   ├── requirements.txt          # Python dependencies
│   ├── .env                      # OPENAI_API_KEY
│   └── app/
│       ├── main.py               ◄────────────────┐
│       │   ├── @app.post("/api/chat")             │
│       │   └── @app.get("/api/dashboard/sample")  │
│       ├── config.py             ◄────────┐       │
│       │   └── get_settings()         │   │       │
│       │                              │   │       │
│       ├── models/                    │   │       │
│       │   ├── __init__.py ────────────────┐      │
│       │   └── models.py             │   │       │
│       │       ├── ChatMessage       │   │       │
│       │       ├── DashboardSpec     │   │       │
│       │       └── DashboardResponse │   │       │
│       │                              │   │       │
│       └── services/                 │   │       │
│           ├── __init__.py ──────────────┤      │
│           └── services.py           │   │       │
│               ├── parse_user_intent()   │       │
│               ├── generate_sample_data()│       │
│               └── get_bot_response() ────┤      │
│                                         │       │
├── frontend/                            │       │
│   ├── package.json              ◄──────────────┤
│   │   └── dependencies:          │       │     │
│   │       - react@19            │       │     │
│   │       - recharts@3.4        │       │     │
│   │       - tailwindcss@4       │       │     │
│   │       - react-icons@5       │       │     │
│   │                              │       │     │
│   ├── .env                      ◄──────────┐  │
│   │   └── VITE_API_URL           │       │    │
│   │                              │       │    │
│   ├── tsconfig.json             │       │    │
│   ├── vite.config.ts            │       │    │
│   │                              │       │    │
│   └── src/                       │       │    │
│       ├── main.tsx              │       │    │
│       ├── App.tsx               │       │    │
│       │                          │       │    │
│       ├── pages/                 │       │    │
│       │   └── DynamicDashboard.tsx       │    │
│       │       ├── imports ChatbotBoard ──────┐
│       │       ├── imports CanvasDashboard    │
│       │       └── manages state             │
│       │                          │       │    │
│       ├── components/            │       │    │
│       │   ├── index.tsx         │       │    │
│       │   ├── ChatbotBoard.tsx ◄────────────┤
│       │   │   ├── uses apiClient           │
│       │   │   ├── calls sendChatMessage()  │
│       │   │   └── emits dashboard data     │
│       │   │                      │       │    │
│       │   └── CanvasDashboard.tsx◄──────────┤
│       │       ├── receives dashboardData    │
│       │       ├── ChartRenderer component   │
│       │       └── renders Recharts          │
│       │                          │       │    │
│       ├── services/             │       │    │
│       │   └── apiClient.ts ◄──────────────┐
│       │       ├── sendChatMessage()       │
│       │       └── getSampleDashboard()   │
│       │                          │       │  │
│       ├── models/               │       │  │
│       │   └── types.ts ◄────────────────┤
│       │       ├── ChatMessage           │
│       │       ├── DashboardSpec         │
│       │       ├── DashboardChart        │
│       │       └── DashboardResponse     │
│       │                          │       │  │
│       └── assets/               │       │  │
│           └── (images, etc.)    │       │  │
│                                  │       │  │
└── INTEGRATION_GUIDE.md          │       │  │
└── SETUP_VERIFICATION.md         │       │  │
```

## Request-Response Cycle

### 1. User Action
```
User types message in ChatbotBoard
↓
calls handleSend()
```

### 2. API Call
```
ChatbotBoard calls:
apiClient.sendChatMessage("Create a dashboard showing sales")
↓
POST http://localhost:8000/api/chat
Content-Type: application/json
Body: { content: "Create a dashboard showing sales" }
```

### 3. Backend Processing
```
main.py receives POST /api/chat
↓
calls get_bot_response(user_message)
↓
services.py:
- Calls OpenAI API with user message
- OpenAI returns dashboard spec (JSON)
- generate_sample_data() creates mock data
- Returns {spec, data}
↓
Returns DashboardResponse JSON
```

### 4. Frontend Response Handling
```
apiClient receives response
↓
ChatbotBoard's handleSend() callback:
- Displays bot message in chat
- Calls onDashboardGenerated(response)
↓
DynamicDashboard receives callback
↓
Sets dashboardData state
↓
Passes data to CanvasDashboard
↓
CanvasDashboard renders charts
```

## Key Integration Points

### 1. **Type Safety (TypeScript)**
```
apiClient.ts exports DashboardResponse interface
├─ Used in DynamicDashboard.tsx
├─ Used in ChatbotBoard.tsx
└─ Ensures compile-time type checking
```

### 2. **API Client Abstraction**
```
apiClient.ts handles all HTTP calls
├─ Encapsulates API_BASE_URL
├─ Handles headers and serialization
└─ Provides catch-all error handling
```

### 3. **Component Composition**
```
DynamicDashboard (Parent)
├─ ChatbotBoard (Child - Emit)
│  └─ calls onDashboardGenerated callback
└─ CanvasDashboard (Child - Display)
   └─ receives dashboardData prop
```

### 4. **Dynamic Rendering**
```
CanvasDashboard.ChartRenderer
├─ Receives chart type and data
├─ Conditionally renders chart component
└─ Uses Recharts ResponsiveContainer
```

---

This architecture ensures:
✅ Clean separation of concerns
✅ Type-safe communication
✅ Scalable component structure
✅ Easy to test and maintain
✅ Ready for expansion
