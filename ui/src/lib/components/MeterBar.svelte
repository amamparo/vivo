<script>
  import { levelToPercent } from '$lib/helpers.js'

  let { left = 0, right = 0, muted = false } = $props()

  let meterEl = $state(null)
  let meterWidth = $state(0)

  const SEG = 5 // 4px lit + 1px gap
  const HOLD_MS = 1500
  const DECAY_RATE = 60 // percent per second

  let leftPct = $derived(levelToPercent(left))
  let rightPct = $derived(levelToPercent(right))
  let leftClip = $derived(!muted && left >= 1.0)
  let rightClip = $derived(!muted && right >= 1.0)

  let leftPeakPct = $state(0)
  let rightPeakPct = $state(0)

  // Peak hold & decay animation loop
  $effect(() => {
    let frame
    let peakL = 0, peakR = 0
    let timeL = 0, timeR = 0
    let lastTime = performance.now()

    function tick() {
      const now = performance.now()
      const dt = (now - lastTime) / 1000
      lastTime = now
      const decay = DECAY_RATE * dt

      const curL = levelToPercent(left)
      const curR = levelToPercent(right)

      if (curL >= peakL) { peakL = curL; timeL = now }
      if (curR >= peakR) { peakR = curR; timeR = now }

      if (now - timeL > HOLD_MS && peakL > curL) {
        peakL = Math.max(curL, peakL - decay)
      }
      if (now - timeR > HOLD_MS && peakR > curR) {
        peakR = Math.max(curR, peakR - decay)
      }

      leftPeakPct = peakL
      rightPeakPct = peakR

      frame = requestAnimationFrame(tick)
    }
    frame = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(frame)
  })

  function quantize(pct) {
    if (meterWidth <= 0) return 0
    const px = (pct / 100) * meterWidth
    return Math.floor(px / SEG) * SEG
  }

  let leftFillW = $derived(quantize(leftPct))
  let rightFillW = $derived(quantize(rightPct))
  let leftPeakW = $derived(quantize(leftPeakPct))
  let rightPeakW = $derived(quantize(rightPeakPct))

  $effect(() => {
    if (!meterEl) return
    const ro = new ResizeObserver(entries => {
      meterWidth = entries[0].contentRect.width
    })
    ro.observe(meterEl)
    return () => ro.disconnect()
  })
</script>

<div bind:this={meterEl} class="flex flex-col gap-[1px] w-full px-[1rem]">
  <div class="meter-row">
    <div
      class="meter-fill"
      class:muted
      style="width: {leftFillW}px; background-size: {meterWidth}px 100%"
    ></div>
    {#if leftPeakW > leftFillW && leftPeakW >= SEG}
      <div
        class="meter-peak"
        class:muted
        style="left: {leftPeakW - SEG}px; background-size: {meterWidth}px 100%; background-position: -{leftPeakW - SEG}px 0"
      ></div>
    {/if}
    {#if leftClip}
      <div class="meter-clip-indicator"></div>
    {/if}
  </div>
  <div class="meter-row">
    <div
      class="meter-fill"
      class:muted
      style="width: {rightFillW}px; background-size: {meterWidth}px 100%"
    ></div>
    {#if rightPeakW > rightFillW && rightPeakW >= SEG}
      <div
        class="meter-peak"
        class:muted
        style="left: {rightPeakW - SEG}px; background-size: {meterWidth}px 100%; background-position: -{rightPeakW - SEG}px 0"
      ></div>
    {/if}
    {#if rightClip}
      <div class="meter-clip-indicator"></div>
    {/if}
  </div>
</div>

<style>
  .meter-row {
    position: relative;
    height: 3px;
    overflow: hidden;
    background: repeating-linear-gradient(
      to right,
      rgba(255,255,255,0.04) 0px, rgba(255,255,255,0.04) 4px,
      transparent 4px, transparent 5px
    );
  }
  .meter-fill {
    position: absolute;
    top: 0;
    left: 0;
    bottom: 0;
    background-image: linear-gradient(to right, #22c55e 0%, #22c55e 60%, #eab308 75%, #ef4444 100%);
    -webkit-mask-image: repeating-linear-gradient(to right, white 0px, white 4px, transparent 4px, transparent 5px);
    mask-image: repeating-linear-gradient(to right, white 0px, white 4px, transparent 4px, transparent 5px);
  }
  .meter-fill.muted {
    background-image: linear-gradient(to right, #525252, #525252);
  }
  .meter-peak {
    position: absolute;
    top: 0;
    bottom: 0;
    width: 4px;
    background-image: linear-gradient(to right, #22c55e 0%, #22c55e 60%, #eab308 75%, #ef4444 100%);
  }
  .meter-peak.muted {
    background-image: linear-gradient(to right, #525252, #525252);
  }
  .meter-clip-indicator {
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    width: 4px;
    background: #ef4444;
    z-index: 10;
  }
</style>
