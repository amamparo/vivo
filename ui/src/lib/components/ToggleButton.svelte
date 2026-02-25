<script>
  let { label, active = false, onclick } = $props()
</script>

<button
  type="button"
  class="min-w-[44px] min-h-[44px] px-3 py-2 rounded text-sm font-bold transition-colors {active ? 'bg-red-600 text-white' : 'bg-neutral-800 text-neutral-400'}"
  {onclick}
>
  {label}
</button>
