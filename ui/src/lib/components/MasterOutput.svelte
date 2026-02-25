<script>
  import Fader from './Fader.svelte'
  import MeterBar from './MeterBar.svelte'
  import { abletonVolToDbStr } from '$lib/helpers.js'
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
  <div class="flex flex-col gap-1 px-3 py-2 rounded-lg bg-[#333]">
    <!-- Row 1: Master label (min-h matches ToggleButton height in ChannelStrip) -->
    <div class="flex items-center min-h-[36px]">
      <span class="text-xs font-bold text-neutral-200">Master</span>
    </div>

    <!-- Row 2: fader + meter + dB -->
    <div class="flex items-center gap-2">
      <div class="flex-1 flex flex-col min-w-0">
        <Fader value={master.volume} onchange={handleVolumeChange} />
        <MeterBar left={meter.left} right={meter.right} muted={master.mute} />
      </div>
      <span class="text-[10px] text-neutral-500 font-mono tabular-nums whitespace-nowrap shrink-0 w-12 text-right">
        {abletonVolToDbStr(master.volume)} dB
      </span>
    </div>
  </div>
{/if}
