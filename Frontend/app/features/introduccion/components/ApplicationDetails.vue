<template>
  <section id="application-details" class="intro-details-section" aria-labelledby="details-heading">
    <div class="details-header">
      <span class="eyebrow">
        <span>✦</span>
        <span>APOYO VOCACIONAL</span>
      </span>
      <h2 id="details-heading">¿Cómo funciona ATHENA?</h2>
      <p>
        Un modelo integral diseñado para acompañar tu vocación, uniendo rigor metodológico y comprensión de tus motivaciones individuales.
      </p>
    </div>

    <!-- 3 Pillars Grid -->
    <div class="details-grid">
      <article class="detail-card">
        <div class="detail-icon-wrap" aria-hidden="true">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="9" stroke-width="2" />
            <path d="M12 7 L12 12 L15 15" stroke-width="2" stroke-linecap="round" />
          </svg>
        </div>
        <h3>Tus intereses son el punto de partida</h3>
        <p>
          No buscamos encasillarte. Tus respuestas y valoraciones revelan afinidades profundas con problemáticas reales del entorno laboral y académico.
        </p>
      </article>

      <article class="detail-card">
        <div class="detail-icon-wrap" aria-hidden="true">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor">
            <path d="M4 19.5 A2.5 2.5 0 0 1 6.5 17 H20" stroke-width="2" />
            <path d="M6.5 2 H20 V22 H6.5 A2.5 2.5 0 0 1 4 19.5 V4.5 A2.5 2.5 0 0 1 6.5 2 z" stroke-width="2" />
          </svg>
        </div>
        <h3>Alineado con carreras reales</h3>
        <p>
          Cada pregunta está vinculada directamente a los objetivos de formación de planes de estudio universitarios e instituciones oficiales como el IPN.
        </p>
      </article>

      <article class="detail-card">
        <div class="detail-icon-wrap" aria-hidden="true">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor">
            <path d="M12 2 L15 8 L22 9 L17 14 L18 21 L12 18 L6 21 L7 14 L2 9 L9 8 Z" stroke-width="2" stroke-linejoin="round" />
          </svg>
        </div>
        <h3>Sin respuestas correctas o incorrectas</h3>
        <p>
          Responde con total libertad. Cada reflexión sincera permite que tu constelación vocacional represente fielmente lo que te mueve y apasiona.
        </p>
      </article>
    </div>

    <!-- 5 Steps Roadmap -->
    <div class="roadmap-container">
      <h3 class="roadmap-title">Las 5 etapas de tu expedición</h3>
      <div class="roadmap-steps">
        <div class="roadmap-step-card">
          <div class="step-badge-number">1</div>
          <h4>Introducción</h4>
          <p>Comprende el propósito del sistema y prepárate para la experiencia.</p>
        </div>

        <div class="roadmap-step-card">
          <div class="step-badge-number">2</div>
          <h4>Datos personales</h4>
          <p>Indica tu área de interés general y elige a tu avatar acompañante.</p>
        </div>

        <div class="roadmap-step-card">
          <div class="step-badge-number">3</div>
          <h4>Objetivos</h4>
          <p>Valora los objetivos formativos de cada carrera y comparte tu punto de vista.</p>
        </div>

        <div class="roadmap-step-card">
          <div class="step-badge-number">4</div>
          <h4>RIASEC</h4>
          <p>Mapeo de tus rasgos de personalidad e intereses ocupacionales.</p>
        </div>

        <div class="roadmap-step-card">
          <div class="step-badge-number">5</div>
          <h4>Resultados</h4>
          <p>Recomendaciones fundamentadas de carreras y programas académicos.</p>
        </div>
      </div>
    </div>
    <div class="details-actions">
      <NuxtLink to="/datos-personales" class="base-button btn-primary btn-lg hero-start-btn">
        <span>Comenzar</span>
      </NuxtLink>
    </div>
  </section>
</template>

<script setup lang="ts">
// Informational Details Component
</script>

<style scoped>
@import '../styles/introduction.css';

.details-actions {
  display: flex;
  justify-content: center;
}

.details-actions .hero-start-btn {
  font-size: 1.5rem;
  padding: 1.15rem 3rem;
  cursor: pointer;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.details-actions .hero-start-btn:hover {
  transform: translateY(-4px) scale(1.04);
  box-shadow: 0 12px 28px rgba(var(--intro-primary-rgb), 0.35);
}

.details-actions .hero-start-btn:active {
  transform: translateY(0) scale(0.98);
}

@media (prefers-reduced-motion: reduce) {
  .details-actions .hero-start-btn {
    transition: none;
    transform: none;
  }
}
</style>
