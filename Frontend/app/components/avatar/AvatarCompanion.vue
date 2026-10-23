<template>
  <section class="avatar-companion" :aria-label="`Tu compañero ${avatar.name}`">
    <button type="button" class="companion-touch" :aria-label="`Saludar a ${avatar.name}`" @click="interact('greeting')">
      <img :key="reaction" :src="avatar.image" alt="" :class="{ 'is-reacting': reaction > 0 }" width="72" height="72">
      <span>¡Salúdame!</span>
    </button>
    <div class="companion-dialogue">
      <strong>{{ avatar.name }} <span>· {{ avatar.role }}</span></strong>
      <p role="status" aria-live="polite" aria-atomic="true">{{ message }}</p>
      <div class="companion-actions">
        <button type="button" @click="interact('tip')">Dame un consejo</button>
        <button type="button" @click="interact('cheer')">Necesito ánimo <span aria-hidden="true">✦</span></button>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { Avatar } from '../../types/avatar'

type Stage = 'personal' | 'objectives' | 'riasec' | 'waiting'
const props = withDefaults(defineProps<{
  avatar: Avatar
  stage: Stage
  name?: string
  complete?: boolean
}>(), { name: '', complete: false })

const tips: Record<Stage, string[]> = {
  personal: [
    'Elige al compañero que más te guste: te acompañará durante todo el recorrido.',
    'Escoge el área académica que quieras explorar. Tus respuestas hablarán de tus propios intereses.',
    'Revisa tus datos antes de continuar y busca un lugar donde puedas responder con calma.'
  ],
  objectives: [
    'Piensa si disfrutarías esta actividad en tu día a día, aunque todavía no sepas hacerla.',
    'Puedes apoyar tu respuesta con una experiencia de clase, de casa o de un proyecto.',
    'No necesitas valorar todo igual. Explica con tus palabras qué te atrae o qué no te interesa.'
  ],
  riasec: [
    'Selecciona las habilidades con las que te identifiques y responde la pregunta abierta para continuar.',
    'Para tu reflexión, recuerda una situación concreta: ¿qué hiciste y cómo te sentiste?',
    'Responde desde tu experiencia. No hace falta elegir una habilidad porque otras personas la prefieran.'
  ],
  waiting: [
    'Tus respuestas ya fueron enviadas. Puedes volver al inicio y regresar desde «Consultar mi evaluación».',
    'Mientras esperas, piensa qué actividades te gustaría conocer mejor de una carrera.',
    'La recomendación será un punto de partida para explorar tus opciones y conversar con un orientador.'
  ]
}
const cheers: Record<string, string[]> = {
  atlas: ['Paso a paso también se llega lejos. Date tiempo para pensar.', 'Tu experiencia merece ser escuchada. Confía en lo que has vivido.'],
  nova: ['¡Sigamos explorando! La curiosidad empieza con una pregunta.', 'No necesitas tener todas las respuestas sobre tu futuro hoy.'],
  pixel: ['¡Tu camino tiene sus propios colores! Exprésate a tu manera.', 'Una idea pequeña puede abrir muchas posibilidades. Dale espacio a la tuya.'],
  orion: ['Cada reflexión es un paso en tu exploración. Voy contigo.', 'No hace falta ver todo el horizonte para dar el siguiente paso.']
}
const reaction = ref(0)
const tipIndex = ref(0)
const cheerIndex = ref(0)
const customMessage = ref('')
const greeting = computed(() => {
  const firstName = props.name.trim().split(/\s+/)[0]
  return `${props.avatar.greeting}${firstName ? `, ${firstName}` : ''}! Soy ${props.avatar.name}. ${props.stage === 'waiting' ? 'Te acompaño mientras esperas tus resultados.' : 'Vamos a descubrir lo que te interesa.'}`
})
const message = computed(() => customMessage.value || greeting.value)

function interact(action: 'greeting' | 'tip' | 'cheer') {
  reaction.value++
  if (action === 'greeting') {
    customMessage.value = reaction.value % 2 ? `¡Aquí estoy! ${props.avatar.encouragement}` : greeting.value
  } else if (action === 'tip') {
    const options = tips[props.stage]
    customMessage.value = options[tipIndex.value++ % options.length]!
  } else {
    const options = cheers[props.avatar.id] ?? [props.avatar.encouragement]
    customMessage.value = options[cheerIndex.value++ % options.length]!
  }
}

watch(() => [props.avatar.id, props.stage], () => {
  customMessage.value = ''
  tipIndex.value = 0
  cheerIndex.value = 0
  reaction.value = 0
})
watch(() => props.complete, (complete, previous) => {
  if (!complete || previous) return
  customMessage.value = props.stage === 'riasec'
    ? '¡Has completado esta dimensión! Puedes revisar tu reflexión o continuar.'
    : '¡Has completado este bloque! Puedes revisar tus respuestas o dar el siguiente paso.'
  reaction.value++
})
</script>

<style scoped>
.avatar-companion {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1.1rem;
  margin-block: 1rem;
  border: 1px solid var(--color-primary-border);
  border-radius: var(--radius-2xl);
  background: var(--color-primary-light);
  text-align: left;
}
.companion-touch {
  display: grid;
  justify-items: center;
  flex: 0 0 80px;
  gap: 0.35rem;
  padding: 0.25rem;
  border-radius: var(--radius-xl);
  color: var(--color-primary);
  font-size: 0.72rem;
  font-weight: 700;
  cursor: pointer;
}
.companion-touch img { object-fit: contain; transition: transform 180ms ease; }
.companion-touch:hover img { transform: rotate(-6deg) scale(1.08); }
.companion-touch:active img { transform: scale(0.93); }
.companion-dialogue { flex: 1; min-width: 0; }
.companion-dialogue strong { color: var(--color-primary); font-size: 0.9rem; }
.companion-dialogue strong span { font-weight: 400; color: var(--color-text-secondary); }
.companion-dialogue p { margin-block: 0.5rem 0.85rem; line-height: 1.6; font-size: 0.95rem; }
.companion-actions { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.companion-actions button {
  min-height: 44px;
  padding: 0.5rem 0.8rem;
  border: 1px solid var(--color-primary-border);
  border-radius: var(--radius-full);
  background: var(--color-surface);
  color: var(--color-primary);
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
}
.companion-actions button:hover { border-color: var(--color-primary); }
button:focus-visible { outline: 3px solid var(--color-primary); outline-offset: 3px; }
.is-reacting { animation: companion-wave 550ms ease; }
@keyframes companion-wave {
  0%, 100% { transform: rotate(0) translateY(0); }
  30% { transform: rotate(-12deg) translateY(-7px); }
  65% { transform: rotate(10deg) translateY(-3px); }
}
@media (max-width: 480px) {
  .avatar-companion { gap: 0.6rem; padding: 0.85rem; }
  .companion-touch { flex-basis: 56px; }
  .companion-touch img { width: 52px; height: 52px; }
  .companion-dialogue strong span { display: block; }
}
@media (prefers-reduced-motion: reduce) {
  .companion-touch img { animation: none; transition: none; }
  .companion-touch:hover img, .companion-touch:active img { transform: none; }
}
</style>
