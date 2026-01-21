<script lang="ts">
  import { tick } from "svelte";
  import TaskCard from "./TaskCard.svelte";
  import type { TaskResponse, TaskStatus } from "$lib/api";
  import { dndzone, type DndEvent } from "svelte-dnd-action";

  export let title: string;
  export let status: TaskStatus;

  export let items: TaskResponse[] = [];

  export let onItemsChange: (
    status: TaskStatus,
    next: TaskResponse[],
    isFinal: boolean,
  ) => void;

  export let onDeleteTask: (taskId: number) => void | Promise<void>;
  export let onEditTask: (
    taskId: number,
    patch: { title?: string; description?: string },
  ) => void | Promise<void>;

  export let onCreateTask: (
    status: TaskStatus,
    payload: { title: string; description?: string },
  ) => void | Promise<void>;

  let adding = false;
  let creating = false;

  let titleDraft = "";
  let descDraft = "";

  let titleInput: HTMLInputElement | null = null;
  let descTextarea: HTMLTextAreaElement | null = null;

  function handleConsider(e: CustomEvent<DndEvent<TaskResponse>>) {
    onItemsChange(status, e.detail.items, false);
  }

  function handleFinalize(e: CustomEvent<DndEvent<TaskResponse>>) {
    onItemsChange(status, e.detail.items, true);
  }

  function stopEvent(e: Event) {
    e.preventDefault();
    e.stopPropagation();
  }

  async function openAdd() {
    adding = true;
    creating = false;
    titleDraft = "";
    descDraft = "";
    await tick();
    titleInput?.focus();
  }

  function cancelAdd() {
    adding = false;
    creating = false;
    titleDraft = "";
    descDraft = "";
  }

  async function submitAdd() {
    if (creating) return;

    const t = titleDraft.trim();
    const d = descDraft.trim();

    if (!t) return;

    creating = true;
    try {
      await onCreateTask(status, { title: t, description: d ? d : undefined });
      cancelAdd();
    } finally {
      creating = false;
    }
  }
</script>

<section
  class="flex min-h-[520px] flex-col rounded-3xl bg-white/5 p-4 ring-1 ring-white/10"
>
  <div class="mb-3 flex items-start justify-between gap-3">
    <div>
      <div class="text-base font-extrabold">{title}</div>
    </div>

    <div class="flex items-center gap-2">
      <span
        class="rounded-full bg-white/5 px-2 py-1 text-xs font-semibold text-slate-200 ring-1 ring-white/10"
      >
        {items.length}
      </span>

      <button
        type="button"
        class="rounded-xl bg-white/10 px-3 py-2 text-xs font-semibold text-white ring-1 ring-white/10 hover:bg-white/15 disabled:opacity-50"
        on:click|stopPropagation={openAdd}
        disabled={adding}
        title="Add a new task"
      >
        + Add
      </button>
    </div>
  </div>

  {#if adding}
    <div
      class="mb-3 rounded-2xl bg-slate-950/40 px-4 py-3 ring-1 ring-white/10"
    >
      <input
        bind:this={titleInput}
        class="w-full rounded-xl bg-white/5 px-3 py-2 text-sm font-semibold text-slate-100 ring-1 ring-white/10"
        placeholder="Task title"
        bind:value={titleDraft}
        on:keydown={(e) => {
          if ((e.ctrlKey || e.metaKey) && e.key === "Enter") submitAdd();
          if (e.key === "Escape") cancelAdd();
        }}
      />

      <textarea
        bind:this={descTextarea}
        class="mt-2 w-full resize-none rounded-xl bg-white/5 px-3 py-2 text-sm text-slate-200 ring-1 ring-white/10"
        rows="3"
        placeholder="Description (optional)"
        bind:value={descDraft}
        on:keydown={(e) => {
          if (e.key === "Escape") cancelAdd();
        }}
      ></textarea>

      <div class="mt-3 flex flex-wrap gap-2">
        <button
          type="button"
          class="rounded-xl bg-indigo-500/20 px-3 py-2 text-xs font-semibold text-indigo-100 ring-1 ring-indigo-400/30 hover:bg-indigo-500/30 disabled:opacity-50"
          on:click={submitAdd}
          disabled={creating || !titleDraft.trim()}
        >
          {creating ? "Adding..." : "Add task"}
        </button>

        <button
          type="button"
          class="rounded-xl bg-white/10 px-3 py-2 text-xs font-semibold text-white ring-1 ring-white/10 hover:bg-white/15 disabled:opacity-50"
          on:click={cancelAdd}
          disabled={creating}
        >
          Cancel
        </button>
      </div>
    </div>
  {/if}

  <div
    class="flex-1 space-y-2 rounded-2xl p-2"
    class:empty-zone={items.length === 0}
    use:dndzone={{ items, flipDurationMs: 140, type: "TASK" }}
    on:consider={handleConsider}
    on:finalize={handleFinalize}
  >
    {#each items as task (task.id)}
      <TaskCard {task} {onDeleteTask} {onEditTask} />
    {/each}
  </div>
</section>
