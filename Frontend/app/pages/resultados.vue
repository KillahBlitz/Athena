<template>
  <div class="results-page">
    <header class="results-hero">
      <div class="results-hero-text reveal">
        <span class="results-eyebrow">
          <span aria-hidden="true">✦</span>
          <span>Expedición completada</span>
        </span>
        <h1 class="page-title results-title">Tu Perfil Vocacional</h1>
        <p class="page-description results-description">{{ summary }}</p>
      </div>

      <div class="results-hero-aside reveal" style="--reveal-index: 1">
        <div class="results-companion">
          <img
            class="results-companion-avatar"
            :src="selectedAvatar.image"
            :alt="`${selectedAvatar.name}, tu compañero`"
            width="96"
            height="96"
          >
          <p class="results-companion-bubble">¡Este es solo el comienzo{{ firstName ? `, ${firstName}` : '' }}!</p>
        </div>
        <span class="results-badge">
          <svg viewBox="0 0 20 20" width="16" height="16" fill="none" stroke="currentColor" aria-hidden="true">
            <circle cx="10" cy="8" r="5" stroke-width="1.6" />
            <path d="M7 12.2 L6 18 L10 16 L14 18 L13 12.2" stroke-width="1.6" stroke-linejoin="round" />
          </svg>
          Recorrido completado
        </span>
      </div>
    </header>

    <section class="results-paths reveal" style="--reveal-index: 2" aria-labelledby="results-paths-title" :aria-busy="state === 'loading'">
      <div class="results-paths-header">
        <h2 id="results-paths-title" class="results-paths-title">{{ state === 'low-match' ? 'Sin una recomendación clara' : pathsTitle }}</h2>
        <span v-if="state !== 'low-match'" class="results-paths-tag">TOP {{ careers.length || 3 }}</span>
      </div>

      <p v-if="state === 'loading'" class="results-status" role="status">Cargando tus resultados…</p>

      <div v-else-if="state === 'error'" class="results-status is-error" role="alert">
        <p>{{ errorMessage }}</p>
        <BaseButton variant="outline" size="sm" class="results-no-print" @click="loadResults">Reintentar</BaseButton>
      </div>

      <div v-else-if="state === 'low-match'" class="results-status results-low-match" role="status">
        <strong class="results-low-match-title">Esta área no parece ser la tuya, y eso también es un descubrimiento.</strong>
        <p>
          Tus respuestas no coinciden lo suficiente con las carreras de esta área como para recomendarte una con confianza.
          Es probable que tus intereses estén en otra área académica.
        </p>
        <p>Te recomendamos repetir el test eligiendo un área distinta.</p>
        <BaseButton class="results-no-print" @click="restartTest">Probar otra área</BaseButton>
      </div>

      <template v-else>
        <ol class="results-careers">
          <li v-for="career in careers" :key="career.rank">
            <CareerMatchCard :career="career" />
          </li>
        </ol>
        <p class="results-paths-note">Consulta los planes de estudio y requisitos de ingreso de cada institución.</p>
      </template>
    </section>

    <div v-if="state === 'ready'" class="results-closing">
      <div class="results-closing-text">
        <strong>Tu perfil es un punto de partida, no una etiqueta.</strong>
        <p>Sigue explorando. Tu camino lo construyes tú.</p>
      </div>

      <div class="results-download results-no-print">
        <BaseButton size="lg" @click="downloadPdf">
          <template #prefix>
            <svg viewBox="0 0 20 20" width="18" height="18" fill="none" stroke="currentColor" aria-hidden="true">
              <path d="M10 3 V13 M6 9 L10 13 L14 9 M4 16 H16" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </template>
          Descargar resultado en PDF
        </BaseButton>
        <span class="results-download-hint">En el diálogo, elige «Guardar como PDF» como destino.</span>
      </div>
    </div>

    <div v-if="state !== 'loading'" class="results-restart results-no-print">
      <BaseButton variant="outline" @click="restartTest">
        <template #prefix>
          <svg viewBox="0 0 20 20" width="16" height="16" fill="none" stroke="currentColor" aria-hidden="true">
            <path d="M4 10 A6 6 0 1 0 6 5.5 M4 3 V6.5 H7.5" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </template>
        Volver a hacer el test
      </BaseButton>
      <span class="results-restart-hint">Se borrarán tus respuestas y resultados de este navegador.</span>
    </div>

    <p class="results-disclaimer">
      <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" aria-hidden="true">
        <circle cx="8" cy="8" r="6.5" stroke-width="1.3" />
        <path d="M8 7.2 V11 M8 5 V5.1" stroke-width="1.5" stroke-linecap="round" />
      </svg>
      <span>El porcentaje estima qué tanto coinciden tus respuestas con cada carrera. Es una referencia para explorar opciones, no una evaluación definitiva.</span>
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import BaseButton from '../components/ui/BaseButton.vue'
import CareerMatchCard from '../features/resultados/components/CareerMatchCard.vue'
import { toCareerMatches } from '../features/resultados/utils/toCareerMatches'
import type { CareerMatch } from '../features/resultados/types'
import { useResultsApi } from '../composables/useResultsApi'
import { useAthenaSessionStore } from '../stores/athenaSession'
import { getEvaluationUuid } from '../utils/evaluationStorage'
import { getCachedResults, saveCachedResults } from '../utils/resultsStorage'

