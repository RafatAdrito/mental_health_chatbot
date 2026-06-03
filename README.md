# MindfulChat - AI Mental Health Support Platform

MindfulChat is a full-stack mental health companion that combines an empathetic AI chat experience with safety-first crisis detection, mood tracking, persistent conversation history, and location-aware support resources for Bangladesh.

This project was built as more than a chatbot. It demonstrates product thinking, backend workflow orchestration, real-time streaming UX, secure authentication, user-specific memory, and guardrails for a sensitive mental health domain.

> Important: MindfulChat is a supportive wellness application, not a replacement for licensed therapy, medical diagnosis, medication guidance, or emergency care.

## What I Built

- Full-stack authenticated AI chat application with React, FastAPI, PostgreSQL, LangGraph, and Gemini.
- Real-time streaming assistant responses through WebSockets, with REST fallback when sockets are unavailable.
- Persistent multi-session conversation history with a sidebar for resume, switch, create, and delete flows.
- Safety workflow that detects crisis language, scores risk, and routes high-risk conversations to crisis resources.
- Mood check-in system that periodically asks users how they feel and stores mood entries over time.
- Support resource module with crisis helplines and nearby hospitals, therapists, or clinics using geolocation.
- Backend test coverage for auth, safety sanitization, crisis detection, graph structure, and coping tools.

## Logic Highlights

### 1. Safety-First Conversation Routing

Every user message passes through a LangGraph workflow before the assistant responds:

```text
User Message
  -> Intake
  -> Crisis Detector
  -> Crisis Responder, if high/critical risk
  -> Mood Check-in, if due
  -> Empathetic Conversation
  -> Tool Executor, if the AI requests support tools
  -> Final Assistant Response
```

The backend does not send every message directly to the LLM. It first applies domain-specific logic:

- Tracks conversation turn count.
- Runs crisis keyword scanning for suicidal ideation, self-harm, abuse, overdose, and severe distress.
- Uses Gemini as an additional risk assessor when keyword risk appears or on periodic turns.
- Combines keyword score, LLM score, and prior risk context into `none`, `low`, `medium`, `high`, or `critical`.
- Immediately bypasses normal chat when risk is `high` or `critical`.

### 2. Crisis Escalation Logic

When a high-risk message is detected, MindfulChat responds with crisis-oriented support instead of general AI conversation.

The system:

- Shows Bangladesh-relevant crisis resources such as NIMH and psychiatric emergency contacts.
- Displays an in-app crisis alert panel in the frontend.
- Encourages immediate emergency help when the user may be in danger.
- Avoids pretending the AI can solve emergency situations alone.

### 3. Medical Safety Guardrails

Because mental health is a high-risk domain, assistant output is sanitized before reaching the user.

The safety layer blocks or rewrites unsafe patterns such as:

- Direct diagnosis claims like "you have depression".
- Medication recommendations like "you should take Prozac".
- Language implying the AI is diagnosing the user.

This keeps the assistant supportive while directing users toward qualified healthcare professionals when clinical judgment is needed.

### 4. Mood Tracking and Check-ins

MindfulChat includes both AI-driven check-ins and user-submitted mood logs.

Backend logic:

- Triggers a mood check-in on the first turn.
- Repeats mood check-ins every 5 turns.
- Stores mood score, label, notes, session ID, and timestamp.
- Provides historical mood retrieval with configurable day range and limits.

Frontend logic:

- Presents a focused mood modal with a 1-10 mood score.
- Offers labels such as anxious, depressed, stressed, overwhelmed, calm, and happy.
- Saves optional user notes for future review.

### 5. Durable Conversation Memory

The app separates two kinds of memory:

- Database memory: users, sessions, messages, and mood entries are stored in PostgreSQL.
- LangGraph checkpoint memory: conversation state is checkpointed per `thread_id`, allowing the agent graph to preserve state across turns.

User-specific context is also generated from stored preferences, such as preferred name, helpful coping strategies, previous topics, and communication style. This context is injected into the system prompt so responses can become more personalized over time.

### 6. Location-Aware Support Resources

Users can share their location to find nearby mental health support.

Resource logic:

