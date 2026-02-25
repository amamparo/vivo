<script>
  import { volToFaderPos, faderPosToVol, abletonVolToDbStr, UNITY_POS, UNITY_VOL_ABLETON } from '$lib/helpers.js'

  let { value = 0, onchange, large = false } = $props()

  const TAP_THRESHOLD = 5

  let dragging = $state(false)
  let rangeEl = $state(null)
  let isDrag = false
  let pointerStartY = 0
  let valueAtDown = '0'
  let lastTapTime = 0

  let displayPos = $derived(dragging ? undefined : volToFaderPos(value))

  function handlePointerDown(e) {
    pointerStartY = e.clientY
    valueAtDown = rangeEl.value
    isDrag = false
  }

  function handlePointerMove(e) {
    if (isDrag) return
    if (Math.abs(e.clientY - pointerStartY) > TAP_THRESHOLD) {
      isDrag = true
      dragging = true
    }
  }

  function handleInput(e) {
    if (!isDrag) {
      rangeEl.value = valueAtDown
      return
    }
    dragging = true
    const pos = parseFloat(e.target.value)
    const vol = faderPosToVol(pos)
    onchange?.(vol)
  }

  function handlePointerUp() {
    if (!isDrag) {
      const now = Date.now()
      if (now - lastTapTime < 300) {
        rangeEl.value = UNITY_POS
        onchange?.(UNITY_VOL_ABLETON)
        lastTapTime = 0
      } else {
        lastTapTime = now
      }
    } else {
      const pos = parseFloat(rangeEl.value)
      const vol = faderPosToVol(pos)
      onchange?.(vol)
    }
    isDrag = false
    dragging = false
  }

  $effect(() => {
    if (rangeEl && !dragging && displayPos !== undefined) {
      rangeEl.value = displayPos
    }
  })
</script>

<div class="flex flex-col items-center gap-1">
  <div class="relative {large ? 'w-12 h-[220px]' : 'w-10 h-[160px]'}">
    <div class="absolute left-1/2 top-0 bottom-0 -translate-x-1/2 w-1.5 rounded-sm bg-[#0a0a0a] shadow-[inset_0_1px_3px_rgba(0,0,0,0.7)] pointer-events-none"></div>
    <div class="absolute left-1/2 bottom-[70.71%] -translate-x-1/2 translate-y-1/2 z-[1] w-5 h-0.5 bg-neutral-700 pointer-events-none rounded-[1px]"></div>
    <input
      bind:this={rangeEl}
      type="range"
      min="0" max="1" step="0.002"
      value={volToFaderPos(value)}
      oninput={handleInput}
      onpointerdown={handlePointerDown}
      onpointermove={handlePointerMove}
      onpointerup={handlePointerUp}
      class="fader-input appearance-none [writing-mode:vertical-lr] [direction:rtl] bg-transparent w-full h-full m-0 p-0 relative z-[2] touch-none"
      class:fader-large={large}
    />
  </div>
  <span class="text-[10px] text-neutral-500 font-mono tabular-nums whitespace-nowrap">
    {abletonVolToDbStr(value)} dB
  </span>
</div>

<style>
  .fader-input::-webkit-slider-runnable-track {
    width: 6px;
    background: transparent;
  }
  .fader-input::-moz-range-track {
    width: 6px;
    background: transparent;
  }
  .fader-input::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 2rem;
    height: 1.25rem;
    border-radius: 3px;
    background-image:
      linear-gradient(to bottom,
        transparent 28%,
        rgba(0,0,0,0.4) 28%, rgba(0,0,0,0.4) 30%,
        rgba(255,255,255,0.25) 30%, rgba(255,255,255,0.25) 32%,
        transparent 32%,
        transparent 48%,
        rgba(0,0,0,0.4) 48%, rgba(0,0,0,0.4) 50%,
        rgba(255,255,255,0.25) 50%, rgba(255,255,255,0.25) 52%,
        transparent 52%,
        transparent 68%,
        rgba(0,0,0,0.4) 68%, rgba(0,0,0,0.4) 70%,
        rgba(255,255,255,0.25) 70%, rgba(255,255,255,0.25) 72%,
        transparent 72%),
      linear-gradient(to right,
        #e0e0e0 0%, #ccc 20%, #b0b0b0 50%, #bbb 80%, #d0d0d0 100%);
    background-size: 100% 50%, 100% 100%;
    background-position: center center;
    background-repeat: no-repeat;
    box-shadow:
      0 1px 4px rgba(0,0,0,0.5),
      0 0 0 0.5px rgba(0,0,0,0.2),
      inset 0 1px 0 rgba(255,255,255,0.4),
      inset 0 -1px 0 rgba(0,0,0,0.1);
  }
  .fader-large::-webkit-slider-thumb {
    width: 2.5rem;
    height: 1.5rem;
  }
  .fader-input::-moz-range-thumb {
    width: 2rem;
    height: 1.25rem;
    border: none;
    border-radius: 3px;
    background-image:
      linear-gradient(to bottom,
        transparent 28%,
        rgba(0,0,0,0.4) 28%, rgba(0,0,0,0.4) 30%,
        rgba(255,255,255,0.25) 30%, rgba(255,255,255,0.25) 32%,
        transparent 32%,
        transparent 48%,
        rgba(0,0,0,0.4) 48%, rgba(0,0,0,0.4) 50%,
        rgba(255,255,255,0.25) 50%, rgba(255,255,255,0.25) 52%,
        transparent 52%,
        transparent 68%,
        rgba(0,0,0,0.4) 68%, rgba(0,0,0,0.4) 70%,
        rgba(255,255,255,0.25) 70%, rgba(255,255,255,0.25) 72%,
        transparent 72%),
      linear-gradient(to right,
        #e0e0e0 0%, #ccc 20%, #b0b0b0 50%, #bbb 80%, #d0d0d0 100%);
    background-size: 100% 50%, 100% 100%;
    background-position: center center;
    background-repeat: no-repeat;
    box-shadow:
      0 1px 4px rgba(0,0,0,0.5),
      0 0 0 0.5px rgba(0,0,0,0.2),
      inset 0 1px 0 rgba(255,255,255,0.4),
      inset 0 -1px 0 rgba(0,0,0,0.1);
  }
  .fader-large::-moz-range-thumb {
    width: 2.5rem;
    height: 1.5rem;
  }
</style>
