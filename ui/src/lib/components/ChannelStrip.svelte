<script>
  import Fader from './Fader.svelte'
  import MeterBar from './MeterBar.svelte'
  import ToggleButton from './ToggleButton.svelte'
  import { abletonVolToDbStr } from '$lib/helpers.js'
  import { setVolume, setMute, toggleSolo, getMeter } from '$lib/stores/mixer.svelte.js'

  let { track, anySoloed = false } = $props()

  let meter = $derived(getMeter(track.index))
  let dimmed = $derived(anySoloed && !track.solo)

  function handleVolumeChange(vol) {
    setVolume(track.index, vol)
  }

  function handleMuteToggle() {
    setMute(track.index, !track.mute)
  }

  function handleSoloToggle() {
    toggleSolo(track.index)
  }
</script>

<div
  class="flex flex-col gap-1 px-3 py-2 rounded-lg bg-neutral-900 transition-opacity"
  style="opacity: {dimmed ? 0.4 : 1};"
>
  <!-- Row 1: name + S/M buttons -->
  <div class="flex items-center justify-between">
    <span class="text-xs text-neutral-300 truncate min-w-0">{track.name}</span>
    <div class="flex gap-1 shrink-0">
      <ToggleButton label="S" active={track.solo} activeClass="bg-amber-500 text-white" onclick={handleSoloToggle} />
      <ToggleButton label="M" active={track.mute} onclick={handleMuteToggle} />
    </div>
  </div>

  <!-- Row 2: fader + meter + dB -->
  <div class="flex items-center gap-2">
    <div class="flex-1 flex flex-col min-w-0">
      <Fader value={track.volume} onchange={handleVolumeChange} />
      <MeterBar left={meter.left} right={meter.right} muted={track.mute} />
    </div>
    <span class="text-[10px] text-neutral-500 font-mono tabular-nums whitespace-nowrap shrink-0 w-12 text-right">
      {abletonVolToDbStr(track.volume)} dB
    </span>
  </div>
</div>
