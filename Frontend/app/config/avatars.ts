import type { Avatar } from '../types/avatar'

export const AVATARS: Avatar[] = [
  {
    id: 'atlas',
    name: 'Atlas',
    role: 'Sabio y Estratégico',
    image: '/avatars/atlas.svg',
    greeting: '¡Un honor acompañarte',
    encouragement: 'Tómate tu tiempo. Tu reflexión importa tanto como tu valoración.',
    color: '#F4C21B',
    theme: {
      primary: '#9C6B46',
      soft: '#FDF6EB',
      border: '#D1BA9C',
      dark: '#5C3818',
      contrast: '#FFFFFF'
    }
  },
  {
    id: 'nova',
    name: 'Nova',
    role: 'Curioso y Tecnológico',
    image: '/avatars/nova.svg',
    greeting: '¡Qué gusto conocerte',
    encouragement: 'Tómate tu tiempo. Tu reflexión importa tanto como tu valoración.',
    color: '#7C3AED',
    theme: {
      primary: '#7C3AED',
      soft: '#F5F3FF',
      border: '#DDD6FE',
      dark: '#4C1D95',
      contrast: '#FFFFFF'
    }
  },
  {
    id: 'pixel',
    name: 'Pixel',
    role: 'Creativo y Ágil',
    image: '/avatars/pixel.svg',
    greeting: '¡Qué genial tenerte aquí',
    encouragement: 'Tómate tu tiempo. Cada respuesta es una chispa para tu camino.',
    color: '#E25114',
    theme: {
      primary: '#E25114',
      soft: '#FFF7ED',
      border: '#FED7AA',
      dark: '#7C2D12',
      contrast: '#FFFFFF'
    }
  },
  {
    id: 'orion',
    name: 'Orion',
    role: 'Visionario y Explorador',
    image: '/avatars/orion.svg',
    greeting: '¡Listo para despegar contigo',
    encouragement: 'Tómate tu tiempo. Tu visión del futuro se construye paso a paso.',
    color: '#38BDF8',
    theme: {
      primary: '#0284C7',
      soft: '#F0F9FF',
      border: '#BAE6FD',
      dark: '#0369A1',
      contrast: '#FFFFFF'
    }
  }
]

export const DEFAULT_AVATAR: Avatar = AVATARS[1] ?? {
  id: 'nova',
  name: 'Nova',
  role: 'Curioso y Tecnológico',
  image: '/avatars/nova.svg',
  greeting: '¡Qué gusto conocerte',
  encouragement: 'Tómate tu tiempo. Tu reflexión importa tanto como tu valoración.',
  color: '#7C3AED',
  theme: {
    primary: '#7C3AED',
    soft: '#F5F3FF',
    border: '#DDD6FE',
    dark: '#4C1D95',
    contrast: '#FFFFFF'
  }
}
