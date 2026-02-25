<script>
  let { label, active = false, activeClass = 'bg-red-600 text-white', onclick } = $props()
</script>

<button
  type="button"
  class="min-w-[36px] min-h-[36px] px-2 py-1 rounded text-xs font-bold transition-colors {active ? activeClass : 'bg-[#363636] text-neutral-400'}"
  {onclick}
>
  {label}
</button>
