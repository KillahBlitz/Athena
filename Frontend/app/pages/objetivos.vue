<template>
  <div class="objectives-page">
    <div class="objectives-header-row">
      <div class="objectives-title-group">
        <span class="eyebrow">
          <span>✦</span>
          <span>CADA RESPUESTA CONECTA UNA ESTRELLA</span>
        </span>
        <h1 class="page-title">¿Qué quieres para tu futuro?</h1>
        <p class="page-description">
          Valora cada objetivo y cuéntanos qué hay detrás de tu respuesta.
        </p>
      </div>

      <ObjectiveProgress :progress="progress" />
    </div>

    <StageCelebration
      :show="isLastBlock && isCurrentBlockComplete"
      title="¡Has valorado todos los objetivos de esta área!"
      message="Tus respuestas han sido registradas. Puedes revisarlas o modificar cualquier valoración antes de la siguiente fase (RISEC)."
    >
      <BaseButton variant="outline" size="sm" @click="handleBack">
        Revisar bloques anteriores
      </BaseButton>
    </StageCelebration>

    <Transition name="onboarding-backdrop-fade">
      <div v-if="showOnboarding" class="onboarding-backdrop" @click="dismissOnboarding" />
    </Transition>

    <div class="objectives-main-row">
      <ObjectiveGrid
        v-if="currentBlockData"
        :block="currentBlockData"
        :get-answer="getAnswer"
        @rating="setRating"
        @justification="setJustification"
      />

      <AvatarCompanion
        class="objectives-companion"
        :avatar="selectedAvatar"
        stage="objectives"
        :complete="isCurrentBlockComplete"
        :onboarding="showOnboarding"
        :next-label="isLastBlock ? 'Finalizar etapa' : 'Adelante'"
        :is-last-block="isLastBlock"
        :next-disabled="!isCurrentBlockComplete"
        @dismiss-onboarding="dismissOnboarding"
        @go-back="handleBack"
        @go-next="handleNext"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import AvatarCompanion from '../components/avatar/AvatarCompanion.vue'
import { useObjectivesForm } from '../features/objetivos/composables/useObjectivesForm'
import ObjectiveProgress from '../features/objetivos/components/ObjectiveProgress.vue'
import ObjectiveGrid from '../features/objetivos/components/ObjectiveGrid.vue'
import BaseButton from '../components/ui/BaseButton.vue'
import StageCelebration from '../components/ui/StageCelebration.vue'
import { hasSeenObjectivesOnboarding, markObjectivesOnboardingSeen } from '../utils/objectivesOnboardingStorage'

useHead({
  title: 'ATHENA | Valoración de objetivos vocacionales'
})

const {
  currentBlockData,
  selectedAvatar,
  progress,
  isCurrentBlockComplete,
  isLastBlock,
  getAnswer,
  setRating,
  setJustification,
  handleNext,
  handleBack
} = useObjectivesForm()

// First time ever on /objetivos: show the avatar's "how to answer" card as
// an overlay above the questions. The user swipes it (or taps "Comenzar")
// to dock it into place; from then on it's remembered for this browser.
const showOnboarding = ref(false)

onMounted(() => {
  showOnboarding.value = !hasSeenObjectivesOnboarding()
})

function dismissOnboarding() {
  showOnboarding.value = false
  markObjectivesOnboardingSeen()
}
</script>

<style scoped>
@import '../features/objetivos/styles/objectives.css';

.onboarding-backdrop {
  position: fixed;
  inset: 0;
  z-index: 55;
  background: rgba(15, 15, 25, 0.45);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
}

.onboarding-backdrop-fade-enter-active,
.onboarding-backdrop-fade-leave-active {
  transition: opacity 220ms ease;
}
.onboarding-backdrop-fade-enter-from,
.onboarding-backdrop-fade-leave-to {
  opacity: 0;
}
</style>
