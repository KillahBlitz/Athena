const SPRING = { type: 'spring', stiffness: 420, damping: 26 } as const
const FADE = { duration: 0.15, ease: 'linear' } as const

type Target = Record<string, number | number[]>

export interface MotionPresets {
  press: { whileHover: Target, whilePress: Target, transition: object }
  select: { animate: Target, transition: object }
  swap: { initial: Target, animate: Target, exit: Target, transition: object }
  celebrate: { initial: Target, animate: Target, transition: object }
  sparkle: { initial: Target, animate: Target, transition: object }
  breathe: { animate: Target, transition: object }
  react: { animate: Target, transition: object }
}

export function motionPresets(reduced: boolean): MotionPresets {
  if (reduced) {
    return {
      press: { whileHover: {}, whilePress: { opacity: 0.85 }, transition: FADE },
      select: { animate: { opacity: 1 }, transition: FADE },
      swap: { initial: { opacity: 0 }, animate: { opacity: 1 }, exit: { opacity: 0 }, transition: FADE },
      celebrate: { initial: { opacity: 0 }, animate: { opacity: 1 }, transition: { duration: 0.2 } },
      sparkle: { initial: { opacity: 0 }, animate: { opacity: [0, 1] }, transition: { duration: 0.2 } },
      breathe: { animate: {}, transition: { duration: 0 } },
      react: { animate: { opacity: [0.6, 1] }, transition: { duration: 0.2 } }
    }
  }

  return {
    press: { whileHover: { y: -2 }, whilePress: { scale: 0.96 }, transition: SPRING },
    select: { animate: { scale: [1, 1.06, 1] }, transition: { duration: 0.35, ease: 'easeOut' } },
    swap: {
      initial: { opacity: 0, x: 32 },
      animate: { opacity: 1, x: 0 },
      exit: { opacity: 0, x: -32 },
      transition: { duration: 0.3, ease: [0.16, 1, 0.3, 1] }
    },
    celebrate: { initial: { opacity: 0, scale: 0.9, y: 16 }, animate: { opacity: 1, scale: 1, y: 0 }, transition: SPRING },
    sparkle: {
      initial: { opacity: 0, scale: 0 },
      animate: { opacity: [0, 1, 0], scale: [0, 1.2, 0.6], y: [0, -28, -44] },
      transition: { duration: 1.1, ease: 'easeOut' }
    },
    breathe: {
      animate: { y: [0, -6, 0], scale: [1, 1.03, 1] },
      transition: { duration: 3.2, repeat: Infinity, ease: 'easeInOut' }
    },
    react: {
      animate: { rotate: [0, -10, 10, 0], scale: [1, 1.15, 1] },
      transition: { duration: 0.6, ease: 'easeOut' }
    }
  }
}
