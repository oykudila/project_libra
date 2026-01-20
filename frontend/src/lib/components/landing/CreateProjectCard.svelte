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

  export let creating = false;
  export let error = "";
  export let onCreate: () => void | Promise<void>;

  const idTitle = "lp_title";
  const idGoal = "lp_goal";
  const idDeadline = "lp_deadline";
  const idHpw = "lp_hpw";

  onMount(() => {
    requestAnimationFrame(() => {
      (document.getElementById(idTitle) as HTMLInputElement | null)?.focus();
    });
  });
</script>

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
      />
    </div>

    <div class="grid gap-2">
      <Label for={idGoal} class="text-slate-200">Goal</Label>
      <Textarea
        id={idGoal}
        class="bg-slate-950/40 text-slate-100 ring-1 ring-white/10 placeholder:text-slate-500"
        placeholder="e.g., I want to create a personal website to showcase my projects and skills."
        bind:value={goal_text}
      />
    </div>

    <div class="grid gap-4 sm:grid-cols-2">
      <div class="grid gap-2">
        <Label for={idDeadline} class="text-slate-200"
          >Deadline (optional)</Label
        >
        <Input
          id={idDeadline}
          class="bg-slate-950/40 text-slate-100 ring-1 ring-white/10 placeholder:text-slate-500"
          placeholder="e.g., 2 weeks"
          bind:value={deadline}
        />
      </div>

      <div class="grid gap-2">
        <Label for={idHpw} class="text-slate-200"
          >Hours per week (optional)</Label
        >
        <Input
          id={idHpw}
          type="number"
          min="0"
          step="1"
          class="bg-slate-950/40 text-slate-100 ring-1 ring-white/10 placeholder:text-slate-500"
          value={hours_per_week ?? ""}
          placeholder="e.g., 6"
          oninput={(e: Event) => {
            const n = (e.currentTarget as HTMLInputElement).valueAsNumber;
            hours_per_week = Number.isFinite(n) ? n : null;
          }}
        />
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
      class="w-full rounded-2xl"
      onclick={() => onCreate()}
      disabled={creating}
    >
      {#if creating}
        <span
          class="mr-2 inline-block h-4 w-4 animate-spin rounded-full
                 border-2 border-slate-200/30 border-t-slate-200"
        ></span>
        Generating your plan...
      {:else}
        Generate project plan
      {/if}
    </Button>
  </CardContent>
</Card>
