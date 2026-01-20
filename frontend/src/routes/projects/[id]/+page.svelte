<script lang="ts">
    import { onMount } from "svelte";
    import {
        getProject,
        generatePlan,
        applyPlan,
        updateTask,
        type ProjectDetailResponse,
        type TaskResponse,
        type GeneratePlanResponse,
    } from "$lib/api";
    import { page } from "$app/state";
    import { goto } from "$app/navigation";

    let projectId = 0;
    $: projectId = Number(page.params.id ?? 0);

    let project: ProjectDetailResponse | null = null;
    let loading = true;
    let error = "";

    let aiLoading = false;
    let aiError = "";
    let aiResult: GeneratePlanResponse | null = null;

    let deadline = "";
    let hours_per_week: number | null = null;
    let experience_level: "beginner" | "intermediate" | "advanced" | "" = "";
    let constraints = "";
    let detail_level: "simple" | "detailed" = "detailed";

    async function load() {
        if (!Number.isFinite(projectId) || projectId <= 0) return;

        loading = true;
        error = "";
        try {
            project = await getProject(projectId);
            deadline = project.deadline ?? "";
            hours_per_week =
                typeof project.hours_per_week === "number" &&
                Number.isFinite(project.hours_per_week)
                    ? project.hours_per_week
                    : null;
        } catch (e: any) {
            error = e?.message ?? "Failed to load project";
            project = null;
        } finally {
            loading = false;
        }
    }

    let lastLoadedProjectId: number | null = null;
    onMount(() => {
        lastLoadedProjectId = projectId;
        load();
    });

    $: if (projectId !== lastLoadedProjectId) {
        lastLoadedProjectId = projectId;
        load();
    }

    async function onGenerate() {
        if (!project) return;

        aiLoading = true;
        aiError = "";
        aiResult = null;

        const hpw =
            typeof hours_per_week === "number" &&
            Number.isFinite(hours_per_week) &&
            Number.isInteger(hours_per_week) &&
            hours_per_week >= 0
                ? hours_per_week
                : hours_per_week === null
                  ? null
                  : null;

        try {
            aiResult = await generatePlan(project.id, {
                goal_text: project.goal_text,
                deadline: deadline.trim() ? deadline.trim() : null,
                hours_per_week: hpw,
                experience_level: experience_level || null,
                constraints: constraints.trim() ? constraints.trim() : null,
                detail_level,
            });
        } catch (e: unknown) {
            aiError = error =
                e instanceof Error ? e.message : "Failed to generate plan";
        } finally {
            aiLoading = false;
        }
    }

    async function onApply() {
        if (!project || !aiResult || aiResult.type !== "plan") return;

        aiLoading = true;
        aiError = "";

        try {
            project = await applyPlan(project.id, {
                milestones: aiResult.milestones,
                tasks: aiResult.tasks,
            });
            aiResult = null;
        } catch (e: unknown) {
            aiError = error =
                e instanceof Error ? e.message : "Failed to apply plan";
        } finally {
            aiLoading = false;
        }
    }

    async function setStatus(
        task: TaskResponse,
        status: TaskResponse["status"],
    ) {
        if (!project) return;

        const old = task.status;
        task.status = status;

        try {
            await updateTask(task.id, { status });
        } catch (e: any) {
            task.status = old;
            alert(e?.message ?? "Failed to update task");
        }
    }

    $: backlog =
        project?.tasks?.filter((t: TaskResponse) => t.status === "backlog") ??
        [];
    $: doing =
        project?.tasks?.filter((t: TaskResponse) => t.status === "doing") ?? [];
    $: done =
        project?.tasks?.filter((t: TaskResponse) => t.status === "done") ?? [];
</script>

