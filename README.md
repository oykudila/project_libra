## Setup for testing

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
A focused AI planning assistant that:

- Takes a high-level goal
- Generates a structured, action based plan
- Allows users to revise and refine that plan

Users can also view and manage existing projects in the same space for continuity across planning sessions.

---

## Features (Current MVP)

- AI plan generation from goal input
- AI plan revision based on user feedback
- Local data persistence
- Caching of AI responses to reduce redundant calls
- Responsive UI for desktop and mobile

---

**UX and AI interaction**

- Interacting with the AI is structured, there is no AI chat distraction
- Prompts are predefined and guuided, reducing the effort to phrase prompts
- Output is action steps, not long texts of advice
- Loading states are explicit

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

- **Frontend** handles all user interaction and AI state (loading, revisions, task updates).
- **Backend** handles API routes for generating and revising plans, AI calls, persistance, and caching.

**Intentional tradeoffs**

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

```

```
