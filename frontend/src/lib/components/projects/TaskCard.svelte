<script lang="ts">
  import type { TaskResponse } from "$lib/api";
  export let task: TaskResponse;

  function down() {
    document.documentElement.classList.add("cursor-grabbing");
  }
  function up() {
    document.documentElement.classList.remove("cursor-grabbing");
  }
</script>

<article
  class="rounded-2xl bg-slate-950/40 px-4 py-3 ring-1 ring-white/10 transition hover:bg-white/5
         cursor-grab select-none"
  on:pointerdown={down}
  on:pointerup={up}
  on:pointercancel={up}
>
  <div class="flex items-start justify-between gap-3">
    <div class="min-w-0">
      <div class="text-sm font-semibold">{task.title}</div>
      {#if task.description}
        <div class="mt-1 text-xs text-slate-300">{task.description}</div>
      {/if}
    </div>

    {#if task.estimate}
      <span
        class="shrink-0 rounded-full bg-white/5 px-2 py-1 text-[11px] text-slate-200 ring-1 ring-white/10"
      >
        {task.estimate}
      </span>
    {/if}
  </div>
</article>
