<script lang="ts">
  import { onDestroy, onMount } from "svelte";
  import { goto } from "$app/navigation";

  import {
    Hero,
    CreateProjectCard,
    ProjectsSection,
  } from "$lib/components/landing";

  import {
    createProject,
    listProjects,
    generatePlanDraft,
    revisePlanDraft,
    applyPlan,
    deleteProject,
    type ProjectResponse,
    type GeneratePlanResponse,
    type ProposeTask,
  } from "$lib/api";

  // --- Types ---
  type ExperienceLevel = "beginner" | "intermediate" | "advanced";

  type PendingDraft = {
    title: string;
    goal_text: string;
    deadline: string | null;
    hours_per_week: number | null;
    experience_level: ExperienceLevel;
  };

  let projects: ProjectResponse[] = [];
  let loading = false;

  let title = "";
  let goal_text = "";
  let deadline = "";
  let hours_per_week: number | null = null;
  let experience_level: ExperienceLevel = "beginner";

  let pending: PendingDraft | null = null;
  let generated: GeneratePlanResponse | null = null;

  let creating = false;
  let error = "";

  let adjustment = "";
  let revising = false;

  // AI typing animation
  let typedTasks: ProposeTask[] = [];
  let typing = false;
  let typingTimer: ReturnType<typeof setTimeout> | null = null;

  let refreshCtrl: AbortController | null = null;

  async function refresh() {
    refreshCtrl?.abort();
    refreshCtrl = new AbortController();

    loading = true;
    error = "";
    try {
      projects = await listProjects(refreshCtrl.signal);
    } catch (e: unknown) {
      if (e instanceof DOMException && e.name === "AbortError") return;
      error = e instanceof Error ? e.message : "Failed to load projects";
    } finally {
      loading = false;
    }
  }

  onMount(refresh);

  onDestroy(() => {
    refreshCtrl?.abort();
    if (typingTimer) clearTimeout(typingTimer);
  });

  function stopTyping() {
    if (typingTimer) {
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
    const acc: ProposeTask[] = [];

    const tick = () => {
      acc.push(tasks[i]);

      typedTasks = acc.slice();
      i += 1;

      if (i >= tasks.length) {
        typing = false;
        typingTimer = null;
        return;
      }

      typingTimer = setTimeout(tick, 10);
    };

    tick();
  }

  function resetGenerated() {
    stopTyping();
    pending = null;
    generated = null;
    typedTasks = [];
  }

  async function onCreate() {
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

    pending = {
      title: t,
      goal_text: g,
      deadline: d,
      hours_per_week: hpw,
      experience_level,
    };

    try {
      const plan = await generatePlanDraft({
        goal_text: g,
        deadline: d,
        hours_per_week: hpw,
        experience_level,
        detail_level: "simple",
      });

      generated = plan;
      if (plan.type === "plan") startTypingTasks(plan.tasks);
    } catch (e: unknown) {
      error = e instanceof Error ? e.message : "Failed to generate plan";
      resetGenerated();
    } finally {
      creating = false;
    }
  }

  async function acceptPlan() {
    if (!pending || !generated || generated.type !== "plan") return;

    creating = true;
    error = "";
    stopTyping();

    try {
      const created = await createProject({
        title: pending.title,
        goal_text: pending.goal_text,
        deadline: pending.deadline,
        hours_per_week: pending.hours_per_week,
      });

      await applyPlan(created.id, {
        milestones: generated.milestones,
        tasks: generated.tasks,
      });

      resetGenerated();
      goto(`/projects/${created.id}`);
    } catch (e: unknown) {
      error = e instanceof Error ? e.message : "Failed to create/apply plan";
    } finally {
      creating = false;
    }
  }

  async function onAdjustPlan() {
    if (!pending || !generated || generated.type !== "plan") return;

    const adj = adjustment.trim();
    if (!adj) return;

    revising = true;
    error = "";
    stopTyping();

    try {
      const revised = await revisePlanDraft({
        goal_text: pending.goal_text,
        deadline: pending.deadline,
        hours_per_week: pending.hours_per_week,
        experience_level: pending.experience_level,
        detail_level: "simple",
        constraints: null,
        current_plan: generated,
        adjustment: adj,
      });

      generated = revised;
      adjustment = "";
      if (revised.type === "plan") startTypingTasks(revised.tasks);
    } catch (e: unknown) {
      error = e instanceof Error ? e.message : "Failed to adjust plan";
      if (generated.type === "plan") startTypingTasks(generated.tasks);
    } finally {
      revising = false;
    }
  }

  function discardPlan() {
    resetGenerated();
  }

  async function onDeleteProject(id: number) {
    if (!confirm("Delete this project?")) return;
    try {
      await deleteProject(id);
      projects = projects.filter((p) => p.id !== id);
    } catch (e: unknown) {
      error = e instanceof Error ? e.message : "Failed to delete project";
    }
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
        bind:experience_level
        {creating}
        {error}
        {onCreate}
      />

      {#if creating && !generated}
        <section
          class="mx-auto mt-10 max-w-xl rounded-3xl bg-white/5 p-6 ring-1 ring-white/10"
        >
          <div class="text-sm font-semibold">Drafting your plan…</div>
          <div class="mt-2 space-y-2">
            <div
              class="h-12 animate-pulse rounded-2xl bg-slate-950/40 ring-1 ring-white/10"
            ></div>
            <div
              class="h-12 animate-pulse rounded-2xl bg-slate-950/40 ring-1 ring-white/10"
            ></div>
            <div
              class="h-12 animate-pulse rounded-2xl bg-slate-950/40 ring-1 ring-white/10"
            ></div>
          </div>
        </section>
      {/if}
    </section>

    {#if pending && generated?.type === "plan"}
      <section
        class="mx-auto mt-10 max-w-xl rounded-3xl bg-white/5 p-6 ring-1 ring-white/10"
        aria-label="Generated tasks"
      >
        <div class="flex items-start justify-between gap-4">
          <div
            class="rounded-2xl bg-white/5 px-2 py-1 text-xs text-slate-200 ring-1 ring-white/10"
          >
            This is the draft plan, you can also adjust your tasks later.
          </div>
          <div
            class="rounded-2xl bg-white/5 px-2 py-1 text-xs text-slate-200 ring-1 ring-white/10"
          >
            Experience: {pending.experience_level}
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
              {#if task.estimate}
                <div class="mt-2 text-xs text-slate-400">
                  Task Size: {task.estimate}
                </div>
              {/if}
            </li>
          {/each}
        </ol>

        <div class="mt-5 space-y-3">
          <div class="rounded-2xl bg-slate-950/40 p-3 ring-1 ring-white/10">
            <div class="text-sm font-semibold">Want to change something?</div>
            <div class="mt-1 text-xs text-slate-300">
              Add constraints like budget, schedule, tools, preferences, or
              difficulty. Example: “Keep it low-budget and only 20 minutes a
              day.”
            </div>

            <textarea
              class="mt-3 w-full resize-none rounded-2xl bg-white/5 px-3 py-2 text-sm text-slate-200 ring-1 ring-white/10"
              rows="3"
              bind:value={adjustment}
              placeholder="e.g., low budget, 20 min/day, focus on practice not theory…"
            ></textarea>

            <div class="mt-3 flex flex-wrap gap-3">
              <button
                class="rounded-2xl bg-indigo-500/20 px-4 py-2 text-sm font-semibold text-indigo-100 ring-1 ring-indigo-400/30 hover:bg-indigo-500/30 disabled:opacity-50"
                on:click={onAdjustPlan}
                disabled={creating || typing || revising || !adjustment.trim()}
              >
                {revising ? "Adjusting..." : "Adjust plan"}
              </button>

              <button
                class="rounded-2xl bg-white/10 px-4 py-2 text-sm font-semibold text-white ring-1 ring-white/10 hover:bg-white/15 disabled:opacity-50"
                on:click={acceptPlan}
                disabled={creating || typing || revising}
              >
                Accept plan
              </button>

              <button
                class="rounded-2xl bg-red-500/15 px-4 py-2 text-sm font-semibold text-red-200 ring-1 ring-red-500/30 hover:bg-red-500/25 disabled:opacity-50"
                on:click={discardPlan}
                disabled={creating || revising}
              >
                Discard
              </button>
            </div>
          </div>
        </div>
      </section>
    {/if}

    <section class="mx-auto mt-20 max-w-6xl">
      <ProjectsSection {projects} {loading} />
    </section>
  </main>
</div>
