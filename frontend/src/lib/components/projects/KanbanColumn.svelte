<script lang="ts">
  import { dndzone, type DndEvent } from "svelte-dnd-action";
  import TaskCard from "./TaskCard.svelte";
  import type { TaskResponse, TaskStatus } from "$lib/api";

  export let title: string;
  export let status: TaskStatus;

  // Controlled list for this column
  export let items: TaskResponse[] = [];

  // Parent callback when list changes (during consider + finalize)
  export let onItemsChange: (
    status: TaskStatus,
    next: TaskResponse[],
    isFinal: boolean,
  ) => void;

  function handleConsider(e: CustomEvent<DndEvent<TaskResponse>>) {
    // "consider" is fired continuously as items make room (this is the smooth gap)
    onItemsChange(status, e.detail.items, false);
  }

  function handleFinalize(e: CustomEvent<DndEvent<TaskResponse>>) {
    // finalize fires on drop (both origin + destination according to docs)
    onItemsChange(status, e.detail.items, true);
  }
</script>

<section class="rounded-3xl bg-white/5 p-4 ring-1 ring-white/10">
  <div class="mb-3 flex items-start justify-between gap-3">
    <div>
      <div class="text-base font-extrabold">{title}</div>
    </div>

    <span
      class="rounded-full bg-white/5 px-2 py-1 text-xs font-semibold text-slate-200 ring-1 ring-white/10"
    >
      {items.length}
    </span>
  </div>

  <div
    class="min-h-[420px] space-y-2 rounded-2xl p-2"
    use:dndzone={{ items, flipDurationMs: 140, type: "TASK" }}
    on:consider={handleConsider}
    on:finalize={handleFinalize}
  >
    {#each items as task (task.id)}
      <TaskCard {task} />
    {/each}
  </div>
</section>
