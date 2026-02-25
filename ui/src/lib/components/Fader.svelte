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
  let dragValid = false

  const THUMB_W = 48 // 3rem
  const HIT_PAD = 12 // extra px around knob for touch ease

  function knobCenter() {
    const rect = overlayEl.getBoundingClientRect()
    const pos = volToFaderPos(value)
    return THUMB_W / 2 + pos * (rect.width - THUMB_W)
  }

  function isOnKnob(pointerX) {
    const rect = overlayEl.getBoundingClientRect()
    const relX = pointerX - rect.left
    return Math.abs(relX - knobCenter()) <= THUMB_W / 2 + HIT_PAD
  }

  $effect(() => {
    if (!overlayEl) return

    // Prevent scrolling when touching the knob (must be non-passive to call preventDefault)
    function onTouchStart(e) {
      const touch = e.touches[0]
      if (touch && isOnKnob(touch.clientX)) {
        e.preventDefault()
      }
    }
    overlayEl.addEventListener('touchstart', onTouchStart, { passive: false })

    const gesture = new DragGesture(overlayEl, (state) => {
      const { dragging, tap, movement: [mx], first, xy } = state

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
        posAtDown = volToFaderPos(value)
        dragValid = isOnKnob(xy[0])
        if (dragValid) interacting = true
      }

      if (!dragValid) return

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

    return () => {
      overlayEl.removeEventListener('touchstart', onTouchStart)
      gesture.destroy()
    }
  })

  $effect(() => {
    if (rangeEl && !interacting) {
      rangeEl.value = volToFaderPos(value)
    }
  })
</script>

<div class="relative h-12 w-full">
  <div class="absolute top-1/2 left-[1rem] right-[1rem] -translate-y-1/2 h-1.5 rounded-sm bg-[#111] shadow-[inset_0_1px_3px_rgba(0,0,0,0.7)] pointer-events-none"></div>
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
    class="absolute inset-0 z-[3]"
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
      /* Foreground depth: top highlight fading to bottom shadow */
      linear-gradient(to bottom,
        rgba(255,255,255,0.12) 0%, transparent 25%,
        transparent 65%, rgba(0,0,0,0.1) 100%),
      /* Three grip lines */
      linear-gradient(to right,
        transparent 33%,
        rgba(0,0,0,0.4) 33%, rgba(0,0,0,0.4) 34.5%,
        rgba(255,255,255,0.22) 34.5%, rgba(255,255,255,0.22) 36%,
        transparent 36%,
        transparent 49%,
        rgba(0,0,0,0.4) 49%, rgba(0,0,0,0.4) 50.5%,
        rgba(255,255,255,0.22) 50.5%, rgba(255,255,255,0.22) 52%,
        transparent 52%,
        transparent 64.5%,
        rgba(0,0,0,0.4) 64.5%, rgba(0,0,0,0.4) 66%,
        rgba(255,255,255,0.22) 66%, rgba(255,255,255,0.22) 67.5%,
        transparent 67.5%),
      /* Base surface */
      linear-gradient(to bottom,
        #e8e8e8 0%, #ddd 10%, #ccc 45%,
        #c0c0c0 55%, #c8c8c8 85%, #d2d2d2 100%);
    background-size: 100% 100%, 100% 55%, 100% 100%;
    background-position: center center;
    background-repeat: no-repeat;
    box-shadow:
      0 2px 6px rgba(0,0,0,0.5),
      0 0 0 0.5px rgba(0,0,0,0.3),
      inset 0 1px 0 rgba(255,255,255,0.5),
      inset 0 -1px 0 rgba(0,0,0,0.2),
      inset 1px 0 0 rgba(255,255,255,0.15),
      inset -1px 0 0 rgba(0,0,0,0.1);
  }
  .fader-input::-moz-range-thumb {
    height: 2rem;
    width: 3rem;
    border: none;
    border-radius: 3px;
    background-image:
      /* Foreground depth: top highlight fading to bottom shadow */
      linear-gradient(to bottom,
        rgba(255,255,255,0.12) 0%, transparent 25%,
        transparent 65%, rgba(0,0,0,0.1) 100%),
      /* Three grip lines */
      linear-gradient(to right,
        transparent 33%,
        rgba(0,0,0,0.4) 33%, rgba(0,0,0,0.4) 34.5%,
        rgba(255,255,255,0.22) 34.5%, rgba(255,255,255,0.22) 36%,
        transparent 36%,
        transparent 49%,
        rgba(0,0,0,0.4) 49%, rgba(0,0,0,0.4) 50.5%,
        rgba(255,255,255,0.22) 50.5%, rgba(255,255,255,0.22) 52%,
        transparent 52%,
        transparent 64.5%,
        rgba(0,0,0,0.4) 64.5%, rgba(0,0,0,0.4) 66%,
        rgba(255,255,255,0.22) 66%, rgba(255,255,255,0.22) 67.5%,
        transparent 67.5%),
      /* Base surface */
      linear-gradient(to bottom,
        #e8e8e8 0%, #ddd 10%, #ccc 45%,
        #c0c0c0 55%, #c8c8c8 85%, #d2d2d2 100%);
    background-size: 100% 100%, 100% 55%, 100% 100%;
    background-position: center center;
    background-repeat: no-repeat;
    box-shadow:
      0 2px 6px rgba(0,0,0,0.5),
      0 0 0 0.5px rgba(0,0,0,0.3),
      inset 0 1px 0 rgba(255,255,255,0.5),
      inset 0 -1px 0 rgba(0,0,0,0.2),
      inset 1px 0 0 rgba(255,255,255,0.15),
      inset -1px 0 0 rgba(0,0,0,0.1);
  }
</style>
