import { watch } from 'vue'
import { defineNuxtPlugin } from '#app'
import { useAthenaSessionStore } from '../stores/athenaSession'
import { applyAvatarTheme } from '../utils/avatarTheme'

export default defineNuxtPlugin(() => {
  const session = useAthenaSessionStore()

  watch(
    () => session.selectedAvatar.color,
    (color) => {
      if (color) applyAvatarTheme(color)
    },
    { immediate: true }
  )
})
