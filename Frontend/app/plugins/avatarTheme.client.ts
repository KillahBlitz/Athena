import { watch } from 'vue'
import { defineNuxtPlugin } from '#app'
import { useAthenaSessionStore } from '../stores/athenaSession'
import { applyAvatarTheme, applyStepperAccent } from '../utils/avatarTheme'

export default defineNuxtPlugin(() => {
  const session = useAthenaSessionStore()

  watch(
    () => session.selectedAvatar.color,
    (color) => {
      if (color) applyAvatarTheme(color)
    },
    { immediate: true }
  )

  watch(
    () => [session.avatarChosen, session.selectedAvatar.color] as const,
    ([chosen, color]) => {
      applyStepperAccent(chosen && color ? color : null)
    },
    { immediate: true }
  )
})
