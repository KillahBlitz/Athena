<template>
  <!--
    When `onboarding` is true this renders as a fixed, centered overlay card
    (see .is-onboarding below). The `layout` prop makes motion-v animate the
    transition automatically: once the user swipes it away (or taps "Comenzar"),
    `onboarding` flips to false, the card drops out of `position: fixed` back
    into its normal docked slot, and motion-v tweens that layout change into a
    smooth "fly to place" animation instead of a hard jump.
  -->
  <Motion
    as="section"
    layout
    class="avatar-companion"
    :class="{ 'is-onboarding': onboarding, 'is-reminding': isReminding }"
    :transition="dockTransition"
    :aria-label="`Tu compañero ${avatar.name}`"
  >
    <button type="button" class="companion-touch" :aria-label="`Saludar a ${avatar.name}`" @click="interact('greeting')">
      <TrackingAvatar v-if="trackingEnabled" class="companion-tracking" :avatar-id="avatar.id" :name="avatar.name" />
      <img v-else :key="reaction" :src="avatar.image" alt="" :class="{ 'is-reacting': reaction > 0 }" width="72" height="72">
      <span>¡Salúdame!</span>
    </button>
    <div class="companion-dialogue">
      <strong>{{ avatar.name }} <span>· {{ avatar.role }}</span></strong>
      <AnimatePresence mode="wait">
        <Motion
          :key="message"
          as="p"
          role="status"
          aria-live="polite"
          aria-atomic="true"
          :initial="presets.dialogue.initial"
          :animate="presets.dialogue.animate"
          :exit="presets.dialogue.exit"
          :transition="presets.dialogue.transition"
        >
          {{ message }}
        </Motion>
      </AnimatePresence>
      <div v-if="stage !== 'personal' && !onboarding && !isLastBlock" class="companion-actions">
        <button type="button" @click="interact('tip')">Dame un consejo</button>
        <button type="button" @click="interact('cheer')">Necesito ánimo <span aria-hidden="true">✦</span></button>
      </div>
      <button v-else-if="onboarding" type="button" class="companion-start-btn" @click="dismiss">
        Comenzar <span aria-hidden="true">→</span>
      </button>

      <!-- Block navigation lives here instead of a separate bar on the page. -->
      <template v-if="nextLabel && !onboarding">
        <p class="companion-block-hint">¿Quieres cambiar de bloque?</p>
        <div class="companion-block-nav" :class="{ 'is-final': isLastBlock }">
          <button type="button" class="block-nav-btn is-back" @click="$emit('go-back')">
            <span aria-hidden="true">←</span>
            <span>Atrás</span>
          </button>
          <button
            type="button"
            class="block-nav-btn is-next"
            :class="{ 'is-soft-disabled': nextDisabled }"
            :aria-disabled="nextDisabled"
            @click="handleNextClick"
          >
            <span>{{ nextLabel }}</span>
            <span aria-hidden="true">→</span>
          </button>
        </div>
      </template>
    </div>
  </Motion>
</template>

<script setup lang="ts">
import { computed, onUnmounted, ref, watch } from 'vue'
import type { Avatar } from '../../types/avatar'
import TrackingAvatar from './TrackingAvatar.vue'
import { useMotionPresets } from '../../composables/useMotionPresets'

type Stage = 'personal' | 'objectives' | 'riasec' | 'waiting'
const props = withDefaults(defineProps<{
  avatar: Avatar
  stage: Stage
  name?: string
  trackingEnabled?: boolean
  complete?: boolean
  /** Shows the one-time "how this section works" intro as an overlay, dismissed with the "Comenzar" button. */
  onboarding?: boolean
  /** Label for the "next block" action. When set, shows block navigation inside the companion box. */
  notice?: string
  reminder?: string
  nextLabel?: string
  nextDisabled?: boolean
  /** On the last block, "Finalizar etapa" stacks below "Atrás" and spans the full width. */
  isLastBlock?: boolean
  block?: number
  totalBlocks?: number
}>(), { name: '', complete: false, trackingEnabled: true, onboarding: false, notice: '', reminder: '', nextLabel: '', nextDisabled: false, isLastBlock: false, block: 0, totalBlocks: 0 })

