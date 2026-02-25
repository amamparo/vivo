/**
 * Ableton volume scaling.
 *
 * Piecewise fit calibrated against Ableton Live's actual fader scale:
 *   Upper region (param ≥ 0.405): dB = 40 * param − 34       (linear)
 *   Lower region (param < 0.405): dB = −200p² + 202p − 66.8  (quadratic)
 *
 * The two segments meet with matching value and slope (~40 dB/unit) at
 * param ≈ 0.405 (≈ −17.8 dB). Unity gain (0 dB) is at param 0.85;
 * max (+6 dB) at param 1.0.
 *
 * The fader position maps 1:1 to the Ableton parameter.
 */

const KNEE = 0.405
const KNEE_DB = 40 * KNEE - 34 // ≈ -17.8 dB

// Ableton output_meter range: 0 → -60 dB, 1.0 → +6 dB
const METER_DB_MIN = -60
const METER_DB_MAX = 6
const METER_DB_RANGE = METER_DB_MAX - METER_DB_MIN // 66

/** Fader position (0–1) to Ableton volume parameter (0–1). Identity mapping. */
export function faderPosToVol(pos) {
  return pos
}

/** Ableton volume parameter (0–1) to fader position (0–1). Identity mapping. */
export function volToFaderPos(vol) {
  if (vol <= 0) return 0
  return Math.min(vol, 1)
}

/** Convert Ableton volume parameter (0–1) to dB value */
export function abletonParamToDb(param) {
  if (param <= 0) return -Infinity
  if (param >= KNEE) return 40 * param - 34
  return -200 * param * param + 202 * param - 66.8
}

/** Convert dB to Ableton volume parameter (0–1). Inverse of abletonParamToDb. */
export function dbToParam(db) {
  if (!isFinite(db)) return 0
  if (db >= KNEE_DB) return Math.max(0, Math.min(1, (db + 34) / 40))
  // Solve: -200p² + 202p - 66.8 = db → 200p² - 202p + (66.8 + db) = 0
  const disc = 202 * 202 - 4 * 200 * (66.8 + db) // 40804 - 800*(66.8+db)
  if (disc < 0) return 0
  return Math.max(0, (202 - Math.sqrt(disc)) / 400)
}

/** Format dB string from Ableton volume parameter (0–1) */
export function abletonVolToDbStr(param) {
  const db = abletonParamToDb(param)
  if (!isFinite(db)) return '-∞'
  return `${db >= 0 ? '+' : ''}${db.toFixed(1)}`
}

/** Unity gain fader position (0 dB at param 0.85) */
export const UNITY_POS = 0.85

/** Unity gain as Ableton volume parameter */
export const UNITY_VOL_ABLETON = 0.85

/**
 * Convert Ableton meter level (0–1, linear-in-dB) to display percentage (0–100)
 * matching the fader parameter scale.
 *
 * Ableton's output_meter values are linear in dB: 0 → -60 dB, 1.0 → +6 dB.
 * We convert meter → dB → fader param so the meter visually aligns with the fader.
 */
export function levelToPercent(level) {
  if (level <= 0) return 0
  const db = level * METER_DB_RANGE + METER_DB_MIN // linear-in-dB → dB
  const param = dbToParam(db)
  return Math.min(param, 1) * 100
}
