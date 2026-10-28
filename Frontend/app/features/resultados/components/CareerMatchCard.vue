<template>
  <article class="career-card" :class="`is-${medal}`" :aria-label="`Opción ${career.rank}: ${career.name}, ${matchText}% de coincidencia`">
    <div class="career-medal" aria-hidden="true">
      <span class="career-medal-badge">{{ career.rank }}</span>
      <span class="career-medal-label">{{ MEDAL_LABEL[medal] }}</span>
    </div>

    <div class="career-info">
      <h3 class="career-name">{{ career.name }}</h3>
      <p v-if="career.schools.length" class="career-school">
        <svg viewBox="0 0 16 16" width="13" height="13" fill="none" stroke="currentColor" aria-hidden="true">
          <path d="M2 6 L8 2.5 L14 6 M3.5 6.5 V12 M6.5 6.5 V12 M9.5 6.5 V12 M12.5 6.5 V12 M2 13.5 H14" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
        <span>IPN · {{ career.schools.join(', ') }}</span>
      </p>
    </div>

    <div class="career-match">
      <span class="career-match-value">{{ matchText }} %</span>
      <span class="career-match-label">coincidencia</span>
    </div>
  </article>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { CareerMatch, Medal } from '../types'

const props = defineProps<{ career: CareerMatch }>()

const MEDAL_LABEL: Record<Medal, string> = { oro: 'Oro', plata: 'Plata', bronce: 'Bronce' }
const MEDALS: Record<CareerMatch['rank'], Medal> = { 1: 'oro', 2: 'plata', 3: 'bronce' }

const PERCENT = new Intl.NumberFormat('es-MX', { maximumFractionDigits: 1 })

const medal = computed(() => MEDALS[props.career.rank])
const matchText = computed(() => PERCENT.format(props.career.match))
</script>

<style scoped>
.career-card {
  --medal: #D4A017;
  --medal-soft: #FEF7E0;
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 1rem 1.25rem;
  padding: 1.15rem 1.35rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  break-inside: avoid;
  transition: border-color var(--motion-base) ease, box-shadow var(--motion-base) ease;
}

.career-card:hover {
  border-color: var(--color-primary-border);
  box-shadow: var(--shadow-card-hover);
}

.career-card.is-oro {
  border-color: var(--color-primary-border);
}

.career-card.is-plata {
  --medal: #64748B;
  --medal-soft: #F1F5F9;
}

.career-card.is-bronce {
  --medal: #C2410C;
  --medal-soft: #FFF1E6;
}

.career-medal {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.3rem;
  width: 3rem;
}

.career-medal-badge {
  display: grid;
  place-items: center;
  width: 2.2rem;
  height: 2.2rem;
  border-radius: 50%;
  border: 1.5px solid var(--medal);
  background: var(--medal-soft);
  color: var(--medal);
  font-weight: 700;
  font-size: 0.95rem;
}

.career-medal-label {
  font-size: 0.6rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--medal);
}

.career-info {
  min-width: 0;
}

.career-name {
  font-family: var(--font-display);
  font-size: clamp(1rem, 0.95rem + 0.3vw, 1.15rem);
  font-weight: 700;
  color: var(--color-text-main);
  line-height: 1.25;
  margin-bottom: 0.35rem;
  text-wrap: balance;
}

.career-school {
  display: flex;
  align-items: flex-start;
  gap: 0.4rem;
  font-size: 0.8rem;
  color: var(--color-text-muted);
}

.career-school svg {
  flex-shrink: 0;
  margin-top: 0.15rem;
}

.career-match {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  text-align: right;
}

.career-match-value {
  font-family: var(--font-display);
  font-size: clamp(1.4rem, 1.2rem + 0.8vw, 1.85rem);
  font-weight: 800;
  line-height: 1;
  color: var(--color-primary);
  white-space: nowrap;
}

.career-match-label {
  margin-top: 0.3rem;
  font-size: 0.7rem;
  color: var(--color-text-muted);
}

@media (max-width: 520px) {
  .career-card {
    grid-template-columns: auto 1fr;
  }

  .career-match {
    grid-column: 2;
    flex-direction: row;
    align-items: baseline;
    gap: 0.4rem;
  }
}
</style>
