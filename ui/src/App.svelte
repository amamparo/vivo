<script>
  import { onMount } from 'svelte'
  import { connect } from '$lib/stores/connection.svelte.js'
  import { getSelectedGroupIndex } from '$lib/stores/mixer.svelte.js'
  import LandingPage from '$lib/components/LandingPage.svelte'
  import MixerPage from '$lib/components/MixerPage.svelte'

  let selected = $derived(getSelectedGroupIndex() >= 0)

  onMount(() => {
    connect()
  })
</script>

{#if selected}
  <MixerPage />
{:else}
  <LandingPage />
{/if}
