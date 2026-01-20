<script lang="ts">
  import { goto } from "$app/navigation";
  import { Card, CardContent } from "$lib/components/ui/card";
  import type { ProjectResponse } from "$lib/api";

  export let projects: ProjectResponse[] = [];
  export let loading = false;
  export let highlight = false;
</script>

<section
  id="projects"
  tabindex="-1"
  class="scroll-mt-24 rounded-2xl focus:outline-none"
>
  <div class="flex items-end justify-between gap-4">
    <div>
      <div class="flex items-center gap-3">
        <div class="flex items-center gap-2">
          <h2
            class="text-xl font-extrabold tracking-tight transition
                 {highlight
              ? 'text-white drop-shadow-[0_0_18px_rgba(255,255,255,0.35)]'
              : ''}"
          >
            Existing projects
          </h2>

          <span
            class="h-2 w-2 rounded-full transition-opacity
                 {highlight ? 'opacity-100 animate-pulse' : 'opacity-0'}"
            style="background: rgba(255,255,255,0.6);"
            aria-hidden="true"
          ></span>
        </div>
        <span
          class="inline-flex items-center rounded-full bg-white/5 px-2.5 py-1 text-xs
               font-semibold text-slate-200 ring-1 ring-white/10"
          aria-label={`Project count: ${projects.length}`}
        >
          {projects.length}
        </span>
      </div>

      <p class="mt-1 text-sm text-slate-300">
        Open a project to generate a plan and start moving tasks.
      </p>
    </div>
  </div>

  {#if loading}
    <div class="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {#each Array(6) as _}
        <div
          class="h-[120px] animate-pulse rounded-3xl bg-white/5 ring-1 ring-white/10"
        ></div>
      {/each}
    </div>
  {:else if projects.length === 0}
    <div
      class="mt-6 rounded-3xl bg-white/5 p-8 text-center ring-1 ring-white/10"
    >
      <div class="text-lg font-bold text-slate-100">No projects yet</div>
      <div class="mt-2 text-sm text-slate-300">
        Start a project above and plan your goals.
      </div>
    </div>
  {:else}
    <div class="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {#each projects as p (p.id)}
        <button class="text-left" on:click={() => goto(`/projects/${p.id}`)}>
          <Card
            class="rounded-3xl bg-white/5 text-slate-100 ring-1 ring-white/10 transition hover:bg-white/10 hover:ring-white/20"
          >
            <CardContent class="p-5">
              <div class="flex items-start justify-between gap-3">
                <div class="min-w-0">
                  <div class="truncate text-base font-extrabold">{p.title}</div>
                  <div class="mt-2 line-clamp-3 text-sm text-slate-300">
                    {p.goal_text}
                  </div>
                </div>
                <div
                  class="rounded-2xl bg-white/5 px-2 py-1 text-xs text-slate-200 ring-1 ring-white/10"
                >
                  #{p.id}
                </div>
              </div>

              <div class="mt-4 flex flex-wrap gap-2 text-xs text-slate-300">
                {#if p.deadline}
                  <span
                    class="rounded-full bg-white/5 px-2 py-1 ring-1 ring-white/10"
                    >Deadline: {p.deadline}</span
                  >
                {/if}
                {#if typeof p.hours_per_week === "number"}
                  <span
                    class="rounded-full bg-white/5 px-2 py-1 ring-1 ring-white/10"
                    >{p.hours_per_week} hrs/wk</span
                  >
                {/if}
                <span
                  class="rounded-full bg-indigo-400/10 px-2 py-1 text-indigo-200 ring-1 ring-indigo-400/20"
                >
                  Open →
                </span>
              </div>
            </CardContent>
          </Card>
        </button>
      {/each}
    </div>
  {/if}
</section>

<style>
  .line-clamp-3 {
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
    line-clamp: 3;
  }
</style>
