<template>
  <Motion
    as="section"
    layout
    class="avatar-companion"
    :class="{ 'is-onboarding': onboarding, 'is-reminding': isReminding, 'is-midpoint': isMidpoint, 'is-celebrating': celebrating }"
    :transition="dockTransition"
    :aria-label="`Tu compañero ${avatar.name}`"
  >
    <button type="button" class="companion-touch" :aria-label="`Saludar a ${avatar.name}`" @click="interact('greeting')">
      <TrackingAvatar v-if="trackingEnabled" class="companion-tracking" :avatar-id="avatar.id" :name="avatar.name" />
      <img v-else :key="reaction" :src="avatar.image" alt="" :class="{ 'is-reacting': reaction > 0 }" width="72" height="72">
      <span>¡Salúdame!</span>
    </button>
    <span v-if="celebrating" class="companion-sparkles" aria-hidden="true">
      <span v-for="(sparkle, index) in SPARKLES" :key="index" class="companion-sparkle" :style="{ left: sparkle.left, top: sparkle.top, animationDelay: `${index * 0.25}s` }">✦</span>
    </span>
    <div class="companion-dialogue">
      <span v-if="celebrating" class="companion-celebration-badge">
        <span aria-hidden="true">✦</span>
        Etapa completada
      </span>
      <strong>{{ avatar.name }} <span v-if="showRole">· {{ avatar.role }}</span></strong>
      <AnimatePresence mode="wait">
        <Motion
          :key="messageKey"
          as="div"
          class="companion-message"
          role="status"
          aria-live="polite"
          aria-atomic="true"
          :initial="presets.dialogue.initial"
          :animate="presets.dialogue.animate"
          :exit="presets.dialogue.exit"
          :transition="presets.dialogue.transition"
        >
          <p class="companion-message-lead">{{ richMessage.lead }}</p>
          <ul v-if="richMessage.items?.length" class="companion-message-list">
            <li v-for="item in richMessage.items" :key="item.text">
              <span v-if="item.tag" class="companion-message-tag">{{ item.tag }}</span>
              <span v-else class="companion-message-bullet" aria-hidden="true">✦</span>
              <span>{{ item.text }}</span>
            </li>
          </ul>
          <p v-if="richMessage.outro" class="companion-message-outro">{{ richMessage.outro }}</p>
        </Motion>
      </AnimatePresence>
      <div v-if="stage !== 'personal' && !onboarding && !complete" class="companion-actions">
        <button type="button" @click="interact('tip')">Dame un consejo</button>
        <button type="button" @click="interact('cheer')">Necesito ánimo <span aria-hidden="true">✦</span></button>
      </div>
      <button v-else-if="onboarding" type="button" class="companion-start-btn" @click="dismiss">
        Comenzar <span aria-hidden="true">→</span>
      </button>
    </div>
  </Motion>
</template>

<script setup lang="ts">
import { computed, onUnmounted, ref, watch } from 'vue'
import type { Avatar } from '../../types/avatar'
import TrackingAvatar from './TrackingAvatar.vue'
import { useMotionPresets } from '../../composables/useMotionPresets'
import { AVATAR_CHEERS, RIASEC_TIPS } from '../../config/avatarMessages'

type Stage = 'personal' | 'objectives' | 'riasec' | 'waiting'
const props = withDefaults(defineProps<{
  avatar: Avatar
  stage: Stage
  name?: string
  trackingEnabled?: boolean
  complete?: boolean
  onboarding?: boolean
  notice?: string
  reminder?: string
  answerEvent?: { rating: number, id: number } | null
  revisitEvent?: { kind: 'answered' | 'rating' | 'justification', id: number } | null
  isLastBlock?: boolean
  block?: number
  totalBlocks?: number
  midpointPulse?: number
  confirmingFinish?: boolean
}>(), { name: '', complete: false, trackingEnabled: true, onboarding: false, notice: '', reminder: '', answerEvent: null, revisitEvent: null, isLastBlock: false, block: 0, totalBlocks: 0, midpointPulse: 0 })

