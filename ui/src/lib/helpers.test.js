import { describe, test, expect } from 'vitest'
import {
  faderPosToVol,
  volToFaderPos,
  volToDb,
  abletonVolToDbStr,
  levelToPercent,
  UNITY_POS,
  UNITY_VOL_ABLETON,
} from './helpers.js'

describe('faderPosToVol', () => {
  test('zero position is silence', () => {
    expect(faderPosToVol(0)).toBe(0)
  })

  test('full position is max volume (4.0)', () => {
    expect(faderPosToVol(1)).toBe(4)
  })

  test('half position is far below unity due to quartic curve', () => {
    expect(faderPosToVol(0.5)).toBeCloseTo(0.25, 5)
  })

  test('unity position yields unity volume (1.0)', () => {
    expect(faderPosToVol(UNITY_POS)).toBeCloseTo(1.0, 5)
  })

  test('quartic scaling: small positions yield very low volumes', () => {
    expect(faderPosToVol(0.1)).toBeCloseTo(0.0004, 5)
  })
})

describe('volToFaderPos', () => {
  test('silence maps to zero position', () => {
    expect(volToFaderPos(0)).toBe(0)
  })

  test('negative volume maps to zero position', () => {
    expect(volToFaderPos(-1)).toBe(0)
  })

  test('unity volume maps to ~0.7071', () => {
    expect(volToFaderPos(1.0)).toBeCloseTo(UNITY_POS, 5)
  })

  test('max volume maps to full position', () => {
    expect(volToFaderPos(4.0)).toBeCloseTo(1.0, 5)
  })

  test('round-trip: vol -> pos -> vol', () => {
    for (const vol of [0, 0.01, 0.1, 0.25, 0.5, 1.0, 2.0, 4.0]) {
      const pos = volToFaderPos(vol)
      expect(faderPosToVol(pos)).toBeCloseTo(vol, 5)
    }
  })

  test('round-trip: pos -> vol -> pos', () => {
    for (const pos of [0, 0.1, 0.25, 0.5, 0.7071, 0.9, 1.0]) {
      const vol = faderPosToVol(pos)
      expect(volToFaderPos(vol)).toBeCloseTo(pos, 5)
    }
  })
})

describe('volToDb', () => {
  test('silence returns -infinity symbol', () => {
    expect(volToDb(0)).toBe('-∞')
  })

  test('near-zero returns -infinity symbol', () => {
    expect(volToDb(0.000001)).toBe('-∞')
  })

  test('unity volume (1.0) is 0 dB', () => {
    expect(volToDb(1.0)).toBe('+0.0')
  })

  test('double amplitude is +6 dB', () => {
    expect(volToDb(2.0)).toBeCloseTo(6.0, 0)
    expect(volToDb(2.0)).toMatch(/^\+6\.0/)
  })

  test('half amplitude is -6 dB', () => {
    expect(volToDb(0.5)).toMatch(/^-6\.0/)
  })

  test('max volume (4.0) is ~+12 dB', () => {
    expect(volToDb(4.0)).toMatch(/^\+12\.0/)
  })

  test('positive dB values have + prefix', () => {
    expect(volToDb(1.5)).toMatch(/^\+/)
  })

  test('negative dB values have - prefix', () => {
    expect(volToDb(0.5)).toMatch(/^-/)
  })
})

describe('abletonVolToDbStr', () => {
  test('ableton 0.25 (unity) is 0 dB', () => {
    expect(abletonVolToDbStr(0.25)).toBe('+0.0')
  })

  test('ableton 0 is silence', () => {
    expect(abletonVolToDbStr(0)).toBe('-∞')
  })

  test('ableton 1.0 (max) is ~+12 dB', () => {
    expect(abletonVolToDbStr(1.0)).toMatch(/^\+12\.0/)
  })

  test('ableton 0.85 (default track volume) produces a positive dB value', () => {
    const result = abletonVolToDbStr(0.85)
    expect(result).toMatch(/^\+/)
  })
})

describe('constants', () => {
  test('UNITY_POS is approximately 0.7071', () => {
    expect(UNITY_POS).toBeCloseTo(Math.pow(0.25, 0.25), 10)
  })

  test('UNITY_VOL_ABLETON is 0.25', () => {
    expect(UNITY_VOL_ABLETON).toBe(0.25)
  })

  test('UNITY_POS round-trips to unity volume', () => {
    expect(faderPosToVol(UNITY_POS)).toBeCloseTo(1.0, 10)
  })
})

describe('levelToPercent', () => {
  test('zero level is 0%', () => {
    expect(levelToPercent(0)).toBe(0)
  })

  test('negative level is 0%', () => {
    expect(levelToPercent(-0.5)).toBe(0)
  })

  test('unity level (1.0) is 0 dB, maps to ~90.9%', () => {
    // 0 dB → (0 + 60) / 66 * 100 = 90.9%
    expect(levelToPercent(1.0)).toBeCloseTo(90.9, 0)
  })

  test('clipping level (2.0) is +6 dB, maps to ~100%', () => {
    // +6 dB → (6 + 60) / 66 * 100 = 100%
    expect(levelToPercent(2.0)).toBeCloseTo(100, 0)
  })

  test('result is clamped to 0-100', () => {
    expect(levelToPercent(0)).toBe(0)
    expect(levelToPercent(10)).toBeLessThanOrEqual(100)
  })

  test('very quiet signal has low percentage', () => {
    // -60 dB = 0.001 linear → (−60 + 60) / 66 * 100 = 0%
    expect(levelToPercent(0.001)).toBeCloseTo(0, 0)
  })

  test('mid-range signal produces mid-range percentage', () => {
    // -20 dB = 0.1 linear → (−20 + 60) / 66 * 100 ≈ 60.6%
    expect(levelToPercent(0.1)).toBeCloseTo(60.6, 0)
  })

  test('monotonically increasing: louder signal = higher percentage', () => {
    const levels = [0.001, 0.01, 0.1, 0.5, 1.0, 1.5]
    const percents = levels.map(levelToPercent)
    for (let i = 1; i < percents.length; i++) {
      expect(percents[i]).toBeGreaterThan(percents[i - 1])
    }
  })
})
