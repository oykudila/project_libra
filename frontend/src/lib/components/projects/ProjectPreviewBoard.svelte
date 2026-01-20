<script lang="ts">
  import { goto } from "$app/navigation";

  import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
  } from "$lib/components/ui/card";
  import { Button } from "$lib/components/ui/button";

  import type {
    ProjectDetailResponse,
    ProposeMilestone,
    ProposeTask,
    TaskStatus,
  } from "$lib/api";

  import "./preview.css";

  type ColumnKey = TaskStatus;
  type PreviewCardTask = ProposeTask & { _tmpId: string };

  export let project: ProjectDetailResponse | null;

  export let previewPlan: {
    milestones: ProposeMilestone[];
    tasks: ProposeTask[];
  } | null;

  export let loading = false;
  export let error = "";
  export let applying = false;

  export let onApplyPreview: () => void;
  export let onDiscardPreview: () => void;

  const columns: { key: ColumnKey; title: string; hint: string }[] = [
    { key: "todo", title: "To Do", hint: "Queued up next" },
    { key: "in_progress", title: "In Progress", hint: "Currently working" },
    { key: "done", title: "Done", hint: "Completed items" },
  ];

  function boardTasks(
    col: ColumnKey,
  ): (PreviewCardTask | ProjectDetailResponse["tasks"][number])[] {
    if (previewPlan) {
      return previewPlan.tasks
        .filter((t) => t.status === col)
        .map((t, i) => ({ ...t, _tmpId: `${col}_${i}` }));
    }
    return (project?.tasks ?? []).filter((t) => t.status === col);
  }
</script>

<div class="preview-page">
  <!-- Top bar -->
  <div class="preview-topbar">
    <div class="min-w-0">
      <div class="preview-metaLabel">Project</div>

      {#if project}
        <h1 class="preview-title">{project.title}</h1>

        {#if project.deadline || typeof project.hours_per_week === "number"}
          <div class="preview-chips">
            {#if project.deadline}
              <span class="preview-chip">Deadline: {project.deadline}</span>
            {/if}
            {#if typeof project.hours_per_week === "number"}
              <span class="preview-chip">{project.hours_per_week} hrs/wk</span>
            {/if}
          </div>
        {/if}
      {:else}
        <h1 class="preview-title">Project</h1>
      {/if}
    </div>

    <div class="flex items-center gap-2">
      <Button variant="secondary" onclick={() => goto("/")}
        >← All projects</Button
      >
    </div>
  </div>

  <!-- Preview banner -->
  {#if previewPlan}
    <Card class="preview-banner">
      <CardHeader class="pb-3">
        <CardTitle class="preview-bannerTitle">Plan preview</CardTitle>
        <CardDescription class="preview-bannerDesc">
          Review the tasks below. Apply to save them to this project, or discard
          to go back.
        </CardDescription>
      </CardHeader>

      <CardContent
        class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"
      >
        <div class="preview-bannerFootnote">
          This preview is stored locally (sessionStorage) until you apply it.
        </div>

        <div class="flex items-center gap-2">
          <Button
            variant="secondary"
            onclick={onDiscardPreview}
            disabled={applying}
          >
            Discard
          </Button>
          <Button onclick={onApplyPreview} disabled={applying}>
            {applying ? "Applying…" : "Apply plan"}
          </Button>
        </div>
      </CardContent>
    </Card>
  {/if}

  <!-- States -->
  {#if loading}
    <Card class="preview-stateCard">
      <CardContent class="py-6 text-sm text-slate-300">Loading…</CardContent>
    </Card>
  {:else if error}
    <Card class="preview-errorCard">
      <CardContent
        class="py-4 text-sm text-red-200"
        role="alert"
        aria-live="polite"
      >
        {error}
      </CardContent>
    </Card>
  {:else if project}
    <!-- Board -->
    <div class="preview-board">
      {#each columns as col (col.key)}
        <Card class="preview-columnCard">
          <CardHeader class="pb-3">
            <div class="preview-columnHeaderRow">
              <div class="min-w-0">
                <CardTitle class="text-sm font-extrabold text-slate-100"
                  >{col.title}</CardTitle
                >
                <CardDescription class="text-xs">{col.hint}</CardDescription>
              </div>

              <div class="flex items-center gap-2">
                {#if previewPlan}
                  <span class="preview-badgePreview">Preview</span>
                {/if}
                <span class="preview-badge" title="Count"
                  >{boardTasks(col.key).length}</span
                >
              </div>
            </div>
          </CardHeader>

          <CardContent class="space-y-3">
            {#if boardTasks(col.key).length === 0}
              <div class="preview-empty">No tasks here yet.</div>
            {:else}
              {#each boardTasks(col.key) as t ("_tmpId" in t ? t._tmpId : t.id)}
                <div class="preview-taskCard">
                  <div class="flex items-start justify-between gap-3">
                    <div class="min-w-0">
                      <div class="preview-taskTitle">{t.title}</div>

                      {#if t.description}
                        <div class="preview-taskDesc line-clamp-2">
                          {t.description}
                        </div>
                      {/if}
                    </div>

                    {#if "estimate" in t && t.estimate}
                      <span class="preview-taskPill shrink-0" title="Estimate">
                        {t.estimate}
                      </span>
                    {/if}
                  </div>

                  <div class="preview-taskMetaRow">
                    {#if "due_date" in t && t.due_date}
                      <span class="preview-taskPill">Due: {t.due_date}</span>
                    {/if}

                    {#if previewPlan}
                      <span class="preview-taskPillPreview">Not saved yet</span>
                    {/if}
                  </div>
                </div>
              {/each}
            {/if}
          </CardContent>
        </Card>
      {/each}
    </div>
  {:else}
    <Card class="preview-stateCard">
      <CardContent class="py-6 text-sm text-slate-300">
        Project not found.
      </CardContent>
    </Card>
  {/if}
</div>
