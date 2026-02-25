import { onMessage, send } from './connection.svelte.js'

let mixes = $state([])
let selectedGroupIndex = $state(-1)
let master = $state(null)
let tracks = $state([])
let meters = $state({})

onMessage((msg) => {
  if (msg.type === 'mixes') {
    mixes = msg.mixes
  } else if (msg.type === 'mix_state') {
    master = msg.master
    tracks = msg.tracks
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
  send({ type: 'select_mix', group_index: groupIndex })
}

export function goBack() {
  selectedGroupIndex = -1
  master = null
  tracks = []
}

export function setVolume(trackIndex, volume) {
  send({ type: 'set_volume', track_index: trackIndex, volume })
}

export function setMute(trackIndex, mute) {
  send({ type: 'set_mute', track_index: trackIndex, mute })
}

export function toggleSolo(trackIndex) {
  send({ type: 'toggle_solo', track_index: trackIndex })
}
