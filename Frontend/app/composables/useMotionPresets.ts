import { computed } from 'vue'
import { useReducedMotion } from 'motion-v'
import { motionPresets } from '../config/motion'

export function useMotionPresets() {
  const reduced = useReducedMotion()
  return computed(() => motionPresets(reduced.value))
}
