<script lang="ts">
  import { Button, buttonVariants } from "$lib/components/ui/button";

  export let onCreate: () => void;
  export let onProjects: () => void;
</script>

<header class="sticky top-0 z-50">
  <div
    class="bg-slate-950/70 backdrop-blur supports-[backdrop-filter]:bg-slate-950/50"
  >
    <div
      class="mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-4"
    >
      <!-- Brand -->
      <button
        type="button"
        class="text-left font-black tracking-tight text-slate-100 hover:text-white"
        on:click={onCreate}
      >
        Project Planner
      </button>

      <nav class="flex items-center gap-2">
        <button
          type="button"
          class={buttonVariants({ variant: "ghost", size: "sm" })}
          on:click={onCreate}
        >
          Create
        </button>

        <Button
          type="button"
          variant="secondary"
          class="bg-white/5 ring-1 ring-white/10 hover:bg-white/10"
          onclick={onProjects}
        >
          Projects
        </Button>
      </nav>
    </div>

    <div class="h-px w-full bg-white/10"></div>
  </div>
</header>
