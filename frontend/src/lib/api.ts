const BASE_URL = "http://localhost:8000";

// --- Errors ---
type ApiErrorBody = { detail?: string };
export class ApiError extends Error {
  status: number;
  detail?: string;

  constructor(status: number, message: string, detail?: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

// -----------------------------
export type TaskStatus = "todo" | "in_progress" | "done";
export type TaskSize = "S" | "M" | "L";

// --- API Responses ---
export type ProjectResponse = {
  id: number;
  title: string;
  goal_text: string;
  deadline?: string | null;
  hours_per_week?: number | null;
};

export type MilestoneResponse = {
  id: number;
  title: string;
  description?: string | null;
  order_index: number;
};

export type TaskResponse = {
  id: number;
  title: string;
  description?: string | null;
  status: TaskStatus;
  due_date?: string | null;
  estimate?: TaskSize | null;
  order_index: number;
  milestone_id?: number | null;
};

export type ProjectDetailResponse = ProjectResponse & {
  milestones: MilestoneResponse[];
  tasks: TaskResponse[];
};

// --- Requests ---
export type ProjectCreateRequest = {
  title: string;
  goal_text: string;
  deadline?: string | null;
  hours_per_week?: number | null;
};

export type TaskUpdateRequest = {
  title?: string | null;
  description?: string | null;
  status?: TaskStatus | null;
  due_date?: string | null;
  estimate?: TaskSize | null;
  order_index?: number | null;
  milestone_id?: number | null;
};

export type TaskCreateRequest = {
  project_id: number;
  title: string;
  description?: string | null;
  status: TaskStatus;
  due_date?: string | null;
  estimate?: TaskSize | null;
  order_index?: number | null;
  milestone_id?: number | null;
};

// -----------------------------
export type PlanGenerateInput = {
  goal_text: string;
  deadline?: string | null;
  hours_per_week?: number | null;
  experience_level?: "beginner" | "intermediate" | "advanced";
  detail_level?: "simple" | "detailed";
  constraints?: string | null;
};

export type ProposeMilestone = {
  title: string;
  description?: string | null;
  order_index: number;
};

export type ProposeTask = {
  title: string;
  description?: string | null;
  milestone_index?: number | null;
  status: TaskStatus;
  due_date?: string | null;
  estimate?: TaskSize | null;
  order_index: number;
};

export type PlanResponse = {
  type: "plan";
  milestones: ProposeMilestone[];
  tasks: ProposeTask[];
};

export type GeneratePlanResponse = PlanResponse;

export type RevisePlanInput = {
  goal_text: string;
  deadline?: string | null;
  hours_per_week?: number | null;
  experience_level?: "beginner" | "intermediate" | "advanced";
  detail_level?: "simple" | "detailed" | null;
  constraints?: string | null;
  current_plan: GeneratePlanResponse;
  adjustment: string;
};

export type PlanApplyInput = {
  milestones: ProposeMilestone[];
  tasks: ProposeTask[];
};

// -----------------------------
type RequestOptions = RequestInit & { signal?: AbortSignal };

async function request<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...(options.headers ?? {}),
    },
  });

  if (!res.ok) {
    let detail: string | undefined;
    try {
      const data = (await res.json()) as ApiErrorBody;
      detail = data?.detail;
    } catch {
      // ignore JSON parse errors
    }
    const message = detail
      ? `API error ${res.status}: ${detail}`
      : `API error ${res.status}`;
    throw new ApiError(res.status, message, detail);
  }

  if (res.status === 204) return undefined as T;

  return (await res.json()) as T;
}

// --- Projects ---
export function listProjects(signal?: AbortSignal) {
  return request<ProjectResponse[]>("/projects", { signal });
}

export function createProject(
  payload: ProjectCreateRequest,
  signal?: AbortSignal,
) {
  return request<ProjectResponse>("/projects", {
    method: "POST",
    body: JSON.stringify(payload),
    signal,
  });
}

export function getProject(projectId: number, signal?: AbortSignal) {
  return request<ProjectDetailResponse>(`/projects/${projectId}`, { signal });
}

export function deleteProject(projectId: number, signal?: AbortSignal) {
  return request<{ ok: boolean }>(`/projects/${projectId}`, {
    method: "DELETE",
    signal,
  });
}

// --- Tasks ---
export function createTask(payload: TaskCreateRequest, signal?: AbortSignal) {
  return request<TaskResponse>("/tasks", {
    method: "POST",
    body: JSON.stringify(payload),
    signal,
  });
}

export function updateTask(
  taskId: number,
  patch: TaskUpdateRequest,
  signal?: AbortSignal,
) {
  return request<TaskResponse>(`/tasks/${taskId}`, {
    method: "PATCH",
    body: JSON.stringify(patch),
    signal,
  });
}

export function deleteTask(taskId: number, signal?: AbortSignal) {
  return request<{ ok: boolean }>(`/tasks/${taskId}`, {
    method: "DELETE",
    signal,
  });
}

// --- Plans ---
export function generatePlan(
  projectId: number,
  payload: PlanGenerateInput,
  signal?: AbortSignal,
) {
  return request<GeneratePlanResponse>(`/projects/${projectId}/plan/generate`, {
    method: "POST",
    body: JSON.stringify(payload),
    signal,
  });
}

export function revisePlan(
  projectId: number,
  payload: RevisePlanInput,
  signal?: AbortSignal,
) {
  return request<GeneratePlanResponse>(`/projects/${projectId}/plan/revise`, {
    method: "POST",
    body: JSON.stringify(payload),
    signal,
  });
}

export function applyPlan(
  projectId: number,
  payload: PlanApplyInput,
  signal?: AbortSignal,
) {
  return request<ProjectDetailResponse>(`/projects/${projectId}/plan/apply`, {
    method: "POST",
    body: JSON.stringify(payload),
    signal,
  });
}

// --- Draft plans ---
export function generatePlanDraft(
  payload: PlanGenerateInput,
  signal?: AbortSignal,
) {
  return request<GeneratePlanResponse>("/plan/generate", {
    method: "POST",
    body: JSON.stringify(payload),
    signal,
  });
}

export function revisePlanDraft(
  payload: RevisePlanInput,
  signal?: AbortSignal,
) {
  return request<GeneratePlanResponse>("/plan/revise", {
    method: "POST",
    body: JSON.stringify(payload),
    signal,
  });
}