const emit = defineEmits<{
  'dismiss-onboarding': []
  'go-back': []
  'go-next': []
}>()

const presets = useMotionPresets()
const dockTransition = computed(() =>
  props.onboarding
    ? { duration: 0 }
    : { type: 'spring', stiffness: 190, damping: 30, mass: 0.9 }
)

// Scoring rules reminder: shown inside the onboarding overlay as one message,
// and afterwards split into two separate tips (rating, then justification)
// when the user explicitly asks for advice.
const ratingRule = 'Responde cada objetivo del 1 al 5, según qué tanto te identificas con él.'
const justificationRuleLow = 'Si marcas 1, no necesitas escribir nada.'
const justificationRuleMid = 'Si marcas entre 2 y 4, la justificación es opcional.'
const justificationRuleHigh = 'Si marcas 5, es obligatorio explicar tu respuesta.'
const objectivesRules = `${ratingRule} ${justificationRuleLow} ${justificationRuleMid} ${justificationRuleHigh}`

// How-this-section-works explanation shown once, inside the onboarding
// overlay, the first time the user lands on /riasec.
const riasecRules = 'En cada dimensión seleccionas las habilidades con las que te identifiques: puedes marcar varias, no hay una única respuesta correcta. Después respondes una pregunta abierta explicando tu elección.'

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
const isReminding = ref(false)
let remindTimer: ReturnType<typeof setTimeout> | null = null

const blockReminder = 'Aún te faltan objetivos por valorar en este bloque. Usa las flechas de la tarjeta para revisarlos antes de continuar.'

// Once onboarding is done, the default dialogue shows a motivational phrase
// for this avatar instead of any explanation.
const blockPhrases: Record<string, string[]> = {
  atlas: ['Empecemos con calma. Cada valoración dice algo de ti.', 'Vas con buen ritmo. Sigue reflexionando con tranquilidad.', 'La constancia también es sabiduría. Continúa a tu paso.', 'Ya recorriste buen camino. Piensa en lo que de verdad te mueve.', 'Estás por cerrar esta etapa. Confía en lo que has pensado.'],
  nova: ['¡A explorar! Cada objetivo es una pista sobre ti.', '¡Qué buen avance! Sigamos descubriendo qué te interesa.', 'Tu curiosidad te trajo hasta aquí. Vamos por más.', 'Cada bloque dibuja mejor tu perfil. ¡Sigue así!', 'Casi terminas. Tus respuestas ya cuentan una historia.'],
  pixel: ['¡Nuevo bloque, nuevas ideas! Responde a tu manera.', '¡Buen ritmo! Deja que tu creatividad guíe tus respuestas.', 'Cada respuesta suma color a tu camino. ¡Sigue!', '¡Qué energía! Ya falta poco para completar el panorama.', 'Último tramo. Cierra con todo tu estilo.'],
  orion: ['Un nuevo horizonte se abre. Mira hacia lo que quieres lograr.', 'Avanzas con rumbo. Cada objetivo te acerca a tu visión.', 'Sigue explorando. Tu futuro se arma paso a paso.', 'Ya se ve más claro el camino. No pierdas el rumbo.', 'Estás llegando. Termina esta etapa con la mirada en el futuro.']
}

const defaultMotivation = computed(() => {
  const options = blockPhrases[props.avatar.id]
  if (props.stage === 'objectives' && props.block > 0 && options) {
    const phrase = options[(props.block - 1) % options.length]!
    const label = props.totalBlocks > 0 ? `Bloque ${props.block} de ${props.totalBlocks}. ` : `Bloque ${props.block}. `
    return `${label}${phrase}`
  }
  return (cheers[props.avatar.id] ?? [props.avatar.encouragement])[0]!
})

