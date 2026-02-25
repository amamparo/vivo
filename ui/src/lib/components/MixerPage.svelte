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
  <div class="flex items-center gap-3 p-4 shrink-0">
    <button
      type="button"
      onclick={goBack}
      class="min-w-[44px] min-h-[44px] flex items-center justify-center text-neutral-400 active:text-neutral-200"
    >
      <span class="text-lg">&larr;</span>
    </button>
    <span class="text-xl font-bold text-neutral-200">{master?.name ?? ''}</span>
  </div>

  <!-- Master output -->
  <div class="px-4 shrink-0">
    <MasterOutput />
  </div>

  <!-- Channel strips — horizontally scrollable -->
  <div class="flex-1 overflow-x-auto px-4 py-4">
    <div class="flex gap-2 pb-2">
      {#each tracks as track (track.index)}
        <ChannelStrip {track} {anySoloed} />
      {/each}
    </div>
  </div>
</div>