- Validates coordinates against Bangladesh's bounding box.
- Searches OpenStreetMap through the Overpass API.
- Supports `hospital`, `therapist`, and `clinic` categories.
- Falls back to curated sample resources when live search is unavailable.
- Returns names, addresses, phone numbers, and map links.

### 7. Secure Multi-User Auth and Session Ownership

The backend uses JWT authentication and validates ownership before exposing private chat history.

Auth logic includes:

- Signup with username, email, password, and optional display name.
- Duplicate username and email protection.
- Password hashing with bcrypt plus SHA-256 prehashing to avoid bcrypt's 72-byte input limit.
- JWT access tokens with expiration.
- Protected `/me`, chat, mood, and session routes.
- Session ownership checks so one user cannot read another user's history.

## User Experience

MindfulChat is designed around a calm, focused chat workflow:

1. User signs up or logs in.
2. App creates or resumes the latest conversation session.
3. User sends a message.
4. Assistant streams the response token-by-token.
5. Crisis alerts appear automatically when needed.
6. User can open support resources at any time.
7. User can log mood and keep a private history of emotional state.
8. User can create, resume, or delete conversations from the sidebar.

## Architecture

```text
Frontend - React + Vite + Zustand
  - Auth pages
  - Protected chat route
  - WebSocket streaming
  - Conversation sidebar
  - Mood check-in modal
  - Crisis alert and support resources

Backend - FastAPI + LangGraph
  - JWT auth
  - Async PostgreSQL persistence
  - LangGraph agent workflow
  - Gemini chat model integration
  - Crisis detection service
  - Safety sanitizer
  - Coping and location tools

Database - PostgreSQL
  - users
  - conversation_sessions
  - conversation_messages
  - mood_entries
  - LangGraph checkpoint tables
```

## Tech Stack

| Layer | Technologies |
| --- | --- |
| Frontend | React 19, Vite, Zustand, React Router, Tailwind CSS, Lucide React |
| Backend | FastAPI, Python, LangGraph, LangChain, Gemini, SQLAlchemy Async, Pydantic |
| Database | PostgreSQL, Alembic migrations, LangGraph Postgres checkpointer |
| Realtime | WebSocket streaming with REST fallback |
| Auth | JWT, bcrypt password hashing, FastAPI security dependencies |
| Testing | Pytest, pytest-asyncio, HTTPX ASGI transport |
| External Data | OpenStreetMap Overpass API |


## Frontend Features

- Protected routing based on JWT presence.
- Local token and active session persistence.
- Responsive sidebar for desktop and mobile.
- Token-level streaming display for assistant responses.
- Automatic WebSocket connection per active session.
- REST fallback when WebSocket is unavailable.
- Auth-expired event handling to cleanly log out invalid sessions.
- Floating support resources button available during chat.
- Geolocation permission handling with user-friendly states.

## Backend Features

- App lifespan initializes database tables, LangGraph checkpointer, and compiled agent graph.
- Async SQLAlchemy sessions with commit/rollback handling.
- LangGraph nodes for intake, crisis detection, crisis response, mood check-in, conversation, and tool execution.
- Gemini model integration for empathetic conversation and structured risk assessment.
- Tool calling for coping strategies and nearby help lookup.
- Alembic migrations for auth/session/message schema evolution.
- Ownership validation on private session history.

## Tests

Backend tests cover the most important domain and security behavior:

- Auth signup, login, invalid token, and duplicate account cases.
- Protected chat route behavior.
- Cross-user session history access prevention.
- Crisis keyword scanning and risk scoring.
- Safety sanitizer behavior for diagnosis and medication claims.
- Coping strategy tool responses.
- LangGraph structure and compilation.

Run backend tests:

```bash
cd Backend
pytest
```

## Local Setup

### Backend

Create a backend `.env` file with:

```env
GOOGLE_API_KEY=your_google_api_key
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/mental_health
GEMINI_MODEL_NAME=gemini-1.5-flash
CRISIS_HOTLINE_NUMBER=999
JWT_SECRET=replace_with_a_secure_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

Install and run:

```bash
cd Backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

Create `Frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

Install and run:

```bash
cd Frontend
npm install
npm run dev
```
