<template>
  <section id="application-details" class="intro-details-section" aria-labelledby="details-heading">
    <div class="details-header reveal" style="--reveal-index: 0">
      <span class="eyebrow">
        <span>✦</span>
        <span>APOYO VOCACIONAL</span>
      </span>
      <h2 id="details-heading">¿Qué es ATHENA?</h2>
      <p>
        ATHENA es un sistema web de apoyo para la orientación vocacional. A partir de tus respuestas, analiza la afinidad entre tu perfil y características de los programas académicos del Instituto Politécnico Nacional.
      </p>
      <p class="details-note">
        Los resultados funcionan como una referencia para explorar opciones académicas. ATHENA no sustituye tu decisión personal ni el acompañamiento de un orientador profesional.
      </p>
    </div>

    <div class="details-grid" aria-label="Beneficios de ATHENA">
      <article class="detail-card reveal" style="--reveal-index: 1">
        <div class="detail-icon-wrap" aria-hidden="true">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor">
            <circle cx="11" cy="11" r="6.5" stroke-width="2" />
            <path d="m16 16 4 4M11 8v6M8 11h6" stroke-width="2" stroke-linecap="round" />
          </svg>
        </div>
        <h3>Explora tu perfil</h3>
        <p>Reconoce los intereses, habilidades y objetivos que influyen en tu elección académica.</p>
      </article>

      <article class="detail-card reveal" style="--reveal-index: 2">
        <div class="detail-icon-wrap" aria-hidden="true">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor">
            <path d="M4 5h6v6H4zM14 13h6v6h-6zM10 8h4v8" stroke-width="2" stroke-linejoin="round" />
          </svg>
        </div>
        <h3>Compara tu afinidad</h3>
        <p>Relaciona tus respuestas con los objetivos y características de las carreras del IPN.</p>
      </article>

      <article class="detail-card reveal" style="--reveal-index: 3">
        <div class="detail-icon-wrap" aria-hidden="true">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor">
            <path d="M12 3 14.8 8.7 21 9.6l-4.5 4.4 1.1 6.2-5.6-2.9-5.6 2.9 1.1-6.2L3 9.6l6.2-.9z" stroke-width="2" stroke-linejoin="round" />
          </svg>
        </div>
        <h3>Conoce tus opciones</h3>
        <p>Obtén recomendaciones de programas académicos específicos dentro del área seleccionada.</p>
      </article>
    </div>

    <div class="roadmap-container reveal" style="--reveal-index: 4">
      <h3 class="roadmap-title">Las 5 etapas de tu recorrido</h3>
      <div class="roadmap-steps">
        <div class="roadmap-step-card reveal" style="--reveal-index: 1">
          <div class="step-badge-number">1</div>
          <h4>Introducción</h4>
          <p>Conoce el propósito y el funcionamiento de ATHENA.</p>
        </div>
        <div class="roadmap-step-card reveal" style="--reveal-index: 2">
          <div class="step-badge-number">2</div>
          <h4>Datos personales</h4>
          <p>Ingresa tus datos, selecciona un comañpero y elige el área académica que deseas explorar.</p>
        </div>
        <div class="roadmap-step-card reveal" style="--reveal-index: 3">
          <div class="step-badge-number">3</div>
          <h4>Objetivos</h4>
          <p>Valora qué tanto te identificas con los objetivos de las carreras del área seleccionada y explica las razones de tus elecciones.</p>
        </div>
        <div class="roadmap-step-card reveal" style="--reveal-index: 4">
          <div class="step-badge-number">4</div>
          <h4>RISEC</h4>
          <p>Explora tus intereses y habilidades mediante cinco dimensiones vocacionales y complementa tus respuestas.</p>
        </div>
        <div class="roadmap-step-card reveal" style="--reveal-index: 5">
          <div class="step-badge-number">5</div>
          <h4>Resultados</h4>
          <p>Consulta los programas académicos que presentan mayor afinidad con tu perfil.</p>
        </div>
      </div>
    </div>

    <div class="before-start section-block">
      <div>
        <span class="eyebrow"><span>✦</span><span>ANTES DE COMENZAR</span></span>
        <p>Selecciona el área académica que deseas explorar y responde cada apartado con sinceridad. No existen respuestas correctas o incorrectas; lo importante es que tus elecciones representen tus intereses y preferencias.</p>
      </div>
      <ul class="guidance-list">
        <li>Lee cuidadosamente cada pregunta.</li>
        <li>Responde desde tu experiencia e intereses personales.</li>
        <li>Explica detalladamente tus respuestas cuando se solicite.</li>
        <li>Debes ser honesto con tus respuestas.</li>
        <li>Completa todas las etapas para obtener tus resultados.</li>
      </ul>
    </div>

    <div class="considerations section-block">
      <div class="section-block-heading">
        <span class="eyebrow"><span>✦</span><span>TEN EN CUENTA</span></span>
        <h2>Tu experiencia es única</h2>
      </div>
      <div class="consideration-grid">
        <article v-for="item in considerations" :key="item.title" class="consideration-item">
          <span class="consideration-marker" aria-hidden="true">✓</span>
          <div><h3>{{ item.title }}</h3><p>{{ item.description }}</p></div>
        </article>
      </div>
    </div>

    <div class="details-actions section-block">
      <div v-if="!hasSubmitted" class="closing-copy">
        <span class="eyebrow"><span>✦</span><span>LISTO PARA EMPEZAR</span></span>
        <h2>Prepárate para comenzar</h2>
        <p>Realiza la evaluación en un lugar tranquilo, lee cada pregunta con atención y responde sin apresurarte. La utilidad de los resultados depende de que tus respuestas representen lo que realmente te interesa.</p>
        <p> </p>
      </div>
      <NuxtLink
        :to="hasSubmitted ? '/espera' : '/datos-personales'"
        class="hero-start-btn"
      >
        <span>{{ hasSubmitted ? 'Consultar mi evaluación' : 'Comenzar evaluación' }}</span>
        <span aria-hidden="true">→</span>
      </NuxtLink>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { getEvaluationUuid } from '../../../utils/evaluationStorage'

const hasSubmitted = ref(false)
onMounted(() => {
  hasSubmitted.value = Boolean(getEvaluationUuid())
})

const considerations = [
  { title: 'Tus intereses son el punto de partida', description: 'Tus respuestas permiten reconocer afinidades con los objetivos y características de diferentes programas académicos.' },
  { title: 'Las opciones dependen del área seleccionada', description: 'La evaluación considera únicamente los programas académicos pertenecientes al área que elijas.' },
  { title: 'No hay respuestas correctas o incorrectas', description: 'Responde con libertad y evita elegir opciones únicamente porque parezcan más convenientes.' },
  { title: 'El resultado es una orientación', description: 'ATHENA presenta afinidades y recomendaciones para apoyar tu reflexión, no una decisión vocacional definitiva.' }
]
</script>

<style scoped>
@import '../styles/introduction.css';

.details-actions {
  display: flex;
  justify-content: center;
}

.details-actions .hero-start-btn {
  font-size: clamp(1.15rem, 1rem + 1vw, 1.5rem);
  padding: 1rem 3rem;
  cursor: pointer;
}
</style>
