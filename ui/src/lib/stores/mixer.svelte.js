import { onMessage, onConnect, send } from './connection.svelte.js'

let mixes = $state([])
let selectedGroupIndex = $state(-1)
let master = $state(null)
let tracks = $state([])
let meters = $state({})

// Restore mix selection from URL hash on connect
function readHash() {
  const match = location.hash.match(/^#mix\/(\d+)$/)
  return match ? parseInt(match[1], 10) : -1
}

onConnect(() => {
  const idx = readHash()
  if (idx >= 0) {
    selectedGroupIndex = idx
    send({ type: 'select_mix', group_index: idx })
  }
})

if (typeof window !== 'undefined') {
  window.addEventListener('hashchange', () => {
    const idx = readHash()
    if (idx < 0 && selectedGroupIndex >= 0) {
      selectedGroupIndex = -1
      master = null
      tracks = []
    }
  })
}

onMessage((msg) => {
  if (msg.type === 'mixes') {
    mixes = msg.mixes
  } else if (msg.type === 'mix_state') {
    if (!msg.master) {
      selectedGroupIndex = -1
      master = null
      tracks = []
      location.hash = ''
    } else {
      master = msg.master
      tracks = msg.tracks
    }
  } else if (msg.type === 'meters') {
    meters = msg.levels
  }
})

export function getMixes() {
  return mixes
}

export function getSelectedGroupIndex() {
  return selectedGroupIndex
}

export function getMaster() {
  return master
}

export function getTracks() {
  return tracks
}

export function getMeter(trackIndex) {
  return meters[trackIndex] || { left: 0, right: 0 }
}

export function selectMix(groupIndex) {
  selectedGroupIndex = groupIndex
  location.hash = `mix/${groupIndex}`
  send({ type: 'select_mix', group_index: groupIndex })
}

export function goBack() {
  selectedGroupIndex = -1
  master = null
  tracks = []
  history.back()
}

export function setVolume(trackIndex, volume) {
  tracks = tracks.map(t =>
    t.index === trackIndex ? { ...t, volume } : t
  )
  if (master?.index === trackIndex) {
    master = { ...master, volume }
  }
  send({ type: 'set_volume', track_index: trackIndex, volume })
}

export function setMute(trackIndex, mute) {
  tracks = tracks.map(t =>
    t.index === trackIndex ? { ...t, mute } : t
  )
  send({ type: 'set_mute', track_index: trackIndex, mute })
}

export function toggleSolo(trackIndex) {
  send({ type: 'toggle_solo', track_index: trackIndex })
}
