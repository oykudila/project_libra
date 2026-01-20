<script lang="ts">
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";

  import {
    Hero,
    CreateProjectCard,
    ProjectsSection,
  } from "$lib/components/landing";

  import {
    createProject,
    listProjects,
    generatePlan,
    applyPlan,
    type ProjectResponse,
    type GeneratePlanResponse,
    type ProposeTask,
    deleteProject,
  } from "$lib/api";

  let projects: ProjectResponse[] = [];
  let loading = false;
  let creating = false;
  let error = "";

  let title = "";
  let goal_text = "";
  let deadline = "";
  let hours_per_week: number | null = null;

  let createdId: number | null = null;
  let generated: GeneratePlanResponse | null = null;

  let typedTasks: ProposeTask[] = [];
  let typing = false;
  let typingTimer: ReturnType<typeof setTimeout> | null = null;

  async function refresh() {
    loading = true;
    error = "";
    try {
      projects = await listProjects();
    } catch (e: unknown) {
      error = e instanceof Error ? e.message : "Failed to load projects";
    } finally {
      loading = false;
    }
  }

  onMount(refresh);

  function stopTyping() {
    if (typingTimer !== null) {
      clearTimeout(typingTimer);
      typingTimer = null;
    }
    typing = false;
  }

  function startTypingTasks(tasks: ProposeTask[]) {
    stopTyping();
    typedTasks = [];
    typing = true;

    let i = 0;

    function tick() {
      typedTasks = [...typedTasks, tasks[i]];
      i += 1;

      if (i >= tasks.length) {
        typing = false;
        typingTimer = null;
        return;
      }

      const delay = 180 + Math.random() * 270;
      typingTimer = setTimeout(tick, delay);
    }

    tick();
  }

  function resetGenerated() {
    stopTyping();
    createdId = null;
    generated = null;
    typedTasks = [];
  }

  async function onCreate() {
    console.log("onCreate clicked - starting generation");
    error = "";

    const t = title.trim();
    const g = goal_text.trim();
    const d = deadline.trim() ? deadline.trim() : null;
    const hpw =
      hours_per_week === null
        ? null
        : Number.isFinite(hours_per_week) &&
            Number.isInteger(hours_per_week) &&
            hours_per_week >= 0
          ? hours_per_week
          : null;

    if (!t || !g) {
      error = "Title and goal are required.";
      return;
    }

    creating = true;
    resetGenerated();

    try {
      const created = await createProject({
        title: t,
        goal_text: g,
        deadline: d,
        hours_per_week: hpw,
      });
      createdId = created.id;

      const plan = await generatePlan(created.id, {
        goal_text: g,
        deadline: d,
        hours_per_week: hpw,
        experience_level: "beginner",
        detail_level: "simple",
      });

      generated = plan;

      if (plan.type === "plan") {
        startTypingTasks(plan.tasks);
      }
    } catch (e: unknown) {
      error = e instanceof Error ? e.message : "Failed to create project";
      resetGenerated();
    } finally {
      creating = false;
      refresh();
    }
  }

  async function acceptPlan() {
    if (!createdId || !generated || generated.type !== "plan") return;

    creating = true;
    error = "";
    stopTyping();

    try {
      await applyPlan(createdId, {
        milestones: generated.milestones,
        tasks: generated.tasks,
      });

      goto(`/projects/${createdId}`);
    } catch (e: unknown) {
      error = e instanceof Error ? e.message : "Failed to apply plan";
    } finally {
      creating = false;
    }
  }

  async function discardPlan() {
    if (createdId) {
      try {
        await deleteProject(createdId);
      } catch {
        //
      }
    }
    resetGenerated();
    refresh();
  }
</script>

<div class="min-h-screen bg-slate-950 text-slate-100">
  <div class="pointer-events-none fixed inset-0 overflow-hidden">
    <div
      class="absolute -top-40 left-1/2 h-[520px] w-[920px] -translate-x-1/2 rounded-full bg-indigo-500/20 blur-3xl"
    ></div>
    <div
      class="absolute -bottom-40 left-1/3 h-[520px] w-[920px] -translate-x-1/2 rounded-full bg-fuchsia-500/10 blur-3xl"
    ></div>
  </div>

  <main class="relative mx-auto w-full max-w-6xl px-6 pb-16 pt-6">
    <Hero />

    <section
      id="create"
      class="mx-auto mt-12 max-w-xl scroll-mt-24"
      aria-label="Create a project"
    >
      <CreateProjectCard
        bind:title
        bind:goal_text
        bind:deadline
        bind:hours_per_week
        {creating}
        {error}
        {onCreate}
      />
    </section>

    {#if createdId && generated?.type === "plan"}
      <section
        class="mx-auto mt-10 max-w-xl rounded-3xl bg-white/5 p-6 ring-1 ring-white/10"
        aria-label="Generated tasks"
      >
        <div class="flex items-start justify-between gap-4">
          <div>
            <h3 class="text-lg font-extrabold">Generated todo list</h3>
            <p class="mt-1 flex items-center gap-2 text-sm text-slate-300">
              {#if typing}
                <span
                  class="inline-block h-2 w-2 animate-pulse rounded-full bg-white/70"
                ></span>
                Generating…
              {:else}
                Done. If you don’t like it, discard and generate again.
              {/if}
            </p>
          </div>

          <div
            class="rounded-2xl bg-white/5 px-2 py-1 text-xs text-slate-200 ring-1 ring-white/10"
          >
            Project #{createdId}
          </div>
        </div>

        <ol class="mt-4 space-y-2">
          {#each typedTasks as task, i (i)}
            <li
              class="rounded-2xl bg-slate-950/40 px-4 py-3 ring-1 ring-white/10"
            >
              <div class="font-semibold">{task.title}</div>
              {#if task.description}
                <div class="mt-1 text-sm text-slate-300">
                  {task.description}
                </div>
              {/if}
              <div class="mt-2 text-xs text-slate-400">
                {#if task.estimate}Est: {task.estimate}{/if}
              </div>
            </li>
          {/each}
        </ol>

        <div class="mt-5 flex flex-wrap gap-3">
          <button
            class="rounded-2xl bg-white/10 px-4 py-2 text-sm font-semibold text-white ring-1 ring-white/10 hover:bg-white/15 disabled:opacity-50"
            on:click={acceptPlan}
            disabled={creating || typing}
          >
            Accept plan
          </button>

          <button
            class="rounded-2xl bg-white/5 px-4 py-2 text-sm font-semibold text-slate-200 ring-1 ring-white/10 hover:bg-white/10 disabled:opacity-50"
            on:click={discardPlan}
            disabled={creating}
          >
            Discard
          </button>
        </div>
      </section>
    {/if}

    <section class="mx-auto mt-12 max-w-6xl">
      <ProjectsSection {projects} {loading} />
    </section>
  </main>
</div>