const greeting = computed(() => {
  const firstName = props.name.trim().split(/\s+/)[0]
  const base = `${props.avatar.greeting}${firstName ? `, ${firstName}` : ''}! Soy ${props.avatar.name}. ${props.stage === 'waiting' ? 'Te acompaño mientras esperas tus resultados.' : 'Vamos a descubrir lo que te interesa.'}`

  if (props.stage === 'objectives') {
    // First time ever on /objetivos: explain the scoring rules.
    if (props.onboarding) {
      return `${base} ${objectivesRules} Toca «Comenzar» cuando quieras empezar.`
    }
    return defaultMotivation.value
  }
  if (props.stage === 'riasec') {
    // First time ever on /riasec: explain how selecting works here.
    if (props.onboarding) {
      return `${base} ${riasecRules} Toca «Comenzar» cuando quieras empezar.`
    }
    return defaultMotivation.value
  }
  return base
})
const message = computed(() => customMessage.value || greeting.value)

function interact(action: 'greeting' | 'tip' | 'cheer') {
  reaction.value++
  if (action === 'greeting') {
    customMessage.value = reaction.value % 2 ? `¡Aquí estoy! ${props.avatar.encouragement}` : greeting.value
  } else if (action === 'tip') {
    // On the objectives stage, cycle the rating rule and each justification
    // case (1, 2-4, 5) as separate tips, then the regular reflection tips.
    const options = props.stage === 'objectives'
      ? [ratingRule, justificationRuleLow, justificationRuleMid, justificationRuleHigh, ...tips.objectives]
      : tips[props.stage]
    customMessage.value = options[tipIndex.value++ % options.length]!
  } else {
    const options = cheers[props.avatar.id] ?? [props.avatar.encouragement]
    customMessage.value = options[cheerIndex.value++ % options.length]!
  }
}

function dismiss() {
  emit('dismiss-onboarding')
}

function handleNextClick() {
  if (!props.nextDisabled) {
    emit('go-next')
    return
  }
  // Block isn't finished yet: remind the user with a "breathing" pulse
  // around the companion box instead of silently doing nothing.
  customMessage.value = props.reminder || blockReminder
  reaction.value++
  isReminding.value = false
  if (remindTimer) clearTimeout(remindTimer)
  requestAnimationFrame(() => { isReminding.value = true })
  remindTimer = setTimeout(() => { isReminding.value = false }, 1600)
}

watch(() => props.notice, (text, previous) => {
  if (text) {
    customMessage.value = text
    reaction.value++
  } else if (customMessage.value === previous) {
    customMessage.value = ''
  }
})

watch(() => props.block, () => {
  customMessage.value = props.notice
  tipIndex.value = 0
  cheerIndex.value = 0
})