<main style="max-width: 1200px; margin: 0 auto; padding: 24px;">
    <div
        style="display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-bottom: 16px;"
    >
        <div>
            <h1 style="margin: 0 0 6px;">
                {project ? project.title : "Project"}
            </h1>
            {#if project}
                <div style="opacity: 0.8;">{project.goal_text}</div>
            {/if}
        </div>
        <button
            on:click={() => goto("/")}
            style="padding: 8px 12px; border-radius: 10px; border: 1px solid #333; cursor: pointer;"
        >
            ← Back to projects
        </button>
    </div>

    {#if loading}
        <div>Loading…</div>
    {:else if error}
        <div style="color: #b00020;">{error}</div>
    {:else if project}
        <div
            style="display: grid; grid-template-columns: 380px 1fr; gap: 16px; align-items: start;"
        >
            <!-- Planner -->
            <section
                style="border: 1px solid #ddd; border-radius: 12px; padding: 16px;"
            >
                <h2 style="margin: 0 0 12px; font-size: 18px;">AI Planner</h2>

                <div style="display: grid; gap: 10px;">
                    <label>
                        <div style="font-size: 12px; opacity: 0.8;">
                            Deadline
                        </div>
                        <input
                            bind:value={deadline}
                            placeholder="YYYY-MM-DD or 'no deadline'"
                            style="width: 100%; padding: 10px;"
                        />
                    </label>

                    <label>
                        <div style="font-size: 12px; opacity: 0.8;">
                            Hours/week
                        </div>
                        <input
                            type="number"
                            min="1"
                            step="1"
                            value={hours_per_week ?? ""}
                            on:input={(e) => {
                                const n = (e.currentTarget as HTMLInputElement)
                                    .valueAsNumber;
                                hours_per_week = Number.isFinite(n) ? n : null;
                            }}
                            placeholder="e.g., 5"
                            style="width: 100%; padding: 10px;"
                        />
                    </label>

                    <label>
                        <div style="font-size: 12px; opacity: 0.8;">
                            Experience level
                        </div>
                        <select
                            bind:value={experience_level}
                            style="width: 100%; padding: 10px;"
                        >
                            <option value="">(choose)</option>
                            <option value="beginner">Beginner</option>
                            <option value="intermediate">Intermediate</option>
                            <option value="advanced">Advanced</option>
                        </select>
                    </label>

                    <label>
                        <div style="font-size: 12px; opacity: 0.8;">
                            Constraints (optional)
                        </div>
                        <textarea
                            bind:value={constraints}
                            rows="3"
                            placeholder="e.g., busy weekdays, no budget..."
                            style="width: 100%; padding: 10px;"
                        ></textarea>
                    </label>

                    <label>
                        <div style="font-size: 12px; opacity: 0.8;">
                            Detail level
                        </div>
                        <select
                            bind:value={detail_level}
                            style="width: 100%; padding: 10px;"
                        >
                            <option value="simple">Simple</option>
                            <option value="detailed">Detailed</option>
                        </select>
                    </label>

                    <button
                        on:click={onGenerate}
                        disabled={aiLoading}
                        style="padding: 10px 14px; border-radius: 10px; border: 1px solid #333; cursor: pointer;"
                    >
                        {aiLoading ? "Generating…" : "Generate plan"}
                    </button>

                    {#if aiError}
                        <div style="color: #b00020;">{aiError}</div>
                    {/if}

                    {#if aiResult?.type === "questions"}
                        <div
                            style="border-top: 1px solid #eee; padding-top: 12px;"
                        >
                            <div style="font-weight: 600; margin-bottom: 6px;">
                                Answer these to improve the plan:
                            </div>
                            <ul style="margin: 0; padding-left: 18px;">
                                {#each aiResult.questions as q}
                                    <li style="margin: 6px 0;">{q.question}</li>
                                {/each}
                            </ul>
                            <div
                                style="opacity: 0.8; font-size: 13px; margin-top: 8px;"
                            >
                                Fill the fields above, then click “Generate
                                plan” again.
                            </div>
                        </div>
                    {/if}

                    {#if aiResult?.type === "plan"}
                        <div
                            style="border-top: 1px solid #eee; padding-top: 12px;"
                        >
                            <div style="font-weight: 600; margin-bottom: 8px;">
                                Preview
                            </div>

                            <div
                                style="font-size: 13px; opacity: 0.85; margin-bottom: 6px;"
                            >
                                Milestones
                            </div>
                            <ol style="margin: 0 0 12px; padding-left: 18px;">
                                {#each aiResult.milestones as m}
                                    <li style="margin: 6px 0;">
                                        <div style="font-weight: 600;">
                                            {m.title}
                                        </div>
                                        {#if m.description}<div
                                                style="opacity: 0.8; font-size: 13px;"
                                            >
                                                {m.description}
                                            </div>{/if}
                                    </li>
                                {/each}
                            </ol>

                            <div
                                style="font-size: 13px; opacity: 0.85; margin-bottom: 6px;"
                            >
                                Tasks
                            </div>
                            <ul style="margin: 0; padding-left: 18px;">
                                {#each aiResult.tasks as t}
                                    <li style="margin: 6px 0;">{t.title}</li>
                                {/each}
                            </ul>

                            <button
                                on:click={onApply}
                                disabled={aiLoading}
                                style="margin-top: 12px; padding: 10px 14px; border-radius: 10px; border: 1px solid #333; cursor: pointer;"
                            >
                                {aiLoading
                                    ? "Applying…"
                                    : "Apply plan to project"}
                            </button>

                            <div
                                style="opacity: 0.8; font-size: 12px; margin-top: 8px;"
                            >
                                Applying will replace the existing tasks for
                                this project.
                            </div>
                        </div>
                    {/if}
                </div>
            </section>

            <!-- Board -->
            <section
                style="border: 1px solid #ddd; border-radius: 12px; padding: 16px;"
            >
                <h2 style="margin: 0 0 12px; font-size: 18px;">Task Board</h2>

                <div
                    style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px;"
                >
                    {#each [{ title: "Backlog", items: backlog }, { title: "Doing", items: doing }, { title: "Done", items: done }] as col}
                        <div
                            style="border: 1px solid #eee; border-radius: 12px; padding: 12px;"
                        >
                            <div style="font-weight: 700; margin-bottom: 10px;">
                                {col.title}
                                <span style="opacity: 0.7; font-weight: 400;"
                                    >({col.items.length})</span
                                >
                            </div>

                            {#if col.items.length === 0}
                                <div style="opacity: 0.7; font-size: 13px;">
                                    No tasks.
                                </div>
                            {:else}
                                <div style="display: grid; gap: 10px;">
                                    {#each col.items as task}
                                        <div
                                            style="border: 1px solid #ddd; border-radius: 12px; padding: 10px;"
                                        >
                                            <div style="font-weight: 600;">
                                                {task.title}
                                            </div>
                                            {#if task.description}
                                                <div
                                                    style="opacity: 0.8; font-size: 13px; margin-top: 4px;"
                                                >
                                                    {task.description}
                                                </div>
                                            {/if}

                                            <div
                                                style="display: flex; gap: 8px; margin-top: 10px; flex-wrap: wrap;"
                                            >
                                                {#if task.status !== "backlog"}
                                                    <button
                                                        on:click={() =>
                                                            setStatus(
                                                                task,
                                                                "backlog",
                                                            )}
                                                        style="padding: 6px 10px; border-radius: 10px; border: 1px solid #333; cursor: pointer;"
                                                    >
                                                        Backlog
                                                    </button>
                                                {/if}
                                                {#if task.status !== "doing"}
                                                    <button
                                                        on:click={() =>
                                                            setStatus(
                                                                task,
                                                                "doing",
                                                            )}
                                                        style="padding: 6px 10px; border-radius: 10px; border: 1px solid #333; cursor: pointer;"
                                                    >
                                                        Doing
                                                    </button>
                                                {/if}
                                                {#if task.status !== "done"}
                                                    <button
                                                        on:click={() =>
                                                            setStatus(
                                                                task,
                                                                "done",
                                                            )}
                                                        style="padding: 6px 10px; border-radius: 10px; border: 1px solid #333; cursor: pointer;"
                                                    >
                                                        Done
                                                    </button>
                                                {/if}
                                            </div>
                                        </div>
                                    {/each}
                                </div>
                            {/if}
                        </div>
                    {/each}
                </div>

                <div style="opacity: 0.75; font-size: 12px; margin-top: 12px;">
                    Tip: This board is persisted in the database—refreshing
                    won’t erase it anymore.
                </div>
            </section>
        </div>
    {/if}
</main>
