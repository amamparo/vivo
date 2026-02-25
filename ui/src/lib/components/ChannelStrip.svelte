<script>
  import Fader from './Fader.svelte'
  import MeterBar from './MeterBar.svelte'
  import ToggleButton from './ToggleButton.svelte'
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
  class="flex flex-col items-center gap-2 p-3 rounded-lg bg-neutral-900 min-w-[80px] transition-opacity"
  style="opacity: {dimmed ? 0.4 : 1};"
>
  <!-- Track name with color dot -->
  <div class="flex items-center gap-1.5 w-full min-h-[20px]">
    <div class="w-2.5 h-2.5 rounded-full shrink-0" style="background-color: {track.color}"></div>
    <span class="text-xs text-neutral-300 truncate">{track.name}</span>
  </div>

  <!-- Solo / Mute buttons -->
  <div class="flex gap-1.5">
    <ToggleButton label="S" active={track.solo} onclick={handleSoloToggle} />
    <ToggleButton label="M" active={track.mute} onclick={handleMuteToggle} />
  </div>

  <!-- Fader and meter side by side -->
  <div class="flex gap-2 items-stretch">
    <Fader value={track.volume} onchange={handleVolumeChange} />
    <MeterBar left={meter.left} right={meter.right} />
  </div>
</div>