watch(() => [props.avatar.id, props.stage], () => {
  customMessage.value = ''
  tipIndex.value = 0
  cheerIndex.value = 0
  reaction.value = 0
})
onUnmounted(() => {
  if (remindTimer) clearTimeout(remindTimer)
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
  /* Sits above the question card stack (z-index 40) so cards sliding out
     pass underneath it instead of covering it. */
  position: relative;
  z-index: 45;
}

/* First-visit onboarding: lifted above the question cards, draggable away. */
.avatar-companion.is-onboarding {
  position: fixed;
  inset: 0;
  margin: auto;
  width: min(760px, calc(100% - 2.5rem));
  height: fit-content;
  z-index: 60;
  flex-direction: column;
  align-items: stretch;
  padding: 1.5rem 1.75rem;
  background: var(--color-surface);
  box-shadow: var(--shadow-card-hover), 0 32px 64px -24px rgba(0, 0, 0, 0.35);
  animation: companion-onboarding-in 360ms cubic-bezier(0.16, 1, 0.3, 1) both;
}
@keyframes companion-onboarding-in {
  from { opacity: 0; translate: 0 18px; scale: 0.96; }
  to { opacity: 1; translate: 0 0; scale: 1; }
}
.avatar-companion.is-onboarding .companion-touch {
  align-self: center;
}
.avatar-companion.is-onboarding .companion-dialogue p {
  font-size: 1rem;
  line-height: 1.7;
}
@media (min-width: 640px) {
  .avatar-companion.is-onboarding {
    flex-direction: row;
    align-items: center;
    gap: 1.75rem;
  }
  .avatar-companion.is-onboarding .companion-touch {
    flex-basis: 130px;
  }
  .avatar-companion.is-onboarding .companion-tracking {
    width: 120px;
  }
}

.companion-start-btn {
  align-self: flex-start;
  min-height: 44px;
  padding: 0.5rem 1rem;
  margin-top: 0.25rem;
  border: none;
  border-radius: var(--radius-full);
  background: var(--gradient-primary, var(--color-primary));
  color: var(--color-on-primary);
  font-size: 0.85rem;
  font-weight: 700;
  cursor: pointer;
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
.companion-tracking { width: 72px; }
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

.companion-block-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

/* Last block: "Finalizar etapa" drops below "Atrás" and spans the row's
   full width (margins come from the companion box's own padding). */
.companion-block-nav.is-final {
  flex-direction: column;
  align-items: stretch;
  gap: 0.6rem;
}
.companion-block-nav.is-final .block-nav-btn.is-back {
  align-self: flex-start;
}
.companion-block-nav.is-final .block-nav-btn.is-next {
  width: 100%;
}
.block-nav-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  min-height: 44px;
  padding: 0 0.9rem;
  border-radius: var(--radius-full);
  font-size: 0.85rem;
  font-weight: 700;
  cursor: pointer;
}
.block-nav-btn.is-back {
  background: var(--color-surface);
  border: 1px solid var(--color-primary-border);
  color: var(--color-text-secondary);
}
.block-nav-btn.is-back:hover {
  color: var(--color-primary);
  border-color: var(--color-primary);
}
.block-nav-btn.is-next {
  flex: 1;
  justify-content: center;
  border: none;
  background: var(--gradient-primary, var(--color-primary));
  color: var(--color-on-primary);
  box-shadow: var(--shadow-glow);
  transition: transform var(--motion-base) ease, box-shadow var(--motion-base) ease, opacity var(--motion-base) ease;
}
.block-nav-btn.is-next:hover:not(:disabled) {
  transform: translateY(-1px);
}
.block-nav-btn.is-next.is-soft-disabled {
  opacity: 0.55;
  box-shadow: none;
}

.companion-block-hint {
  margin: 0.85rem 0 0.5rem;
  padding-top: 0.75rem;
  border-top: 1px dashed var(--color-primary-border);
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--color-text-secondary);
}
button:focus-visible { outline: 3px solid var(--color-primary); outline-offset: 3px; }
.is-reacting { animation: companion-wave 550ms ease; }

/* "Breathing" reminder pulse when the user tries to move on with an
   incomplete block: a glow that breathes outward around the whole box. */
.avatar-companion.is-reminding {
  animation: companion-remind-breathe 1.6s ease-in-out;
}
@keyframes companion-remind-breathe {
  0%, 100% { box-shadow: 0 0 0 0 rgba(var(--color-primary-rgb), 0.45); }
  50% { box-shadow: 0 0 0 14px rgba(var(--color-primary-rgb), 0); }
}
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
  .avatar-companion.is-onboarding { width: calc(100% - 1.5rem); }
}
@media (prefers-reduced-motion: reduce) {
  .companion-touch img { animation: none; transition: none; }
  .companion-touch:hover img, .companion-touch:active img { transform: none; }
  .is-reacting { animation: none; }
  .avatar-companion.is-reminding { animation: none; }
  .avatar-companion.is-onboarding { animation: none; }
}
</style>