const emit = defineEmits<{
  'dismiss-onboarding': []
}>()

const showRole = computed(() => props.stage !== 'objectives' || props.block <= 1)
const celebrating = computed(() => props.stage === 'objectives' && props.isLastBlock && props.complete && !props.onboarding)
const SPARKLES = [
  { left: '8%', top: '78%' },
  { left: '30%', top: '12%' },
  { left: '55%', top: '84%' },
  { left: '76%', top: '10%' },
  { left: '92%', top: '70%' }
]

const presets = useMotionPresets()
const dockTransition = computed(() =>
  props.onboarding
    ? { duration: 0 }
    : { type: 'spring', stiffness: 190, damping: 30, mass: 0.9 }
)

const ratingRule = 'Responde cada objetivo del 1 al 5, según qué tanto te identificas con él.'
const justificationRuleLow = 'Si marcas 1, no necesitas escribir nada.'
const justificationRuleMid = 'Si marcas 2 o 3, la justificación es opcional.'
const justificationRuleHigh = 'Si marcas 4 o 5, es obligatorio explicar tu respuesta.'

interface RichMessage {
  lead: string
  items?: { tag?: string, text: string }[]
  outro?: string
}
type Message = string | RichMessage

const objectivesRules: RichMessage['items'] = [
  { text: 'Responde cada objetivo del 1 al 5, según qué tanto te identificas con él.' },
  { tag: '1', text: 'No necesitas escribir nada.' },
  { tag: '2 - 3', text: 'La justificación es opcional.' },
  { tag: '4 - 5', text: 'Es obligatorio explicar tu respuesta.' }
]
const riasecRules: RichMessage['items'] = [
  { text: 'En cada dimensión, selecciona las habilidades con las que te identifiques.' },
  { text: 'Puedes marcar varias: no hay una única respuesta correcta.' },
  { text: 'Después responde una pregunta abierta explicando tu elección.' }
]
const startHint = 'Toca «Comenzar» cuando quieras empezar.'

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
  riasec: RIASEC_TIPS,
  waiting: [
    'Tus respuestas ya fueron enviadas. Puedes volver al inicio y regresar desde «Consultar mi evaluación».',
    'Mientras esperas, piensa qué actividades te gustaría conocer mejor de una carrera.',
    'La recomendación será un punto de partida para explorar tus opciones y conversar con un orientador.'
  ]
}
const cheers = AVATAR_CHEERS
const reaction = ref(0)
const tipIndex = ref(0)
const cheerIndex = ref(0)
const customMessage = ref<Message>('')
const isReminding = ref(false)
let remindTimer: ReturnType<typeof setTimeout> | null = null
const isMidpoint = ref(false)
let midpointTimer: ReturnType<typeof setTimeout> | null = null

const blockReminder = 'Aún te faltan objetivos por valorar en este bloque. Usa las flechas de la tarjeta para revisarlos antes de continuar.'

const blockPhrases: Record<string, string[]> = {
  atlas: ['Empecemos con calma. Cada valoración dice algo de ti.', 'Vas con buen ritmo. Sigue reflexionando con tranquilidad.', 'La constancia también es sabiduría. Continúa a tu paso.', 'Ya recorriste buen camino. Piensa en lo que de verdad te mueve.', 'Estás por cerrar esta etapa. Confía en lo que has pensado.'],
  nova: ['¡A explorar! Cada objetivo es una pista sobre ti.', '¡Qué buen avance! Sigamos descubriendo qué te interesa.', 'Tu curiosidad te trajo hasta aquí. Vamos por más.', 'Cada bloque dibuja mejor tu perfil. ¡Sigue así!', 'Casi terminas. Tus respuestas ya cuentan una historia.'],
  pixel: ['¡Nuevo bloque, nuevas ideas! Responde a tu manera.', '¡Buen ritmo! Deja que tu creatividad guíe tus respuestas.', 'Cada respuesta suma color a tu camino. ¡Sigue!', '¡Qué energía! Ya falta poco para completar el panorama.', 'Último tramo. Cierra con todo tu estilo.'],
  orion: ['Un nuevo horizonte se abre. Mira hacia lo que quieres lograr.', 'Avanzas con rumbo. Cada objetivo te acerca a tu visión.', 'Sigue explorando. Tu futuro se arma paso a paso.', 'Ya se ve más claro el camino. No pierdas el rumbo.', 'Estás llegando. Termina esta etapa con la mirada en el futuro.']
}

