<script>
  import Fader from './Fader.svelte'
  import MeterBar from './MeterBar.svelte'
  import { getMaster, setVolume, getMeter } from '$lib/stores/mixer.svelte.js'

  let master = $derived(getMaster())
  let meter = $derived(master ? getMeter(master.index) : { left: 0, right: 0 })

  function handleVolumeChange(vol) {
    if (master) {
      setVolume(master.index, vol)
    }
  }
</script>

{#if master}
  <div class="flex flex-col items-center gap-2 p-4 rounded-lg bg-neutral-900">
    <span class="text-sm font-bold text-neutral-200">Master Output</span>
    <div class="flex gap-3 items-stretch">
      <Fader value={master.volume} onchange={handleVolumeChange} large={true} />
      <MeterBar left={meter.left} right={meter.right} />
    </div>
  </div>
{/if}
