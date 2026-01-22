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

## Development Diary

I started by defining a determenistic response structure for the AI output before spending time and tokens on the prompt. I defined the Pydanctic schemas first, then shaped the AI prompt to stay within these defined types with its responses.

Next, I implemented the backend routes for generating new plans, revising existing plans with user feedback, and locally persisting projects. During testing, I noticed that the revisions were quite slow because of seperate calls, so I implemented two local caches to avoid redundant AI calls. One cache is for revisions and the other is for detecting and reusing plans for projects that have very similar high-level goals.

Once the backend was up and running as intended, I started on the frontend. I used shadcn/ui components to gain speed on the UI development and to keep a consistent design across pages.I prioritised making the loading and generation states clear, and ensure a flow of `create plan -> revise plan -> save plan as project`.

---

## Core Idea

AI-powered planning tool that helps users break down high-level, abstract goals into clear tasks. The aim is for users to spend less time on planning and more time on doing.

This tool focuses on **structured thinking and execution**, the environment is minimal, built for a specific purpose without distractions. Instead of thinking about how to prompt the AI, users can get right into reviewing and acting on structured plans. I used **Svelte** and **FastAPI** to familiarize myself with the Libra tech stack while building this MVP :)

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

**UI/UX**

- Interacting with the AI is structured rather than conversational
- Prompts are predefined and guided to reduce user effort
- AI output is actionable steps instead of long texts of advice
- Loading and revision states are explicit

---

**More on the AI**

The AI responses are intentionally constrained to avoid acting as a general purpose model. The prompt ensures that we only get consistent JSON responses of actionable tasks that fit in predefined schemas and are easy to render in the UI.

\*_Prompt_

- Creates exactly 3 milestones for the high-level structure (read V2 Plans)
- Fixed number of tasks to not overwhelm the user or crowd up the project boards
- Task titles that always start with verbs
- Short instructions as descriptions
- Index ordering and milestone grouping
- Adjust plan according to user's experience level

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

1. User submits a high-level goal via the frontend
2. Frontend calls the FastAPI backend
3. Backend constructs a structured AI prompt and calls the OpenAI API
4. The generated plan is validated, cached, and persisted locally
5. Frontend renders tasks and allows user-driven revisions

- **Frontend** handles all user interaction and AI state (loading, revisions, task updates)

- **Backend** handles API routes for generating and revising plans, AI calls, persistance, and caching

**Tradeoffs**

- Local persistence only: data is stored locally

- Focused scope: the tool prioritizes actionable planning, there is no scheduling, reminders, or tracking

- Reduced AI complexity: simple models and prompts instead of complex multi-agent systems

- Cache management: AI responses are cached locally to improve performance, but cache eviction and automatic cleanup would be required for environments with bigger loads

---

## V2 Plans

- Milestones act as general guides on a project
- Clicking a task opens a dedicated board with subtasks
- In-project AI discussion chat for refining plans
- Progress tracking and task completion analytics
- AI-driven plan revisions based on completed tasks

---

## Way Ahead Ideas

- Calendar integration
- Personalization
- Notifications and reminders
