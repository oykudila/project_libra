<script lang="ts">
    import { onMount } from "svelte";
    import {
        createProject,
        listProjects,
        type ProjectResponse,
    } from "$lib/api";
    import { goto } from "$app/navigation";

    let projects: ProjectResponse[] = [];
    let loading = false;
    let creating = false;
    let error = "";

    let title = "";
    let goal_text = "";
    let deadline = "";
    let hours_per_week: number | null = null;

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

    async function onCreate() {
        error = "";

        const t = title.trim();
        const g = goal_text.trim();
        const d = deadline.trim() ? deadline.trim() : null;

        const hpw = parseOptionalInt(hours_per_week);
        if (hours_per_week.trim() && hpw === null) {
            error = "Hours per week must be a non-negative whole number.";
            return;
        }

        if (!t || !g) {
            error = "Title and goal are required.";
            return;
        }

        creating = true;
        try {
            const p = await createProject({
                title: t,
                goal_text: g,
                deadline: d,
                hours_per_week: hpw,
            });

            title = "";
            goal_text = "";
            deadline = "";
            hours_per_week = "";

            await goto(`/projects/${p.id}`);
        } catch (e: unknown) {
            error = e instanceof Error ? e.message : "Failed to create project";
        } finally {
            creating = false;
        }
    }
    onMount(refresh);
</script>

<main style="max-width: 1000px; margin: 0 auto; padding: 24px;">
    <h1 style="margin: 0 0 8px;">Projects</h1>
    <p style="margin: 0 0 16px; opacity: 0.8;">
        Create a project, generate a plan with AI, then track tasks on a board.
    </p>

    <section
        style="border: 1px solid #ddd; border-radius: 12px; padding: 16px; margin-bottom: 16px;"
    >
        <h2 style="margin: 0 0 12px; font-size: 18px;">New project</h2>

        {#if error}
            <div style="margin-bottom: 12px; color: #b00020;">{error}</div>
        {/if}

        <form
            on:submit|preventDefault={onCreate}
            style="display: grid; gap: 10px;"
        >
            <label>
                <div style="font-size: 12px; opacity: 0.8;">Title</div>
                <input
                    bind:value={title}
                    placeholder="e.g., Learn Svelte and build a portfolio"
                    style="width: 100%; padding: 10px;"
                />
            </label>

            <label>
                <div style="font-size: 12px; opacity: 0.8;">Goal</div>
                <textarea
                    bind:value={goal_text}
                    rows="3"
                    placeholder="Describe your high-level goal..."
                    style="width: 100%; padding: 10px;"
                ></textarea>
            </label>

            <div
                style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;"
            >
                <label>
                    <div style="font-size: 12px; opacity: 0.8;">
                        Deadline (optional)
                    </div>
                    <input
                        bind:value={deadline}
                        placeholder="YYYY-MM-DD or 'no deadline'"
                        style="width: 100%; padding: 10px;"
                    />
                </label>

                <label>
                    <div style="font-size: 12px; opacity: 0.8;">
                        Hours/week (optional)
                    </div>
                    <input
                        bind:value={hours_per_week}
                        inputmode="numeric"
                        pattern="[0-9]*"
                        placeholder="e.g., 5"
                        style="width: 100%; padding: 10px;"
                    />
                </label>
            </div>

            <button
                type="submit"
                disabled={creating || loading}
                style="padding: 10px 14px; border-radius: 10px; border: 1px solid #333; cursor: pointer; opacity: {creating ||
                loading
                    ? 0.6
                    : 1};"
            >
                {#if creating}
                    Creating…
                {:else}
                    Create project
                {/if}
            </button>
        </form>
    </section>

    <section
        style="border: 1px solid #ddd; border-radius: 12px; padding: 16px;"
    >
        <h2 style="margin: 0 0 12px; font-size: 18px;">Your projects</h2>

        {#if loading}
            <div>Loading…</div>
        {:else if projects.length === 0}
            <div style="opacity: 0.8;">No projects yet.</div>
        {:else}
            <ul
                style="list-style: none; padding: 0; margin: 0; display: grid; gap: 10px;"
            >
                {#each projects as p}
                    <li
                        style="border: 1px solid #eee; border-radius: 12px; padding: 12px;"
                    >
                        <div
                            style="display: flex; justify-content: space-between; gap: 12px; align-items: center;"
                        >
                            <div style="min-width: 0;">
                                <div style="font-weight: 600;">{p.title}</div>
                                <div
                                    style="opacity: 0.8; font-size: 13px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;"
                                >
                                    {p.goal_text}
                                </div>
                            </div>
                            <button
                                type="button"
                                on:click={() => goto(`/projects/${p.id}`)}
                                style="padding: 8px 12px; border-radius: 10px; border: 1px solid #333; cursor: pointer;"
                            >
                                Open
                            </button>
                        </div>
                    </li>
                {/each}
            </ul>
        {/if}
    </section>
</main>
