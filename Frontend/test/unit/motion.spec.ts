import { describe, expect, it } from 'vitest'
import { motionPresets } from '../../app/config/motion'

const TRANSFORM_KEYS = ['x', 'y', 'scale', 'scaleX', 'scaleY', 'rotate']

function collectKeys(value: unknown, keys = new Set<string>()): Set<string> {
  if (value && typeof value === 'object') {
    for (const [key, nested] of Object.entries(value)) {
      if (key !== 'transition') keys.add(key)
      collectKeys(nested, keys)
    }
  }
  return keys
}

function collectDurations(value: unknown, durations: number[] = []): number[] {
  if (value && typeof value === 'object') {
    for (const [key, nested] of Object.entries(value)) {
      if (key === 'duration' && typeof nested === 'number') durations.push(nested)
      collectDurations(nested, durations)
    }
  }
  return durations
}

describe('motionPresets', () => {
  it('con movimiento completo incluye desplazamientos y escalados', () => {
    const keys = collectKeys(motionPresets(false))

    expect(TRANSFORM_KEYS.some(k => keys.has(k))).toBe(true)
  })

  it('con movimiento reducido no anima transformaciones', () => {
    const keys = collectKeys(motionPresets(true))

    expect(TRANSFORM_KEYS.filter(k => keys.has(k))).toEqual([])
  })

  it('con movimiento reducido ninguna transición supera 0.2 s ni usa springs', () => {
    const presets = motionPresets(true)
    const durations = collectDurations(presets)

    expect(durations.length).toBeGreaterThan(0)
    expect(Math.max(...durations)).toBeLessThanOrEqual(0.2)
    expect(JSON.stringify(presets)).not.toContain('"spring"')
  })

  it('expone los mismos presets en ambos modos', () => {
    expect(Object.keys(motionPresets(true)).sort()).toEqual(Object.keys(motionPresets(false)).sort())
  })
})
