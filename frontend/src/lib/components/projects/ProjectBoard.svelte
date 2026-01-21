<script lang="ts">
  import KanbanColumn from "./KanbanColumn.svelte";
  import type {
    ProjectDetailResponse,
    TaskResponse,
    TaskStatus,
  } from "$lib/api";

  export let project: ProjectDetailResponse | null = null;
  export let loading = false;
  export let saving = false;
  export let error = "";

  export let onBack: () => void;
  export let onDelete: () => void | Promise<void>;
  export let onDeleteTask: (taskId: number) => void | Promise<void>;
  export let onCreateTask: (
    status: TaskStatus,
    payload: { title: string; description?: string },
  ) => void | Promise<void>;
  export let onEditTask: (
    taskId: number,
    patch: { title?: string; description?: string },
  ) => void | Promise<void>;

  export let onCommit: (
    tasks: Array<{ id: number; status: TaskStatus; order_index: number }>,
  ) => void | Promise<void>;

  const STATUSES = ["todo", "in_progress", "done"] as const;
  const COLUMNS: Array<{ title: string; status: TaskStatus }> = [
    { title: "To Do", status: "todo" },
    { title: "In progress", status: "in_progress" },
    { title: "Done", status: "done" },
  ];

  let cols: Record<TaskStatus, TaskResponse[]> = {
    todo: [],
    in_progress: [],
    done: [],
  };

  $: if (project) {
    const next: Record<TaskStatus, TaskResponse[]> = {
      todo: [],
      in_progress: [],
      done: [],
    };

    const sorted = project.tasks
      .slice()
      .sort((a, b) => (a.order_index ?? 0) - (b.order_index ?? 0));

    for (const t of sorted) {
      const s: TaskStatus =
        t.status === "in_progress" || t.status === "done" ? t.status : "todo";
      next[s].push(t);
    }
    cols = next;
  } else {
    cols = { todo: [], in_progress: [], done: [] };
  }

  function normalizeAndFlatten() {
    const out: Array<{ id: number; status: TaskStatus; order_index: number }> =
      [];
    for (const s of STATUSES) {
      cols[s].forEach((t, i) =>
        out.push({ id: t.id, status: s, order_index: i }),
      );
    }
    return out;
  }

  async function handleDeleteProject() {
    if (!project) return;
    const ok = confirm(`Delete "${project.title}"? This cannot be undone.`);
    if (!ok) return;
    await onDelete();
  }

  async function handleItemsChange(
    status: TaskStatus,
    next: TaskResponse[],
    isFinal: boolean,
  ) {
    cols = { ...cols, [status]: next.map((t) => ({ ...t, status })) };

    if (isFinal) {
      await onCommit(normalizeAndFlatten());
    }
  }
</script>

<div class="pointer-events-none fixed inset-0 overflow-hidden">
  <div
    class="absolute -top-40 left-1/2 h-[520px] w-[920px] -translate-x-1/2 rounded-full bg-indigo-500/20 blur-3xl"
  ></div>
  <div
    class="absolute -bottom-40 left-1/3 h-[520px] w-[920px] -translate-x-1/2 rounded-full bg-fuchsia-500/10 blur-3xl"
  ></div>
</div>

<div class="relative">
  <div class="mb-6 flex flex-wrap items-start justify-between gap-4">
    <div class="min-w-0">
      <button
        type="button"
        class="mb-3 inline-flex items-center gap-2 rounded-xl bg-white/5 px-3 py-2 text-sm text-slate-200 ring-1 ring-white/10 hover:bg-white/10"
        on:click={onBack}
      >
        ← Back
      </button>

      <h1 class="truncate text-2xl font-extrabold tracking-tight">
        {project ? project.title : "Project"}
      </h1>

      {#if project}
        <p class="mt-2 max-w-3xl text-sm text-slate-300">{project.goal_text}</p>
      {/if}
    </div>

    <div class="flex items-center gap-3">
      <button
        type="button"
        class="rounded-2xl bg-red-500/15 px-4 py-2 text-sm font-semibold text-red-200 ring-1 ring-red-500/30 hover:bg-red-500/25 disabled:opacity-50"
        on:click={handleDeleteProject}
        disabled={loading || saving || !project}
        title="Delete this project"
      >
        Delete
      </button>
    </div>
  </div>

  {#if error}
    <div
      class="mb-6 rounded-2xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-200"
      role="alert"
    >
      {error}
    </div>
  {/if}

  {#if loading}
    <div class="grid gap-4 lg:grid-cols-3">
      <div
        class="h-[520px] animate-pulse rounded-3xl bg-white/5 ring-1 ring-white/10"
      ></div>
      <div
        class="h-[520px] animate-pulse rounded-3xl bg-white/5 ring-1 ring-white/10"
      ></div>
      <div
        class="h-[520px] animate-pulse rounded-3xl bg-white/5 ring-1 ring-white/10"
      ></div>
    </div>
  {:else if !project}
    <div class="rounded-3xl bg-white/5 p-8 text-center ring-1 ring-white/10">
      <div class="text-lg font-bold text-slate-100">Project not found</div>
    </div>
  {:else}
    <div class="grid gap-4 lg:grid-cols-3">
      {#each COLUMNS as col (col.status)}
        <KanbanColumn
          title={col.title}
          status={col.status}
          items={cols[col.status]}
          onItemsChange={handleItemsChange}
          {onDeleteTask}
          {onEditTask}
          {onCreateTask}
        />
      {/each}
    </div>
  {/if}
</div>
