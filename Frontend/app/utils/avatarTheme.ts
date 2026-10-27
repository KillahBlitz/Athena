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

function relativeLuminance([r, g, b]: RGB): number {
  const [lr, lg, lb] = [r, g, b].map((channel) => {
    const c = clamp(channel) / 255
    return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4
  }) as RGB
  return 0.2126 * lr + 0.7152 * lg + 0.0722 * lb
}

export function contrastRatio(foreground: string, background: string): number {
  const a = relativeLuminance(hexToRgb(foreground))
  const b = relativeLuminance(hexToRgb(background))
  return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05)
}

const WHITE: RGB = [255, 255, 255]
const BLACK: RGB = [0, 0, 0]
const ON_PRIMARY = '#FFFFFF'
const MIN_TEXT_CONTRAST = 4.5
const DARKEN_STEPS = 50

function lightTint(color: RGB): RGB {
  return mix(color, WHITE, 0.92)
}

function accessiblePrimary(base: RGB): RGB {
  let color = base
  for (let step = 0; step <= DARKEN_STEPS; step++) {
    color = mix(base, BLACK, step / DARKEN_STEPS)
    const hex = rgbToHex(color)
    const readableOnIt = contrastRatio(ON_PRIMARY, hex) >= MIN_TEXT_CONTRAST
    const readableOnTint = contrastRatio(hex, rgbToHex(lightTint(color))) >= MIN_TEXT_CONTRAST
    if (readableOnIt && readableOnTint) return color
  }
  return color
}

export interface PrimaryScale {
  primary: string
  hover: string
  active: string
  light: string
  border: string
  rgb: string
  accent: string
  onPrimary: string
}

export function buildPrimaryScale(baseColor: string): PrimaryScale {
  const original = hexToRgb(baseColor)
  const base = accessiblePrimary(original)
  return {
    primary: rgbToHex(base),
    hover: rgbToHex(mix(base, BLACK, 0.12)),
    active: rgbToHex(mix(base, BLACK, 0.24)),
    light: rgbToHex(lightTint(base)),
    border: rgbToHex(mix(base, WHITE, 0.6)),
    rgb: base.map(c => clamp(c)).join(', '),
    accent: rgbToHex(original),
    onPrimary: ON_PRIMARY
  }
}

export function applyStepperAccent(baseColor: string | null): void {
  if (typeof document === 'undefined') return
  const root = document.documentElement.style
  const names = ['--avatar-line', '--avatar-primary', '--avatar-primary-active', '--avatar-primary-light', '--avatar-primary-border']
  if (!baseColor) {
    names.forEach(name => root.removeProperty(name))
    return
  }
  const scale = buildPrimaryScale(baseColor)
  root.setProperty('--avatar-line', scale.accent)
  root.setProperty('--avatar-primary', scale.primary)
  root.setProperty('--avatar-primary-active', scale.active)
  root.setProperty('--avatar-primary-light', scale.light)
  root.setProperty('--avatar-primary-border', scale.border)
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
  root.setProperty('--color-accent', scale.accent)
  root.setProperty('--color-on-primary', scale.onPrimary)
}