const defaultMotivation = computed(() => {
  const options = blockPhrases[props.avatar.id]
  if (props.stage === 'objectives' && props.block > 0 && options) {
    return options[(props.block - 1) % options.length]!
  }
  return (cheers[props.avatar.id] ?? [props.avatar.encouragement])[0]!
})

const greeting = computed<Message>(() => {
  const firstName = props.name.trim().split(/\s+/)[0]
  const base = `${props.avatar.greeting}${firstName ? `, ${firstName}` : ''}! Soy ${props.avatar.name}. ${props.stage === 'waiting' ? 'Te acompaño mientras esperas tus resultados.' : 'Vamos a descubrir lo que te interesa.'}`

  if (props.stage === 'objectives') {
    if (props.onboarding) {
      return { lead: base, items: objectivesRules, outro: startHint }
    }
    return defaultMotivation.value
  }
  if (props.stage === 'riasec') {
    if (props.onboarding) {
      return { lead: 'Así funciona esta sección:', items: riasecRules, outro: startHint }
    }
    return defaultMotivation.value
  }
  return base
})
const richMessage = computed<RichMessage>(() => {
  const current = customMessage.value || greeting.value
  return typeof current === 'string' ? { lead: current } : current
})
const messageKey = computed(() => JSON.stringify(richMessage.value))

