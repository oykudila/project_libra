<script lang="ts">
  import KanbanColumn from "./KanbanColumn.svelte";
  import type {
    ProjectDetailResponse,
    TaskResponse,
    TaskStatus,
  } from "$lib/api";

  export let project: ProjectDetailResponse | null = null;
  export let loading = false;
  export let error = "";

  export let onBack: () => void;
  export let onRefresh: () => void | Promise<void>;
  export let onDelete: () => void | Promise<void>;

  // Parent persistence hook: called on finalize with flattened tasks
  export let onCommit: (
    tasks: Array<{ id: number; status: TaskStatus; order_index: number }>,
  ) => void | Promise<void>;

  let cols: Record<TaskStatus, TaskResponse[]> = {
    todo: [],
    in_progress: [],
    done: [],
  };

  let lastProjectId: number | null = null;
  $: if (project && project.id !== lastProjectId) {
    lastProjectId = project.id;

    const sorted = project.tasks
      .slice()
      .sort((a, b) => (a.order_index ?? 0) - (b.order_index ?? 0));

    cols = {
      todo: sorted.filter((t) => t.status === "todo"),
      in_progress: sorted.filter((t) => t.status === "in_progress"),
      done: sorted.filter((t) => t.status === "done"),
    };
  }

  function normalizeAndFlatten(): Array<{
    id: number;
    status: TaskStatus;
    order_index: number;
  }> {
    const out: Array<{ id: number; status: TaskStatus; order_index: number }> =
      [];
    (["todo", "in_progress", "done"] as const).forEach((s) => {
      cols[s].forEach((t, i) => {
        out.push({ id: t.id, status: s, order_index: i });
      });
    });
    return out;
  }

  async function handleDelete() {
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
    // Update the local column list to keep the gap animation smooth
    cols = { ...cols, [status]: next.map((t) => ({ ...t, status })) };

    // When moving across columns, svelte-dnd-action will also emit for origin/destination,
    // so by the time you drop, both columns should be updated through this handler. :contentReference[oaicite:6]{index=6}

    if (isFinal) {
      const flattened = normalizeAndFlatten();
      await onCommit(flattened);
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
        class="rounded-2xl bg-white/10 px-4 py-2 text-sm font-semibold text-white ring-1 ring-white/10 hover:bg-white/15 disabled:opacity-50"
        on:click={() => onRefresh()}
        disabled={loading}
      >
        Refresh
      </button>

      <button
        type="button"
        class="rounded-2xl bg-red-500/15 px-4 py-2 text-sm font-semibold text-red-200 ring-1 ring-red-500/30 hover:bg-red-500/25 disabled:opacity-50"
        on:click={handleDelete}
        disabled={loading || !project}
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
      <KanbanColumn
        title="To do"
        status="todo"
        items={cols.todo}
        onItemsChange={handleItemsChange}
      />
      <KanbanColumn
        title="In progress"
        status="in_progress"
        items={cols.in_progress}
        onItemsChange={handleItemsChange}
      />
      <KanbanColumn
        title="Done"
        status="done"
        items={cols.done}
        onItemsChange={handleItemsChange}
      />
    </div>
  {/if}
</div>
