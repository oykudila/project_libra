<script lang="ts">
  import type { TaskResponse } from "$lib/api";
  import { tick } from "svelte";

  let titleInput: HTMLInputElement | null = null;
  let descTextarea: HTMLTextAreaElement | null = null;

  export let task: TaskResponse;

  export let onDeleteTask: (taskId: number) => void | Promise<void>;
  export let onEditTask: (
    taskId: number,
    patch: { title?: string; description?: string },
  ) => void | Promise<void>;

  let editingTitle = false;
  let editingDesc = false;

  let titleDraft = "";
  let descDraft = "";

  async function startEditTitle() {
    editingTitle = true;
    titleDraft = task.title;
    await tick();
    titleInput?.focus();
  }

  async function startEditDesc() {
    editingDesc = true;
    descDraft = task.description ?? "";
    await tick();
    descTextarea?.focus();
  }

  async function saveTitle() {
    if (!editingTitle) return;
    editingTitle = false;

    const next = titleDraft.trim();
    if (!next) {
      // Don’t allow empty titles; just revert visually
      titleDraft = task.title;
      return;
    }
    if (next !== task.title) {
      await onEditTask(task.id, { title: next });
    }
  }

  async function saveDesc() {
    if (!editingDesc) return;
    editingDesc = false;

    const next = descDraft.trim();
    const cur = (task.description ?? "").trim();

    if (next !== cur) {
      await onEditTask(task.id, { description: next });
    }
  }

  function stopEvent(e: Event) {
    // prevent drag start + prevent bubbling into dnd container
    e.preventDefault();
    e.stopPropagation();
  }
</script>

<div class="rounded-2xl bg-slate-950/40 px-4 py-3 ring-1 ring-white/10">
  <div class="flex items-start justify-between gap-3">
    <div class="min-w-0 flex-1">
      {#if editingTitle}
        <input
          bind:this={titleInput}
          class="w-full rounded-xl bg-white/5 px-3 py-2 text-sm font-semibold text-slate-100 ring-1 ring-white/10"
          bind:value={titleDraft}
          on:mousedown={stopEvent}
          on:pointerdown={stopEvent}
          on:click|stopPropagation
          on:keydown={(e) => {
            if (e.key === "Enter") saveTitle();
            if (e.key === "Escape") editingTitle = false;
          }}
          on:blur={saveTitle}
        />
      {:else}
        <button
          type="button"
          class="w-full text-left font-semibold"
          title="Click to edit title"
          on:click|stopPropagation={startEditTitle}
          on:mousedown={stopEvent}
          on:pointerdown={stopEvent}
        >
          {task.title}
        </button>
      {/if}

      {#if editingDesc}
        <textarea
          bind:this={descTextarea}
          class="mt-2 w-full resize-none rounded-xl bg-white/5 px-3 py-2 text-sm text-slate-200 ring-1 ring-white/10"
          rows="3"
          bind:value={descDraft}
          on:mousedown={stopEvent}
          on:pointerdown={stopEvent}
          on:click|stopPropagation
          on:keydown={(e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === "Enter") saveDesc();
            if (e.key === "Escape") editingDesc = false;
          }}
          on:blur={saveDesc}
        ></textarea>
      {:else if task.description}
        <button
          type="button"
          class="mt-2 w-full text-left text-sm text-slate-300"
          title="Click to edit description"
          on:click|stopPropagation={startEditDesc}
          on:mousedown={stopEvent}
          on:pointerdown={stopEvent}
        >
          {task.description}
        </button>
      {:else}
        <button
          type="button"
          class="mt-2 text-left text-sm text-slate-400 hover:text-slate-200"
          on:click|stopPropagation={startEditDesc}
          on:mousedown={stopEvent}
          on:pointerdown={stopEvent}
        >
          + Add description
        </button>
      {/if}

      <div class="mt-2 text-xs text-slate-400">
        {#if task.estimate}Est: {task.estimate}{/if}
      </div>
    </div>

    <button
      type="button"
      class="shrink-0 rounded-xl bg-red-500/15 px-3 py-2 text-xs font-semibold text-red-200 ring-1 ring-red-500/30 hover:bg-red-500/25"
      title="Delete task"
      on:click|stopPropagation={() => onDeleteTask(task.id)}
      on:mousedown={stopEvent}
      on:pointerdown={stopEvent}
    >
      Delete
    </button>
  </div>
</div>
