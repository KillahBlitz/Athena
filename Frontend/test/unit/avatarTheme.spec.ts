import { describe, expect, it } from 'vitest'
import { AVATARS } from '../../app/config/avatars'
import { buildPrimaryScale, contrastRatio } from '../../app/utils/avatarTheme'

const PAGE_BACKGROUND = '#F9FAFC'
const WHITE = '#FFFFFF'

describe('contrastRatio', () => {
  it('calcula los extremos WCAG', () => {
    expect(contrastRatio('#000000', '#FFFFFF')).toBeCloseTo(21, 1)
    expect(contrastRatio('#FFFFFF', '#FFFFFF')).toBeCloseTo(1, 5)
  })
})

describe('buildPrimaryScale', () => {
  it.each(AVATARS.map(a => [a.name, a.color]))(
    'con %s (%s) el texto sobre primary y primary sobre sus tintes cumplen AA',
    (_name, color) => {
      const scale = buildPrimaryScale(color)

      expect(contrastRatio(scale.onPrimary, scale.primary)).toBeGreaterThanOrEqual(4.5)
      expect(contrastRatio(scale.primary, scale.light)).toBeGreaterThanOrEqual(4.5)
      expect(contrastRatio(scale.primary, PAGE_BACKGROUND)).toBeGreaterThanOrEqual(3)
    }
  )

  it('conserva el color original del avatar como acento', () => {
    expect(buildPrimaryScale('#F4C21B').accent).toBe('#F4C21B')
  })

  it('no altera un color que ya cumple AA', () => {
    const scale = buildPrimaryScale('#7C3AED')

    expect(scale.primary).toBe('#7C3AED')
    expect(scale.onPrimary).toBe(WHITE)
    expect(scale.rgb).toBe('124, 58, 237')
  })

  it('oscurece un color claro hasta cumplir AA sin cambiar de tono', () => {
    const scale = buildPrimaryScale('#38BDF8')

    expect(scale.primary).not.toBe('#38BDF8')
    const [r, g, b] = scale.rgb.split(', ').map(Number)
    expect(b).toBeGreaterThan(r!)
    expect(g).toBeGreaterThan(r!)
  })
})