function interact(action: 'greeting' | 'tip' | 'cheer') {
  reaction.value++
  if (action === 'greeting') {
    customMessage.value = reaction.value % 2 ? `¡Aquí estoy! ${props.avatar.encouragement}` : greeting.value
  } else if (action === 'tip') {
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

function remind() {
  customMessage.value = props.reminder || blockReminder
  reaction.value++
  isReminding.value = false
  if (remindTimer) clearTimeout(remindTimer)
  requestAnimationFrame(() => { isReminding.value = true })
  remindTimer = setTimeout(() => { isReminding.value = false }, 1600)
}

defineExpose({ remind })

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

const midpointPhrases: Record<string, string> = {
  atlas: '¡Ya vas a la mitad! Respira, lo estás haciendo muy bien. Falta poco.',
  nova: '¡Mitad del camino! Lo que queda se va a pasar volando.',
  pixel: '¡Ya llevas la mitad! Un último empujón y terminamos.',
  orion: '¡Vas a la mitad del recorrido! Ya falta poco para llegar.'
}

watch(() => props.midpointPulse, (pulse) => {
  if (!pulse || props.stage !== 'objectives') return
  const phrase = midpointPhrases[props.avatar.id] ?? '¡Ya vas a la mitad! Falta poco.'
  customMessage.value = `Bloque ${props.block} de ${props.totalBlocks}. ${phrase}`
  reaction.value++
  isMidpoint.value = false
  if (midpointTimer) clearTimeout(midpointTimer)
  requestAnimationFrame(() => { isMidpoint.value = true })
  midpointTimer = setTimeout(() => { isMidpoint.value = false }, 1100)
})

watch(() => props.confirmingFinish, (confirming) => {
  if (!confirming || props.stage !== 'objectives') return
  customMessage.value = {
    lead: '¿Estás seguro de que quieres finalizar?',
    outro: 'Si quieres revisar, toca «Revisar bloques».'
  }
  reaction.value++
})

watch(() => [props.avatar.id, props.stage], () => {
  customMessage.value = ''
  tipIndex.value = 0
  cheerIndex.value = 0
  reaction.value = 0
})
onUnmounted(() => {
  if (remindTimer) clearTimeout(remindTimer)
  if (midpointTimer) clearTimeout(midpointTimer)
})

const ratingReactions: Record<number, string[]> = {
  1: ['Anotado: este objetivo no va contigo, y está bien.', 'Gracias por ser sincero. Saber qué no te atrae también orienta.', 'Un 1 también dice mucho de ti. Sigamos.'],
  2: ['Te interesa poco, entendido. Pasemos al siguiente.', 'Algo de curiosidad, pero sin mucha emoción. Apuntado.', 'Vale, no te llama demasiado. Seguimos.'],
  3: ['Un punto medio: ni mucho ni poco. Apuntado.', 'Te genera dudas, y es normal. Sigamos explorando.', 'Término medio anotado. Vamos con la siguiente.'],
  4: ['¡Te gusta bastante! Buena señal.', 'Eso suena a algo que podrías disfrutar. ¡Bien!', '¡Me gusta tu respuesta! Esto dice algo de ti.'],
  5: ['¡Te encantó! Gracias por contarme por qué.', '¡Un 5! Eso te apasiona de verdad.', '¡Qué entusiasmo! Esto dice mucho de ti.']
}
watch(() => props.answerEvent, (event) => {
  if (!event || props.onboarding || props.stage !== 'objectives') return
  const options = ratingReactions[event.rating]
  if (!options) return
  customMessage.value = options[event.id % options.length]!
  reaction.value++
})

const revisitPhrases: Record<'answered' | 'rating' | 'justification', string[]> = {
  answered: ['¿Quieres cambiar tu respuesta?', '¿Se te olvidó contarme algo más sobre este objetivo?', 'Puedes ajustar tu valoración o ampliar lo que escribiste.', 'Volviste a esta. ¿Quieres revisar lo que respondiste?'],
  rating: ['Esta la pasaste de largo. ¿Quieres contestarla ahora?', '¿Te animas a valorar este objetivo?', 'Aún no me cuentas qué opinas de esta. ¿La respondemos?'],
  justification: ['Marcaste un 4 o un 5, pero se te olvidó contarme por qué. ¿Me lo explicas?', 'Falta tu justificación. ¿Qué te atrae de este objetivo?']
}
watch(() => props.revisitEvent, (event) => {
  if (!event || props.onboarding || props.stage !== 'objectives') return
  const options = revisitPhrases[event.kind]
  customMessage.value = options[event.id % options.length]!
  reaction.value++
})

watch(() => props.complete, (complete, previous) => {
  if (!complete || previous) return
  if (props.stage === 'riasec') {
    customMessage.value = '¡Has completado esta dimensión! Puedes revisar tu reflexión o continuar.'
  } else if (props.stage === 'objectives' && props.isLastBlock) {
    customMessage.value = {
      lead: '¡Completaste todos los objetivos de esta área!',
      outro: 'Revisa o cambia tus valoraciones si quieres, y finaliza para pasar a RISEC.'
    }
  } else {
    customMessage.value = '¡Has completado este bloque! Puedes revisar tus respuestas o dar el siguiente paso.'
  }
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
  position: relative;
  z-index: 45;
}

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
  animation: companion-start-breathe 2.4s ease-in-out infinite;
}
.companion-start-btn:hover { animation-play-state: paused; transform: scale(1.04); }
@keyframes companion-start-breathe {
  0%, 100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(var(--color-primary-rgb), 0.45); }
  50% { transform: scale(1.06); box-shadow: 0 0 0 12px rgba(var(--color-primary-rgb), 0); }
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
.companion-message { margin-block: 0.5rem 0.85rem; }
.companion-message p { margin: 0; line-height: 1.6; font-size: 0.95rem; }
.companion-message-lead { font-weight: 600; }
.companion-message-list {
  display: grid;
  gap: 0.45rem;
  margin: 0.65rem 0 0;
  padding: 0.7rem 0.85rem;
  list-style: none;
  border-radius: var(--radius-xl);
  background: var(--color-surface);
  border: 1px solid var(--color-primary-border);
}
.companion-message-list li {
  display: flex;
  align-items: baseline;
  gap: 0.6rem;
  font-size: 0.9rem;
  line-height: 1.5;
}
.companion-message-bullet { flex: 0 0 auto; color: var(--color-primary); font-size: 0.75rem; }
.companion-message-tag {
  flex: 0 0 auto;
  min-width: 2.6rem;
  padding: 0.1rem 0.5rem;
  border-radius: var(--radius-full);
  background: var(--gradient-primary, var(--color-primary));
  color: var(--color-on-primary);
  font-size: 0.72rem;
  font-weight: 800;
  text-align: center;
}
.companion-message-outro { margin-top: 0.65rem !important; color: var(--color-primary); font-weight: 700; }
.avatar-companion.is-onboarding .companion-message p { font-size: 1rem; line-height: 1.6; }
.avatar-companion.is-onboarding .companion-message-list li { font-size: 0.95rem; }
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
.avatar-companion.is-celebrating {
  background: var(--gradient-brand-soft, var(--color-primary-light));
  border: 1.5px solid var(--color-primary);
  box-shadow: var(--shadow-glow);
  animation: companion-celebrate-in 700ms cubic-bezier(0.16, 1, 0.3, 1) both;
}
@keyframes companion-celebrate-in {
  0% { transform: scale(0.97); box-shadow: 0 0 0 0 rgba(var(--color-primary-rgb), 0.5); }
  60% { transform: scale(1.015); box-shadow: 0 0 0 16px rgba(var(--color-primary-rgb), 0); }
  100% { transform: scale(1); }
}
.companion-celebration-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.25rem 0.75rem;
  margin-bottom: 0.5rem;
  border-radius: var(--radius-full);
  background: var(--gradient-primary, var(--color-primary));
  color: var(--color-on-primary);
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}
.companion-sparkles {
  position: absolute;
  inset: 0;
  overflow: hidden;
  border-radius: inherit;
  pointer-events: none;
}
.companion-sparkle {
  position: absolute;
  font-size: 1rem;
  color: var(--color-accent);
  opacity: 0;
  animation: companion-sparkle 2.4s ease-in-out infinite;
}
@keyframes companion-sparkle {
  0%, 100% { opacity: 0; transform: translateY(6px) scale(0.6); }
  50% { opacity: 1; transform: translateY(-6px) scale(1.1); }
}
button:focus-visible { outline: 3px solid var(--color-primary); outline-offset: 3px; }
.is-reacting { animation: companion-wave 550ms ease; }

.avatar-companion.is-reminding {
  animation: companion-remind-breathe 1.6s ease-in-out;
}
.avatar-companion.is-midpoint {
  animation: companion-midpoint-pulse 700ms cubic-bezier(0.34, 1.56, 0.64, 1) 200ms both;
}
@keyframes companion-midpoint-pulse {
  0% { scale: 1; box-shadow: 0 0 0 0 rgba(var(--color-primary-rgb), 0.45); }
  35% { scale: 1.025; box-shadow: 0 0 0 8px rgba(var(--color-primary-rgb), 0.25); }
  100% { scale: 1; box-shadow: 0 0 0 0 rgba(var(--color-primary-rgb), 0); }
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
  .avatar-companion.is-midpoint { animation: none; }
  .avatar-companion.is-onboarding { animation: none; }
  .companion-start-btn { animation: none; }
  .avatar-companion.is-celebrating { animation: none; }
  .companion-sparkle { animation: none; opacity: 0.7; }
}
</style>
