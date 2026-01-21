const BASE_URL = "http://localhost:8000";
type ApiErrorBody = { detail?: string };

// -----------------------------
export type TaskStatus = "todo" | "in_progress" | "done";
export type TaskSize = "S" | "M" | "L";

// -----------------------------
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

// -----------------------------
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
  experience_level?: "beginner" | "intermediate" | "advanced" | null;
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
  experience_level?: "beginner" | "intermediate" | "advanced" | null;
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
async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...(options.headers ?? {}),
    },
  });

  if (!res.ok) {
    let detail = "";
    try {
      const data = (await res.json()) as ApiErrorBody;
      if (data?.detail) detail = `: ${data.detail}`;
    } catch (err) {
      // ignore JSON parse errors, raise HTTP errors
    }
    throw new Error(`API error ${res.status}${detail}`);
  }
  return (await res.json()) as T;
}

export async function deleteProject(
  projectId: number,
): Promise<{ ok: boolean }> {
  const response = await fetch(`${BASE_URL}/projects/${projectId}`, {
    method: "DELETE",
  });
  if (!response.ok) throw new Error(await response.text());
  return await response.json();
}

export function revisePlan(projectId: number, payload: RevisePlanInput) {
  return request<GeneratePlanResponse>(`/projects/${projectId}/plan/revise`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listProjects() {
  return request<ProjectResponse[]>("/projects");
}

export function createProject(payload: ProjectCreateRequest) {
  return request<ProjectResponse>("/projects", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getProject(projectId: number) {
  return request<ProjectDetailResponse>(`/projects/${projectId}`);
}

export function generatePlan(projectId: number, payload: PlanGenerateInput) {
  return request<GeneratePlanResponse>(`/projects/${projectId}/plan/generate`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function applyPlan(projectId: number, payload: PlanApplyInput) {
  return request<ProjectDetailResponse>(`/projects/${projectId}/plan/apply`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateTask(taskId: number, patch: TaskUpdateRequest) {
  return request<TaskResponse>(`/tasks/${taskId}`, {
    method: "PATCH",
    body: JSON.stringify(patch),
  });
}

export async function deleteTask(taskId: number): Promise<{ ok: boolean }> {
  const res = await fetch(`${BASE_URL}/tasks/${taskId}`, { method: "DELETE" });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export function createTask(payload: TaskCreateRequest) {
  return request<TaskResponse>("/tasks", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function generatePlanDraft(payload: PlanGenerateInput) {
  return request<GeneratePlanResponse>("/plan/generate", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function revisePlanDraft(payload: RevisePlanInput) {
  return request<GeneratePlanResponse>("/plan/revise", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
