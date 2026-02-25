<script>
  import { getMixes, selectMix } from '$lib/stores/mixer.svelte.js'

  let mixes = $derived(getMixes())
</script>

<div class="min-h-screen max-w-lg mx-auto p-4 flex flex-col gap-4">
  <h1 class="text-xl font-bold text-neutral-200">Select your mix</h1>

  {#if mixes.length > 0}
    <div class="flex flex-col gap-2">
      {#each mixes as mix (mix.index)}
        <button
          type="button"
          onclick={() => selectMix(mix.index)}
          class="flex items-center gap-3 p-4 rounded-lg bg-neutral-900 active:bg-neutral-800 transition-colors text-left"
        >
          <div class="w-4 h-4 rounded-full shrink-0" style="background-color: {mix.color}"></div>
          <span class="text-lg text-neutral-200 font-medium">{mix.name}</span>
          <span class="ml-auto text-sm text-neutral-500">{mix.track_count} ch</span>
        </button>
      {/each}
    </div>
  {:else}
    <div class="text-neutral-500 text-sm text-center py-8 px-4">
      <p class="mb-4">No monitor mixes found.</p>
      <p>Ensure Ableton Live is running with AbletonOSC enabled and your project has group tracks for each monitor mix.</p>
    </div>
  {/if}
</div>
