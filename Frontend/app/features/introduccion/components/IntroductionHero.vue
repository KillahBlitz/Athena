<template>
  <section class="intro-hero" aria-labelledby="hero-main-title">
    <div class="hero-copy">
      <span class="eyebrow">
        <span>✦</span>
        <span>ATHENA</span>
      </span>
      <h1 id="hero-main-title" class="hero-title">Sistema Inteligente de Orientación Vocacional</h1>
      <h2 class="hero-subtitle">Instituto Politecnico Nacional</h2>
      <p class="hero-lead">
        Descubre dónde tu perfil se alinea mejor con los programas académicos del Instituto Politécnico Nacional.
      </p>

      <div class="hero-actions">
        <a href="#application-details" class="base-button btn-primary btn-lg hero-start-btn">
          <span>Empieza por aqui </span>
          <span aria-hidden="true">→</span>
        </a>
      </div>
    </div>

    <!-- Right Column: Visual card matching Image 1 -->
    <div class="hero-visual" aria-label="Constelación e ilustración interactiva de Athena">
      <img
        src="/illustrations/hero-nebula.svg"
        alt="Visualización fluida con constelación de estrellas de Athena"
        class="nebula-illustration"
      >

      <!-- Floating Top Pill -->
      <div class="floating-top-pill" aria-hidden="true">
        <span>✦</span>
        <span>Todo empieza con una pregunta</span>
      </div>

      <!-- Floating Bottom Card -->
      <div class="floating-bottom-card" role="note">
        <div class="floating-avatar-icon" aria-hidden="true">
          <svg viewBox="0 0 40 40" width="28" height="28" fill="none">
            <circle cx="20" cy="20" r="16" fill="#8E52FF" />
            <circle cx="15" cy="17" r="2.5" fill="#40FEFE" />
            <circle cx="25" cy="17" r="2.5" fill="#40FEFE" />
            <path d="M16 23 Q20 27 24 23" stroke="#40FEFE" stroke-width="2" stroke-linecap="round" />
            <path d="M20 7 L21 10 L24 10 L21.5 12 L22.5 15 L20 13 L17.5 15 L18.5 12 L16 10 L19 10 Z" fill="#FD3EFD" />
          </svg>
        </div>
        <div class="floating-card-text">
          <strong class="floating-card-title">Alinea tu perfil con los programas académicos del IPN</strong>
          <span class="floating-card-subtitle">Empieza dibujando tu camino.</span>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
// Visual Hero Component
</script>

<style scoped>
@import '../styles/introduction.css';
</style>
