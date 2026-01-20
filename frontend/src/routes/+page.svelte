<script lang="ts">
    type Todo = {
        id: string;
        title: string;
        notes: string;
        status: "todo";
        estimate: "S" | "M" | "L";
        order: number;
    };

    let goal = "";
    let assistantText = "";
    let todos: Todo[] = [];
    let loading = false;

    async function generate() {
        loading = true;
        assistantText = "Generating todos...";
        todos = [];

        const response = await fetch("http://localhost:8000/plans/generate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                goal,
                constraints: { time_per_week: 6, deadline: "2 weeks" },
            }),
        });

        if (!response.ok) {
            const errorText = await response.text();
            assistantText = `Backend error ${response.status}: ${errorText}`;
            loading = false;
            return;
        }

        
    }
</script>

<div class="layout">
    <main>
        <h1>Goal → AI → ToDos</h1>
        <textarea bind:value={goal} placeholder="Describe a goal..."></textarea>
        <button on:click={generate} disabled={loading || !goal.trim()}>
            {loading ? "Generating..." : "Generate"}
        </button>

        {#if assistantText}
            <h2>AI Assistant:</h2>
            <p>{assistantText}</p>
        {/if}
    </main>

    <aside>
        <h2>ToDos</h2>
        {#if todos.length === 0}
            <p class="muted">No ToDos generated yet.</p>
        {:else}
            <ul>
                {#each todos as t (t.id)}
                    <li>
                        <input type="checkbox" />
                        <span>{t.title}</span>
                        <small>{t.estimate}</small>
                    </li>
                {/each}
            </ul>
        {/if}
    </aside>
</div>

<style>
    .layout {
        display: grid;
        grid-template-columns: 1fr 340px;
        gap: 16px;
        padding: 16px;
    }
    textarea {
        width: 100%;
        height: 110px;
        margin: 10px 0;
        padding: 10px;
    }
    aside {
        border-left: 1px solid #ddd;
        padding-left: 16px;
    }
    ul {
        list-style: none;
        padding: 0;
    }
    li {
        display: flex;
        gap: 8px;
        align-items: center;
        padding: 8px;
        border: 1px solid #eee;
        border-radius: 10px;
        margin: 8px 0;
    }
    .muted {
        opacity: 0.7;
    }
    small {
        margin-left: auto;
        opacity: 0.7;
    }
</style>
