<script lang="ts">
  import { onMount } from "svelte";
  import { page } from "$app/state";
  import { goto } from "$app/navigation";

  import {
    getProject,
    applyPlan,
    type ProjectDetailResponse,
    type GeneratePlanResponse,
    type ProposeTask,
    type ProposeMilestone,
    type TaskStatus,
  } from "$lib/api";

  import ProjectPreviewBoard from "$lib/components/projects/ProjectPreviewBoard.svelte";

  let projectId = 0;
  let project: ProjectDetailResponse | null = null;

  let previewPlan: {
    milestones: ProposeMilestone[];
    tasks: ProposeTask[];
  } | null = null;

  let loading = false;
  let error = "";
  let applying = false;

  function getId() {
    const n = Number(page.params.id);
    return Number.isFinite(n) ? n : 0;
  }

  async function refresh() {
    loading = true;
    error = "";
    try {
      project = await getProject(projectId);
    } catch (e: unknown) {
      error = e instanceof Error ? e.message : "Failed to load project";
      project = null;
    } finally {
      loading = false;
    }
  }

  function loadPreviewIfAny() {
    const isPreview = page.url.searchParams.get("preview") === "1";
    if (!isPreview) return;

    const raw = sessionStorage.getItem(`plan_preview_${projectId}`);
    if (!raw) return;

    try {
      const parsed = JSON.parse(raw) as GeneratePlanResponse;
      if (parsed.type === "plan") {
        previewPlan = { milestones: parsed.milestones, tasks: parsed.tasks };
      }
    } catch {
      // ignore
    }
  }

  onMount(async () => {
    projectId = getId();
    await refresh();
    loadPreviewIfAny();
  });

  async function applyPreview() {
    if (!previewPlan) return;
    applying = true;
    error = "";
    try {
      const updated = await applyPlan(projectId, {
        milestones: previewPlan.milestones,
        tasks: previewPlan.tasks,
      });

      project = updated;
      sessionStorage.removeItem(`plan_preview_${projectId}`);
      previewPlan = null;

      goto(`/projects/${projectId}`, { replaceState: true });
    } catch (e: unknown) {
      error = e instanceof Error ? e.message : "Failed to apply plan";
    } finally {
      applying = false;
    }
  }

  function discardPreview() {
    sessionStorage.removeItem(`plan_preview_${projectId}`);
    previewPlan = null;
    goto(`/projects/${projectId}`, { replaceState: true });
  }
</script>

<ProjectPreviewBoard
  {project}
  {previewPlan}
  {loading}
  {error}
  {applying}
  onApplyPreview={applyPreview}
  onDiscardPreview={discardPreview}
/>
