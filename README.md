## Running the project locally

### Backend Setup

Fill in and use the `.env.example` as `.env`

```
cd backend
python -m venv venv
source venv/bin/activate or venv\Scripts\activate (W)
pip install -r requirements.txt

uvicorn app.main:app --reload
```

**Swagger Overview**
`http://localhost:8000/docs`

---

### Frontend Setup

```
cd frontend
npm install
npm run dev
```

---

## Core Idea

AI-powered planning tool to help users break down high-level, abstract goals into clear tasks.

This tool focuses on **structured thinking and execution**, the environment is minimal, built for a specific purpose without distractions and comes with filters. Users do not have to spend their time planning, they can get to doing. I used **Svelte** and **FastAPI** to familiarize myself with the Libra tech stack while building this MVP :)

**User Problem**

Many people struggle to put vague and abstract goals into concrete next steps. This tool guides you to break up those big goals and lays down a plan crafted for your needs.

**Solution**

An AI planning assistant with a simple purpose:

- Take a high-level goal
- Generate a structured, action based plan
- Allows users to revise and refine that plan

Users can also view and manage existing projects in the same space for continuity across planning sessions.

---

## MVP

**Features**

- AI plan generation from goal input
- AI plan revision based on user feedback
- (Local) Data persistence
- Caching of AI responses to reduce redundant calls
- Responsive UI for desktop and mobile

---

**UX and AI interaction**

- Interacting with the AI is structured, there is no AI chat distraction
- Instructions are predefined and guided, reducing the effort to phrase prompts
- Output is actionable steps, not long texts of advice
- Loading states are explicit

---

**AI Design**

- The AI responses are not free-form advice.
- Responses are constrained to a structured format to create tasks.
- Prompts are predefined and contextual.
- Plan revision reuses existing context instead of regenerating from scratch.

---

## Tech Stack

### Frontend

- Svelte
- TypeScript
- Tailwind CSS
- shadcn/ui

### Backend

- Python
- FastAPI
- OpenAI API integration
- SQLite (local)

---

## Architecture Overview

**Flow**

1. User submits a high-level goal via the frontend.
2. Frontend calls the FastAPI backend.
3. Backend constructs a structured AI prompt and calls the OpenAI API.
4. The generated plan is validated, cached, and persisted locally.
5. Frontend renders tasks and allows user-driven revisions.

- **Frontend** handles all user interaction and AI state (loading, revisions, task updates).

- **Backend** handles API routes for generating and revising plans, AI calls, persistance, and caching.

**Tradeoffs**

- **Local persistence only**
  Data is stored locally.

- **Focused scope**
  The tool prioritizes actionable planning, there is no scheduling, reminders, or execution tracking.

- **Reduced AI complexity**
  Simple models and prompts instead of complex multi-agent systems.

- **Cache management**
  AI responses are cached locally to improve performance, but cache eviction and cleanup are not yet implemented and would be required

---

## V2 Plans

- Clicking a task opens a dedicated board with subtasks
- In-project AI discussion chat for refining plans
- Progress tracking and task completion analytics
- AI-driven plan revisions based on completed tasks

---

## Way Ahead Ideas

- Calendar integration
- Personalization
- Notifications and reminders
