<script lang="ts">
    import { onMount } from "svelte";
    import { dndzone } from "svelte-dnd-action";
    import {
        getProject,
        generatePlan,
        applyPlan,
        updateTask,
        deleteProject,
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

    let board = {
        todo: [] as TaskResponse[],
        doing: [] as TaskResponse[],
        done: [] as TaskResponse[],
    };

    function makeBoardFromProject() {
        const tasks = project?.tasks ?? [];
        const byStatus = {
            todo: [] as TaskResponse[],
            doing: [] as TaskResponse[],
            done: [] as TaskResponse[],
        };

        for (const t of tasks) {
            if (t.status === "doing") byStatus.doing.push(t);
            else if (t.status === "done") byStatus.done.push(t);
            else byStatus.todo.push(t);
        }

        byStatus.todo.sort(
            (a, b) => (a.order_index ?? 0) - (b.order_index ?? 0),
        );
        byStatus.doing.sort(
            (a, b) => (a.order_index ?? 0) - (b.order_index ?? 0),
        );
        byStatus.done.sort(
            (a, b) => (a.order_index ?? 0) - (b.order_index ?? 0),
        );

        board = byStatus;
    }

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
            makeBoardFromProject();
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
            makeBoardFromProject();
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
            makeBoardFromProject();
        } catch (e: any) {
            task.status = old;
            alert(e?.message ?? "Failed to update task");
        }
    }

    async function persistColumn(
        status: "todo" | "doing" | "done",
        items: TaskResponse[],
    ) {
        items.forEach((t, idx) => {
            t.status = status;
            t.order_index = idx;
        });

        await Promise.all(
            items.map((t, idx) =>
                updateTask(t.id, { status, order_index: idx }),
            ),
        );
    }

    async function persistAllColumns() {
        await Promise.all([
            persistColumn("todo", board.todo),
            persistColumn("doing", board.doing),
            persistColumn("done", board.done),
        ]);
    }

    function rebuildProjectTasksFromBoard() {
        if (!project) return;
        const merged = [...board.todo, ...board.doing, ...board.done];
        project.tasks = merged;
    }

    async function onDeleteProject() {
        if (!project) return;
        const ok = confirm(
            "Delete this project? This will delete all its tasks.",
        );
        if (!ok) return;

        try {
            await deleteProject(project.id);
            goto("/");
        } catch (e: any) {
            alert(e?.message ?? "Failed to delete project");
        }
    }

    const COLS: Array<{ key: "todo" | "doing" | "done"; title: string }> = [
        { key: "todo", title: "Todo" },
        { key: "doing", title: "Doing" },
        { key: "done", title: "Done" },
    ];
</script>

