<script>
  import { levelToPercent } from '$lib/helpers.js'

  let { left = 0, right = 0 } = $props()

  let leftPct = $derived(levelToPercent(left))
  let rightPct = $derived(levelToPercent(right))
  let leftClip = $derived(left >= 1.0)
  let rightClip = $derived(right >= 1.0)

  const meterGradient = 'background: linear-gradient(to top, #22c55e 0%, #22c55e 60%, #eab308 75%, #ef4444 100%)'
</script>

<div class="flex gap-[3px] h-full min-h-[120px]">
  <div class="relative w-[6px] rounded-sm overflow-hidden bg-neutral-900">
    {#if leftClip}
      <div class="absolute top-0 left-0 right-0 h-1 bg-red-500 z-10"></div>
    {/if}
    <div
      class="absolute bottom-0 left-0 right-0 rounded-sm transition-[height] duration-100 ease-out"
      style="height: {leftPct}%; {meterGradient}"
    ></div>
  </div>
  <div class="relative w-[6px] rounded-sm overflow-hidden bg-neutral-900">
    {#if rightClip}
      <div class="absolute top-0 left-0 right-0 h-1 bg-red-500 z-10"></div>
    {/if}
    <div
      class="absolute bottom-0 left-0 right-0 rounded-sm transition-[height] duration-100 ease-out"
      style="height: {rightPct}%; {meterGradient}"
    ></div>
  </div>
</div>
