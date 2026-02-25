/**
 * Quartic volume scaling for natural audio feel.
 * Fader position 0-1, volume 0-1 (sent to Ableton).
 * Unity gain at fader position ~0.7071 → volume 0.25.
 */

const MAX_VOL = 4.0

export function faderPosToVol(pos) {
  return Math.pow(pos, 4) * MAX_VOL
}

export function volToFaderPos(vol) {
  if (vol <= 0) return 0
  return Math.pow(vol / MAX_VOL, 0.25)
}

/** Convert internal volume (0-4) to dB string */
export function volToDb(vol) {
  if (vol < 0.00001) return '-∞'
  const db = 20 * Math.log10(vol)
  return `${db >= 0 ? '+' : ''}${db.toFixed(1)}`
}

/** Format dB string from Ableton volume parameter (0-1) */
export function abletonVolToDbStr(abletonVol) {
  const internalVol = abletonVol * MAX_VOL
  return volToDb(internalVol)
}

/** Unity gain in fader position */
export const UNITY_POS = volToFaderPos(1.0)

/** Unity gain as Ableton volume parameter */
export const UNITY_VOL_ABLETON = 1.0 / MAX_VOL

/** Convert linear level (0+) to meter display percentage (0-100). Maps -60 dB to +6 dB range. */
export function levelToPercent(level) {
  if (level <= 0) return 0
  const db = 20 * Math.log10(level)
  const pct = ((db + 60) / 66) * 100
  return Math.max(0, Math.min(100, pct))
}