<main class="page">
    <header class="topbar">
        <div class="titleblock">
            <h1 class="h1">{project ? project.title : "Project"}</h1>
            {#if project}
                <div class="subtitle">{project.goal_text}</div>
            {/if}
        </div>

        <div class="topactions">
            {#if project}
                <button
                    class="btn danger"
                    on:click={onDeleteProject}
                    title="Delete project"
                >
                    Delete
                </button>
            {/if}

            <button class="btn" on:click={() => goto("/")}>← Back</button>
        </div>
    </header>

    {#if loading}
        <div class="muted">Loading…</div>
    {:else if error}
        <div class="error">{error}</div>
    {:else if project}
        <div class="layout">
            <!-- Planner -->
            <section class="card">
                <div class="cardhead">
                    <h2 class="h2">AI Planner</h2>
                    {#if aiLoading}
                        <div class="chip">
                            <span class="spinner"></span>
                            Generating…
                        </div>
                    {/if}
                </div>

                <div class="form">
                    <label class="field">
                        <div class="label">Deadline</div>
                        <input
                            class="input"
                            bind:value={deadline}
                            placeholder="YYYY-MM-DD or 'no deadline'"
                        />
                    </label>

                    <label class="field">
                        <div class="label">Hours/week</div>
                        <input
                            class="input"
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
                        />
                    </label>

                    <label class="field">
                        <div class="label">Experience level</div>
                        <select class="input" bind:value={experience_level}>
                            <option value="">(choose)</option>
                            <option value="beginner">Beginner</option>
                            <option value="intermediate">Intermediate</option>
                            <option value="advanced">Advanced</option>
                        </select>
                    </label>

                    <label class="field">
                        <div class="label">Constraints (optional)</div>
                        <textarea
                            class="input"
                            bind:value={constraints}
                            rows="3"
                            placeholder="e.g., busy weekdays, no budget..."
                        ></textarea>
                    </label>

                    <label class="field">
                        <div class="label">Detail level</div>
                        <select class="input" bind:value={detail_level}>
                            <option value="simple">Simple</option>
                            <option value="detailed">Detailed</option>
                        </select>
                    </label>

                    <button
                        class="btn primary"
                        on:click={onGenerate}
                        disabled={aiLoading}
                    >
                        {aiLoading ? "Generating…" : "Generate plan"}
                    </button>

                    {#if aiError}
                        <div class="error">{aiError}</div>
                    {/if}

                    {#if aiResult?.type === "questions"}
                        <div class="divider"></div>
                        <div class="preview">
                            <div class="previewTitle">
                                Answer these to improve the plan
                            </div>
                            <ul class="list">
                                {#each aiResult.questions as q}
                                    <li>{q.question}</li>
                                {/each}
                            </ul>
                            <div class="muted small">
                                Fill the fields above, then click “Generate
                                plan” again.
                            </div>
                        </div>
                    {/if}

                    {#if aiResult?.type === "plan"}
                        <div class="divider"></div>
                        <div class="preview">
                            <div class="previewTitle">Preview</div>

                            <div class="muted small">Milestones</div>
                            <ol class="list">
                                {#each aiResult.milestones as m}
                                    <li>
                                        <div class="bold">{m.title}</div>
                                        {#if m.description}
                                            <div class="muted small">
                                                {m.description}
                                            </div>
                                        {/if}
                                    </li>
                                {/each}
                            </ol>

                            <div class="muted small">Tasks</div>
                            <ul class="list">
                                {#each aiResult.tasks as t}
                                    <li>{t.title}</li>
                                {/each}
                            </ul>

                            <button
                                class="btn primary"
                                on:click={onApply}
                                disabled={aiLoading}
                            >
                                {aiLoading
                                    ? "Applying…"
                                    : "Apply plan to project"}
                            </button>

                            <div class="muted small">
                                Applying will replace the existing tasks for
                                this project.
                            </div>
                        </div>
                    {/if}
                </div>
            </section>

            <!-- Board -->
            <section class="card">
                <div class="cardhead">
                    <h2 class="h2">Task Board</h2>
                    <div class="muted small">
                        Drag tasks to reorder or move columns.
                    </div>
                </div>

                <div class="board">
                    {#each COLS as col (col.key)}
                        <div class="col">
                            <div class="colHead">
                                <div class="colTitle">{col.title}</div>
                                <div class="count">
                                    {board[col.key].length}
                                </div>
                            </div>

                            <div
                                class="dropzone"
                                use:dndzone={{
                                    items: board[col.key],
                                    flipDurationMs: 150,
                                    type: "kanban",
                                }}
                                on:consider={(e) => {
                                    // Live update while dragging (prevents disappearing cards)
                                    board = {
                                        ...board,
                                        [col.key]: e.detail.items,
                                    };
                                }}
                                on:finalize={(e) => {
                                    // Final state after drop
                                    board = {
                                        ...board,
                                        [col.key]: e.detail.items,
                                    };

                                    // Persist AFTER UI updates so dragging feels smooth
                                    void (async () => {
                                        try {
                                            await persistAllColumns();
                                            rebuildProjectTasksFromBoard();
                                        } catch (err: any) {
                                            alert(
                                                err?.message ??
                                                    "Failed to save drag/drop changes",
                                            );
                                            await load(); // revert to server state
                                        }
                                    })();
                                }}
                            >
                                {#if board[col.key].length === 0}
                                    <div class="empty">No tasks.</div>
                                {/if}

                                {#each board[col.key] as task (task.id)}
                                    <div class="task">
                                        <div class="taskTop">
                                            <div class="taskTitle">
                                                {task.title}
                                            </div>

                                            {#if task.estimate}
                                                <div
                                                    class="badge"
                                                    title="Size estimate"
                                                >
                                                    {task.estimate}
                                                </div>
                                            {/if}
                                        </div>

                                        {#if task.description}
                                            <div class="taskDesc">
                                                {task.description}
                                            </div>
                                        {/if}

                                        <div class="taskActions">
                                            {#if task.status !== "todo"}
                                                <button
                                                    class="btn tiny"
                                                    on:click={() =>
                                                        setStatus(task, "todo")}
                                                >
                                                    Todo
                                                </button>
                                            {/if}
                                            {#if task.status !== "doing"}
                                                <button
                                                    class="btn tiny"
                                                    on:click={() =>
                                                        setStatus(
                                                            task,
                                                            "doing",
                                                        )}
                                                >
                                                    Doing
                                                </button>
                                            {/if}
                                            {#if task.status !== "done"}
                                                <button
                                                    class="btn tiny"
                                                    on:click={() =>
                                                        setStatus(task, "done")}
                                                >
                                                    Done
                                                </button>
                                            {/if}
                                        </div>
                                    </div>
                                {/each}
                            </div>
                        </div>
                    {/each}
                </div>
            </section>
        </div>
    {/if}
</main>

<style>
    /* clean, modern UI without Tailwind */

    .page {
        max-width: 1200px;
        margin: 0 auto;
        padding: 24px;
        color: #0f172a;
        font-family:
            ui-sans-serif,
            system-ui,
            -apple-system,
            Segoe UI,
            Roboto,
            Arial,
            "Apple Color Emoji",
            "Segoe UI Emoji";
    }

    .topbar {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 12px;
        margin-bottom: 16px;
    }

    .titleblock {
        min-width: 0;
    }

    .h1 {
        margin: 0 0 6px;
        font-size: 28px;
        letter-spacing: -0.02em;
    }

    .subtitle {
        opacity: 0.85;
        line-height: 1.35;
    }

    .topactions {
        display: flex;
        gap: 10px;
        align-items: center;
    }

    .layout {
        display: grid;
        grid-template-columns: 380px 1fr;
        gap: 16px;
        align-items: start;
    }

    .card {
        border: 1px solid #e5e7eb;
        background: white;
        border-radius: 16px;
        padding: 16px;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06);
    }

    .cardhead {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 12px;
        margin-bottom: 12px;
    }

    .h2 {
        margin: 0;
        font-size: 18px;
        letter-spacing: -0.01em;
    }

    .muted {
        color: #475569;
    }
    .small {
        font-size: 12px;
    }
    .bold {
        font-weight: 700;
    }
    .error {
        color: #b00020;
    }

    .chip {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 12px;
        color: #0f172a;
        background: #f1f5f9;
        border: 1px solid #e2e8f0;
        padding: 6px 10px;
        border-radius: 999px;
    }

    .spinner {
        width: 14px;
        height: 14px;
        border-radius: 999px;
        border: 2px solid #cbd5e1;
        border-top-color: #0f172a;
        animation: spin 0.9s linear infinite;
    }

    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }

    .form {
        display: grid;
        gap: 10px;
    }

    .field .label {
        font-size: 12px;
        color: #475569;
        margin-bottom: 6px;
    }

    .input {
        width: 100%;
        padding: 10px 12px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        outline: none;
        background: #ffffff;
        transition:
            border-color 120ms ease,
            box-shadow 120ms ease;
    }
    .input:focus {
        border-color: #94a3b8;
        box-shadow: 0 0 0 4px rgba(148, 163, 184, 0.25);
    }

    .btn {
        padding: 10px 12px;
        border-radius: 12px;
        border: 1px solid #0f172a;
        background: white;
        cursor: pointer;
        transition:
            transform 80ms ease,
            opacity 80ms ease;
        user-select: none;
    }
    .btn:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }
    .btn:active {
        transform: translateY(1px);
    }
    .btn.primary {
        background: #0f172a;
        color: white;
    }
    .btn.danger {
        border-color: #ef4444;
        color: #ef4444;
    }
    .btn.tiny {
        padding: 6px 10px;
        border-radius: 999px;
        font-size: 12px;
    }

    .divider {
        height: 1px;
        background: #e5e7eb;
        margin: 6px 0;
    }

    .previewTitle {
        font-weight: 800;
        margin-bottom: 8px;
    }
    .list {
        margin: 8px 0 12px;
        padding-left: 18px;
        color: #0f172a;
    }
    .list li {
        margin: 6px 0;
    }

    .board {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
    }

    .col {
        border: 1px solid #eef2f7;
        border-radius: 16px;
        background: #fafafa;
        overflow: hidden;
    }

    .colHead {
        padding: 12px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #f8fafc;
        border-bottom: 1px solid #eef2f7;
    }

    .colTitle {
        font-weight: 800;
    }

    .count {
        font-size: 12px;
        color: #475569;
        border: 1px solid #e2e8f0;
        background: white;
        padding: 3px 8px;
        border-radius: 999px;
    }

    .dropzone {
        padding: 12px;
        display: grid;
        gap: 10px;
        min-height: 120px;
    }

    .empty {
        color: #64748b;
        font-size: 13px;
        padding: 10px;
        border: 1px dashed #cbd5e1;
        border-radius: 12px;
        background: white;
    }

    .task {
        cursor: grab;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        background: white;
        padding: 10px;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06);
    }
    .task:active {
        cursor: grabbing;
    }

    .taskTop {
        display: flex;
        align-items: flex-start;
        gap: 10px;
    }

    .taskTitle {
        font-weight: 800;
        line-height: 1.2;
        flex: 1;
        min-width: 0;
    }

    .badge {
        flex: none;
        font-size: 12px;
        font-weight: 800;
        color: #0f172a;
        background: #f1f5f9;
        border: 1px solid #e2e8f0;
        padding: 2px 8px;
        border-radius: 999px;
    }

    .taskDesc {
        margin-top: 6px;
        color: #475569;
        font-size: 13px;
        line-height: 1.35;
    }

    .taskActions {
        margin-top: 10px;
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }

    @media (max-width: 980px) {
        .layout {
            grid-template-columns: 1fr;
        }
        .board {
            grid-template-columns: 1fr;
        }
    }
</style>
