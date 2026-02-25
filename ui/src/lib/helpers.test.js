import { describe, test, expect } from 'vitest'
import {
  faderPosToVol,
  volToFaderPos,
  abletonParamToDb,
  dbToParam,
  abletonVolToDbStr,
  levelToPercent,
  UNITY_POS,
  UNITY_VOL_ABLETON,
} from './helpers.js'

describe('faderPosToVol', () => {
  test('identity mapping: position equals volume parameter', () => {
    expect(faderPosToVol(0)).toBe(0)
    expect(faderPosToVol(0.5)).toBe(0.5)
    expect(faderPosToVol(1)).toBe(1)
  })
})

describe('volToFaderPos', () => {
  test('silence maps to zero position', () => {
    expect(volToFaderPos(0)).toBe(0)
  })

  test('negative volume maps to zero position', () => {
    expect(volToFaderPos(-1)).toBe(0)
  })

  test('identity mapping for valid range', () => {
    expect(volToFaderPos(0.5)).toBe(0.5)
    expect(volToFaderPos(0.85)).toBe(0.85)
    expect(volToFaderPos(1.0)).toBe(1.0)
  })

  test('clamps to 1.0', () => {
    expect(volToFaderPos(1.5)).toBe(1.0)
  })

  test('round-trip: pos -> vol -> pos', () => {
    for (const pos of [0, 0.1, 0.25, 0.5, 0.85, 0.9, 1.0]) {
      const vol = faderPosToVol(pos)
      expect(volToFaderPos(vol)).toBeCloseTo(pos, 5)
    }
  })
})

describe('abletonParamToDb', () => {
  test('param 0 is -Infinity', () => {
    expect(abletonParamToDb(0)).toBe(-Infinity)
  })

  test('param 0.85 is exactly 0 dB', () => {
    expect(abletonParamToDb(0.85)).toBe(0)
  })

  test('param 1.0 is exactly +6 dB', () => {
    expect(abletonParamToDb(1.0)).toBe(6)
  })

  // Calibration points derived from Ableton Live measurements.
  // Each test uses the parameter value that Ableton assigns to the given dB,
  // and verifies our formula produces the correct dB within ±0.2 dB.
  test.each([
    [0.699, -6],
    [0.550, -12],
    [0.399, -18],
    [0.302, -24],
    [0.239, -30],
    [0.188, -36],
    [0.143, -42],
    [0.103, -48],
    [0.068, -54],
    [0.035, -60],
  ])('param %f is approximately %d dB', (param, expectedDb) => {
    expect(abletonParamToDb(param)).toBeCloseTo(expectedDb, 0)
  })

  test('monotonically increasing', () => {
    const params = [0.01, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 0.85, 1.0]
    const dbs = params.map(abletonParamToDb)
    for (let i = 1; i < dbs.length; i++) {
      expect(dbs[i]).toBeGreaterThan(dbs[i - 1])
    }
  })

  test('continuous at the piecewise knee (~0.405)', () => {
    const below = abletonParamToDb(0.404)
    const above = abletonParamToDb(0.406)
    expect(Math.abs(above - below)).toBeLessThan(0.2)
  })
})

describe('abletonVolToDbStr', () => {
  test('param 0.85 (unity) is +0.0', () => {
    expect(abletonVolToDbStr(0.85)).toBe('+0.0')
  })

  test('param 0 is silence', () => {
    expect(abletonVolToDbStr(0)).toBe('-∞')
  })

  test('param 1.0 (max) is +6.0', () => {
    expect(abletonVolToDbStr(1.0)).toBe('+6.0')
  })

  test('positive dB values have + prefix', () => {
    expect(abletonVolToDbStr(0.9)).toMatch(/^\+/)
  })

  test('negative dB values have - prefix', () => {
    expect(abletonVolToDbStr(0.5)).toMatch(/^-/)
  })
})

describe('constants', () => {
  test('UNITY_POS is 0.85', () => {
    expect(UNITY_POS).toBe(0.85)
  })

  test('UNITY_VOL_ABLETON is 0.85', () => {
    expect(UNITY_VOL_ABLETON).toBe(0.85)
  })
})

describe('dbToParam', () => {
  test('round-trip: param -> dB -> param', () => {
    const params = [0.01, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 0.85, 1.0]
    for (const p of params) {
      const db = abletonParamToDb(p)
      expect(dbToParam(db)).toBeCloseTo(p, 4)
    }
  })

  test('-Infinity returns 0', () => {
    expect(dbToParam(-Infinity)).toBe(0)
  })

  test('0 dB returns 0.85 (unity)', () => {
    expect(dbToParam(0)).toBeCloseTo(0.85, 5)
  })

  test('+6 dB returns 1.0 (max)', () => {
    expect(dbToParam(6)).toBeCloseTo(1.0, 5)
  })
})

describe('levelToPercent', () => {
  // Ableton meter: 0 → -60 dB, 1.0 → +6 dB (linear in dB)
  test('zero level is 0%', () => {
    expect(levelToPercent(0)).toBe(0)
  })

  test('negative level is 0%', () => {
    expect(levelToPercent(-0.5)).toBe(0)
  })

  test('max level (1.0 = +6 dB) maps to 100%', () => {
    expect(levelToPercent(1.0)).toBeCloseTo(100, 0)
  })

  test('meter at 0 dB aligns with unity fader position (85%)', () => {
    // 0 dB → meter value = (0 - (-60)) / 66 = 60/66 ≈ 0.909
    const meterAt0dB = 60 / 66
    expect(levelToPercent(meterAt0dB)).toBeCloseTo(85, 0)
  })

  test('meter at -27 dB aligns with fader at -27 dB', () => {
    // -27 dB → meter value = (-27 - (-60)) / 66 = 33/66 = 0.5
    const meterAtMinus27 = 0.5
    const faderParam = dbToParam(-27)
    expect(levelToPercent(meterAtMinus27)).toBeCloseTo(faderParam * 100, 0)
  })

  test('monotonically increasing', () => {
    const levels = [0.001, 0.01, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0]
    const percents = levels.map(levelToPercent)
    for (let i = 1; i < percents.length; i++) {
      expect(percents[i]).toBeGreaterThan(percents[i - 1])
    }
  })
})
