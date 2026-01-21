<script lang="ts">
  import { onMount } from "svelte";
  import { page } from "$app/state";
  import { goto } from "$app/navigation";

  import {
    getProject,
    updateTask,
    deleteTask,
    deleteProject,
    createTask,
    type ProjectDetailResponse,
    type TaskStatus,
  } from "$lib/api";

  import ProjectBoard from "$lib/components/projects/ProjectBoard.svelte";

  let projectId = 0;
  let project: ProjectDetailResponse | null = null;

  let loading = false;
  let error = "";
  let saving = false;

  let snapshot = new Map<number, { status: TaskStatus; order_index: number }>();

  function getId() {
    const n = Number(page.params.id);
    return Number.isFinite(n) ? n : 0;
  }

  async function refresh() {
    loading = true;
    error = "";
    try {
      project = await getProject(projectId);
      snapshot = new Map(
        project.tasks.map((t) => [
          t.id,
          { status: t.status, order_index: t.order_index },
        ]),
      );
    } catch (e: unknown) {
      error = e instanceof Error ? e.message : "Failed to load project";
      project = null;
      snapshot = new Map();
    } finally {
      loading = false;
    }
  }

  onMount(async () => {
    projectId = getId();
    await refresh();
  });

  async function onCommit(
    desired: Array<{ id: number; status: TaskStatus; order_index: number }>,
  ) {
    if (!project) return;

    saving = true;
    error = "";

    const prev = new Map(
      project.tasks.map((t) => [
        t.id,
        { status: t.status, order_index: t.order_index },
      ]),
    );

    const toPatch = desired.filter((d) => {
      const p = prev.get(d.id);
      return !p || p.status !== d.status || p.order_index !== d.order_index;
    });

    const desiredById = new Map(desired.map((d) => [d.id, d]));
    project = {
      ...project,
      tasks: project.tasks.map((t) => {
        const d = desiredById.get(t.id);
        return d ? { ...t, status: d.status, order_index: d.order_index } : t;
      }),
    };

    try {
      if (toPatch.length > 0) {
        await Promise.all(
          toPatch.map((d) =>
            updateTask(d.id, { status: d.status, order_index: d.order_index }),
          ),
        );
      }
    } catch (e: unknown) {
      error = e instanceof Error ? e.message : "Failed to save drag & drop";
      await refresh();
    } finally {
      saving = false;
    }
  }

  async function onCreateTask(
    status: TaskStatus,
    payload: { title: string; description?: string },
  ) {
    if (!project) return;

    const tempId = -Math.floor(Math.random() * 1_000_000_000);

    const prev = project;
    project = {
      ...project,
      tasks: project.tasks.map((t) =>
        t.status === status
          ? { ...t, order_index: (t.order_index ?? 0) + 1 }
          : t,
      ),
    };

    const tempTask = {
      id: tempId,
      title: payload.title,
      description: payload.description ?? null,
      status,
      due_date: null,
      estimate: null,
      order_index: 0,
      milestone_id: null,
    };

    project = { ...project, tasks: [...project.tasks, tempTask] };

    try {
      const created = await createTask({
        project_id: projectId,
        title: payload.title,
        description: payload.description ?? null,
        status,
        order_index: 0,
      });

      project = {
        ...project,
        tasks: project.tasks.map((t) => (t.id === tempId ? created : t)),
      };
    } catch (e: unknown) {
      error = e instanceof Error ? e.message : "Failed to create task";
      project = prev;
    }
  }

  async function onDeleteTask(taskId: number) {
    if (!project) return;
    if (!confirm("Delete this task?")) return;

    const prev = project;
    project = {
      ...project,
      tasks: project.tasks.filter((t) => t.id !== taskId),
    };

    try {
      await deleteTask(taskId);
    } catch (e: unknown) {
      error = e instanceof Error ? e.message : "Failed to delete task";
      project = prev; // rollback
    }
  }

  async function onEditTask(
    taskId: number,
    patch: { title?: string; description?: string },
  ) {
    if (!project) return;

    const prev = project;
    project = {
      ...project,
      tasks: project.tasks.map((t) =>
        t.id === taskId ? { ...t, ...patch } : t,
      ),
    };

    try {
      await updateTask(taskId, patch);
    } catch (e: unknown) {
      error = e instanceof Error ? e.message : "Failed to update task";
      project = prev; // rollback
    }
  }

  async function handleDeleteProject() {
    if (!project) return;
    await deleteProject(project.id);
    goto("/");
  }
</script>

<div class="min-h-screen bg-slate-950 text-slate-100">
  <main class="mx-auto w-full max-w-6xl px-6 pb-16 pt-6">
    <ProjectBoard
      {project}
      {loading}
      {error}
      onBack={() => goto("/")}
      onRefresh={refresh}
      {onCommit}
      onDelete={handleDeleteProject}
      {onDeleteTask}
      {onEditTask}
      {onCreateTask}
    />
  </main>
</div>
