<script lang="ts">
  import { onMount } from "svelte";
  import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
  } from "$lib/components/ui/card";
  import { Button } from "$lib/components/ui/button";
  import { Input } from "$lib/components/ui/input";
  import { Textarea } from "$lib/components/ui/textarea";
  import { Label } from "$lib/components/ui/label";

  export let title = "";
  export let goal_text = "";
  export let deadline = "";
  export let hours_per_week: number | null = null;
  export let experience_level: "beginner" | "intermediate" | "advanced" =
    "beginner";

  export let creating = false;
  export let error = "";
  export let onCreate: () => void | Promise<void>;

  const idTitle = "lp_title";
  const idGoal = "lp_goal";
  const idDeadline = "lp_deadline";
  const idHpw = "lp_hpw";
  const idExp = "lp_exp";

  onMount(() => {
    requestAnimationFrame(() => {
      const el = document.getElementById(idTitle);
      if (el instanceof HTMLInputElement && !creating) el.focus();
    });
  });
</script>

<div class="relative">
  <!-- Loading overlay -->
  {#if creating}
    <div
      class="absolute inset-0 z-10 rounded-3xl bg-slate-950/40 backdrop-blur-sm ring-1 ring-white/10"
      role="status"
      aria-live="polite"
      aria-label="Generating your plan"
    >
      <div
        class="flex h-full flex-col items-center justify-center gap-3 px-6 text-center"
      >
        <div class="text-sm font-semibold text-slate-100">
          Generating your plan…
        </div>
        <div class="text-xs text-slate-300">
          Turning your goals into milestones and tasks
        </div>

        <div
          class="mt-4 h-2 w-full max-w-sm overflow-hidden rounded-full bg-white/10"
        >
          <div
            class="h-full w-1/3 animate-loading-bar rounded-full bg-white/40"
          ></div>
        </div>
      </div>
    </div>
  {/if}

  <Card id="create" class="bg-white/5 text-slate-100 ring-1 ring-white/10">
    <CardHeader>
      <CardTitle class="text-slate-100">Plan your project</CardTitle>
      <CardDescription class="text-slate-300">
        Give your project a title and describe a clear goal.
      </CardDescription>
    </CardHeader>

    <CardContent class="grid gap-4">
      <div class="grid gap-2">
        <Label for={idTitle} class="text-slate-200">Project Title</Label>
        <Input
          id={idTitle}
          class="bg-slate-950/40 text-slate-100 ring-1 ring-white/10 placeholder:text-slate-500"
          placeholder="e.g., Build a portfolio website"
          bind:value={title}
          disabled={creating}
        />
      </div>

      <div class="grid gap-2">
        <Label for={idGoal} class="text-slate-200">Goals</Label>
        <Textarea
          id={idGoal}
          class="bg-slate-950/40 text-slate-100 ring-1 ring-white/10 placeholder:text-slate-500"
          placeholder="e.g., I want to create a personal website to showcase my projects and skills."
          bind:value={goal_text}
          disabled={creating}
        ></Textarea>
      </div>

      <div class="grid gap-4 sm:grid-cols-2">
        <div class="grid gap-2">
          <Label for={idDeadline} class="text-slate-200">
            Deadline (optional)
          </Label>
          <Input
            id={idDeadline}
            class="bg-slate-950/40 text-slate-100 ring-1 ring-white/10 placeholder:text-slate-500"
            placeholder="e.g., 2 weeks"
            bind:value={deadline}
            disabled={creating}
          />
        </div>

        <div class="grid gap-2">
          <Label for={idHpw} class="text-slate-200">
            Hours per week (optional)
          </Label>
          <Input
            id={idHpw}
            type="number"
            min="0"
            step="1"
            class="bg-slate-950/40 text-slate-100 ring-1 ring-white/10 placeholder:text-slate-500"
            value={hours_per_week ?? ""}
            placeholder="e.g., 6"
            disabled={creating}
            oninput={(e) => {
              const n = (e.currentTarget as HTMLInputElement).valueAsNumber;
              hours_per_week = Number.isFinite(n) ? n : null;
            }}
          />
        </div>
      </div>

      <div class="grid gap-2">
        <Label for={idExp} class="text-slate-200">Experience level</Label>
        <select
          id={idExp}
          class="w-full rounded-xl bg-slate-950/40 px-3 py-2 text-sm text-slate-100 ring-1 ring-white/10"
          bind:value={experience_level}
          disabled={creating}
        >
          <option value="beginner">Beginner</option>
          <option value="intermediate">Intermediate</option>
          <option value="advanced">Advanced</option>
        </select>
        <div class="text-xs text-slate-400">
          Affects how detailed and challenging the plan is.
        </div>
      </div>

      {#if error}
        <div
          class="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-200"
          role="alert"
          aria-live="polite"
        >
          {error}
        </div>
      {/if}

      <Button
        class="w-full rounded-2xl disabled:opacity-100 disabled:cursor-not-allowed"
        onclick={() => onCreate()}
        disabled={creating}
      >
        {#if creating}
          <span
            class="mr-3 inline-block h-5 w-5 animate-spin rounded-full
              border-[3px] border-white/20
              border-t-white border-r-white/70"
            aria-hidden="true"
          ></span>
          Generating your plan…
        {:else}
          Generate project plan
        {/if}
      </Button>
    </CardContent>
  </Card>
</div>

<style>
  @keyframes loading-bar {
    0% {
      transform: translateX(-120%);
    }
    100% {
      transform: translateX(320%);
    }
  }
  :global(.animate-loading-bar) {
    animation: loading-bar 1.1s ease-in-out infinite;
  }
</style>
