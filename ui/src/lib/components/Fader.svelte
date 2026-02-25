<script>
  import { tick } from 'svelte'
  import { DragGesture } from '@use-gesture/vanilla'
  import { volToFaderPos, faderPosToVol, UNITY_POS, UNITY_VOL_ABLETON } from '$lib/helpers.js'

  let { value = 0, onchange } = $props()

  let rangeEl = $state(null)
  let overlayEl = $state(null)
  let interacting = $state(false)
  let posAtDown = 0
  let lastTapTime = 0

  $effect(() => {
    if (!overlayEl) return

    const gesture = new DragGesture(overlayEl, (state) => {
      const { dragging, tap, movement: [mx], first } = state

      if (tap) {
        const now = Date.now()
        if (now - lastTapTime < 300) {
          rangeEl.value = UNITY_POS
          onchange?.(UNITY_VOL_ABLETON)
          lastTapTime = 0
        } else {
          lastTapTime = now
        }
        return
      }

      if (first) {
        interacting = true
        posAtDown = volToFaderPos(value)
      }

      if (dragging) {
        const rect = overlayEl.getBoundingClientRect()
        const pos = Math.max(0, Math.min(1, posAtDown + mx / rect.width))
        rangeEl.value = pos
        onchange?.(faderPosToVol(pos))
      } else {
        tick().then(() => { interacting = false })
      }
    }, {
      filterTaps: true,
      pointer: { capture: true },
      threshold: 3,
    })

    return () => gesture.destroy()
  })

  $effect(() => {
    if (rangeEl && !interacting) {
      rangeEl.value = volToFaderPos(value)
    }
  })
</script>

<div class="relative h-12 w-full">
  <div class="absolute top-1/2 left-[1rem] right-[1rem] -translate-y-1/2 h-1.5 rounded-sm bg-[#0a0a0a] shadow-[inset_0_1px_3px_rgba(0,0,0,0.7)] pointer-events-none"></div>
  <div class="absolute left-[calc(85%-1.05rem)] -translate-x-1/2 bottom-[calc(50%+7px)] z-[1] h-[0.75rem] w-px bg-neutral-700 pointer-events-none"></div>
  <div class="absolute left-[calc(85%-1.05rem)] -translate-x-1/2 top-[calc(50%+7px)] z-[1] h-[0.75rem] w-px bg-neutral-700 pointer-events-none"></div>
  <input
    bind:this={rangeEl}
    type="range"
    min="0" max="1" step="0.002"
    class="fader-input appearance-none bg-transparent w-full h-full m-0 p-0 relative z-[2] pointer-events-none"
  />
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <div
    bind:this={overlayEl}
    class="absolute inset-0 z-[3] touch-none"
  ></div>
</div>

<style>
  .fader-input::-webkit-slider-runnable-track {
    height: 6px;
    background: transparent;
  }
  .fader-input::-moz-range-track {
    height: 6px;
    background: transparent;
  }
  .fader-input::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    height: 2rem;
    width: 3rem;
    margin-top: -13px;
    border-radius: 3px;
    background-image:
      linear-gradient(to right,
        transparent 30%,
        rgba(0,0,0,0.35) 30%, rgba(0,0,0,0.35) 31.5%,
        rgba(255,255,255,0.2) 31.5%, rgba(255,255,255,0.2) 33%,
        transparent 33%,
        transparent 48.5%,
        rgba(0,0,0,0.35) 48.5%, rgba(0,0,0,0.35) 50%,
        rgba(255,255,255,0.2) 50%, rgba(255,255,255,0.2) 51.5%,
        transparent 51.5%,
        transparent 67%,
        rgba(0,0,0,0.35) 67%, rgba(0,0,0,0.35) 68.5%,
        rgba(255,255,255,0.2) 68.5%, rgba(255,255,255,0.2) 70%,
        transparent 70%),
      linear-gradient(to bottom,
        #e8e8e8 0%, #ddd 8%, #c8c8c8 20%, #b0b0b0 45%,
        #a8a8a8 55%, #b8b8b8 80%, #ccc 92%, #d5d5d5 100%);
    background-size: 55% 100%, 100% 100%;
    background-position: center center;
    background-repeat: no-repeat;
    box-shadow:
      0 2px 5px rgba(0,0,0,0.5),
      0 0 0 0.5px rgba(0,0,0,0.25),
      inset 0 1px 0 rgba(255,255,255,0.5),
      inset 0 -1px 0 rgba(0,0,0,0.15),
      inset 1px 0 0 rgba(255,255,255,0.15),
      inset -1px 0 0 rgba(0,0,0,0.08);
  }
  .fader-input::-moz-range-thumb {
    height: 2rem;
    width: 3rem;
    border: none;
    border-radius: 3px;
    background-image:
      linear-gradient(to right,
        transparent 30%,
        rgba(0,0,0,0.35) 30%, rgba(0,0,0,0.35) 31.5%,
        rgba(255,255,255,0.2) 31.5%, rgba(255,255,255,0.2) 33%,
        transparent 33%,
        transparent 48.5%,
        rgba(0,0,0,0.35) 48.5%, rgba(0,0,0,0.35) 50%,
        rgba(255,255,255,0.2) 50%, rgba(255,255,255,0.2) 51.5%,
        transparent 51.5%,
        transparent 67%,
        rgba(0,0,0,0.35) 67%, rgba(0,0,0,0.35) 68.5%,
        rgba(255,255,255,0.2) 68.5%, rgba(255,255,255,0.2) 70%,
        transparent 70%),
      linear-gradient(to bottom,
        #e8e8e8 0%, #ddd 8%, #c8c8c8 20%, #b0b0b0 45%,
        #a8a8a8 55%, #b8b8b8 80%, #ccc 92%, #d5d5d5 100%);
    background-size: 55% 100%, 100% 100%;
    background-position: center center;
    background-repeat: no-repeat;
    box-shadow:
      0 2px 5px rgba(0,0,0,0.5),
      0 0 0 0.5px rgba(0,0,0,0.25),
      inset 0 1px 0 rgba(255,255,255,0.5),
      inset 0 -1px 0 rgba(0,0,0,0.15),
      inset 1px 0 0 rgba(255,255,255,0.15),
      inset -1px 0 0 rgba(0,0,0,0.08);
  }
</style>
