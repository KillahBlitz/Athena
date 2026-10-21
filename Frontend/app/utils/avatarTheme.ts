
type RGB = [number, number, number]

function clamp(value: number): number {
  return Math.max(0, Math.min(255, Math.round(value)))
}

function hexToRgb(hex: string): RGB {
  const normalized = hex.replace('#', '').trim()
  const full = normalized.length === 3
    ? normalized.split('').map(c => c + c).join('')
    : normalized
  const int = parseInt(full, 16)
  return [(int >> 16) & 255, (int >> 8) & 255, int & 255]
}

function rgbToHex([r, g, b]: RGB): string {
  return '#' + [r, g, b]
    .map(c => clamp(c).toString(16).padStart(2, '0'))
    .join('')
    .toUpperCase()
}

function mix(color: RGB, target: RGB, weight: number): RGB {
  return [
    color[0] + (target[0] - color[0]) * weight,
    color[1] + (target[1] - color[1]) * weight,
    color[2] + (target[2] - color[2]) * weight
  ]
}

const WHITE: RGB = [255, 255, 255]
const BLACK: RGB = [0, 0, 0]

export interface PrimaryScale {
  primary: string
  hover: string
  active: string
  light: string
  border: string
  rgb: string
}

export function buildPrimaryScale(baseColor: string): PrimaryScale {
  const base = hexToRgb(baseColor)
  return {
    primary: rgbToHex(base),
    hover: rgbToHex(mix(base, BLACK, 0.12)),
    active: rgbToHex(mix(base, BLACK, 0.24)),
    light: rgbToHex(mix(base, WHITE, 0.92)),
    border: rgbToHex(mix(base, WHITE, 0.6)),
    rgb: base.map(c => clamp(c)).join(', ')
  }
}

export function applyAvatarTheme(baseColor: string): void {
  if (typeof document === 'undefined') return
  const scale = buildPrimaryScale(baseColor)
  const root = document.documentElement.style
  root.setProperty('--color-primary', scale.primary)
  root.setProperty('--color-primary-hover', scale.hover)
  root.setProperty('--color-primary-active', scale.active)
  root.setProperty('--color-primary-light', scale.light)
  root.setProperty('--color-primary-border', scale.border)
  root.setProperty('--color-primary-rgb', scale.rgb)
  root.setProperty('--color-border-focus', scale.primary)
}
