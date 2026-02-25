<script>
  import MasterOutput from './MasterOutput.svelte'
  import ChannelStrip from './ChannelStrip.svelte'
  import { getTracks, getMaster, goBack } from '$lib/stores/mixer.svelte.js'

  let master = $derived(getMaster())
  let tracks = $derived(getTracks())
  let anySoloed = $derived(tracks.some(t => t.solo))
</script>

<div class="min-h-screen flex flex-col">
  <!-- Header -->
  <div class="flex items-center px-4 py-2 shrink-0">
    <button
      type="button"
      onclick={goBack}
      class="min-h-[44px] flex items-center gap-2 text-neutral-400 active:text-neutral-200"
    >
      <span class="text-lg">&larr;</span>
      <span class="text-xl font-bold text-neutral-200">{master?.name ?? ''}</span>
    </button>
  </div>

  <!-- Tracks stacked vertically -->
  <div class="flex flex-col gap-1.5 px-2 pb-4">
    <MasterOutput />
    {#each tracks as track (track.index)}
      <ChannelStrip {track} {anySoloed} />
    {/each}
  </div>
</div>