useHead({
  title: 'ATHENA | Resultados'
})

const router = useRouter()
const session = useAthenaSessionStore()
const { fetchResults } = useResultsApi()

const MIN_TOP_MATCH = 60

const state = ref<'loading' | 'ready' | 'error' | 'low-match'>('loading')
const errorMessage = ref('')
const careers = ref<CareerMatch[]>([])
let pendingRequest: AbortController | null = null

const selectedAvatar = computed(() => session.selectedAvatar)
const firstName = computed(() => session.name.trim().split(/\s+/)[0] ?? '')
const summary = computed(() => {
  const text = state.value === 'low-match'
    ? 'esta vez no encontramos una carrera que encaje claramente contigo en esta área.'
    : 'estas son las carreras del IPN que más coinciden con tus objetivos e intereses.'
  return firstName.value
    ? `${firstName.value}, ${text}`
    : `${text.charAt(0).toUpperCase()}${text.slice(1)}`
})

const PATHS_TITLES: Record<number, string> = {
  1: 'Un camino para explorar',
  2: 'Dos caminos para explorar'
}
const pathsTitle = computed(() => PATHS_TITLES[careers.value.length] ?? 'Tres caminos para explorar')

async function loadResults() {
  const uuid = getEvaluationUuid()
  if (!uuid) {
    await router.replace('/riasec')
    return
  }
  // Si ya obtuvimos los resultados antes, los mostramos directamente sin volver
  // a consultar la API. Así persisten aunque se cierre y reabra la ventana.
  const cached = getCachedResults(uuid)
  if (cached) {
    careers.value = toCareerMatches(cached)
    state.value = (careers.value[0]?.match ?? 0) < MIN_TOP_MATCH ? 'low-match' : 'ready'
    return
  }
  pendingRequest?.abort()
  const request = new AbortController()
  pendingRequest = request
  state.value = 'loading'
  try {
    const response = await fetchResults(uuid, request.signal)
    if (request.signal.aborted) return
    if (response.status_id !== 4) {
      await router.replace('/espera')
      return
    }
    saveCachedResults(uuid, response.results ?? [])
    careers.value = toCareerMatches(response.results)
    state.value = (careers.value[0]?.match ?? 0) < MIN_TOP_MATCH ? 'low-match' : 'ready'
  } catch (err) {
    if (request.signal.aborted) return
    errorMessage.value = err instanceof Error && err.message.startsWith('Tu evaluación')
      ? err.message
      : 'No pudimos cargar tus resultados. Revisa tu conexión e inténtalo de nuevo.'
    state.value = 'error'
  } finally {
    if (pendingRequest === request) pendingRequest = null
  }
}

async function restartTest() {
  const confirmed = window.confirm(
    '¿Quieres volver a hacer el test? Se borrarán tus respuestas y resultados guardados en este navegador. ' +
    'Si quieres conservarlos, descarga primero tu resultado en PDF.'
  )
  if (!confirmed) return
  pendingRequest?.abort()
  session.startOver()
  await router.replace('/')
}

onMounted(() => {
  session.restore()
  void loadResults()
})

onBeforeUnmount(() => {
  pendingRequest?.abort()
})

/**
 * Abre el diálogo de impresión del navegador con estilos de impresión dedicados.
 * Se renombra el documento temporalmente para que el PDF guardado tenga un nombre útil.
 */
function downloadPdf() {
  const previousTitle = document.title
  const suffix = firstName.value ? `-${firstName.value}` : ''
  document.title = `ATHENA-Perfil-Vocacional${suffix}`

  const restoreTitle = () => { document.title = previousTitle }
  window.addEventListener('afterprint', restoreTitle, { once: true })
  window.print()
}
</script>

<style scoped>
@import '../features/resultados/styles/results.css';
</style>

<style>
/* Reglas de impresión que afectan al layout global, limitadas a esta página. */
@media print {
  @page {
    size: A4 portrait;
    margin: 12mm;
  }

  body:has(.results-page) .athena-header,
  body:has(.results-page) .app-footer {
    display: none !important;
  }

  body:has(.results-page) .app-container {
    min-height: 0;
    background: #FFFFFF;
  }

  body:has(.results-page) .main-content {
    max-width: none;
    padding: 0;
  }

  body:has(.results-page) .reveal {
    animation: none !important;
  }
}
</style>
