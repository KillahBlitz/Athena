<template>
  <div class="personal-data-layout">
    <!-- Left Column: Companion Panel -->
    <aside class="companion-panel" aria-label="Acompañamiento vocacional">
      <div class="companion-badge-pill" role="status">
        <span class="companion-badge-avatar" aria-hidden="true">
          <img :src="selectedAvatar?.image || '/avatars/nova.svg'" alt="">
        </span>
        <span>Estoy aquí para acompañarte</span>
      </div>

      <div class="companion-panel-text">
        <h2 class="companion-panel-heading">Siéntete acompañado en tu aventura</h2>
      </div>

      <AvatarSelector
        :avatars="avatarsList"
        :selected-id="form.selectedAvatarId"
        :selected-avatar="selectedAvatar"
        @select="selectAvatar"
      />

      <div class="companion-speech-card" role="note">
        <Motion
          :key="form.selectedAvatarId"
          class="companion-speech-avatar"
          aria-hidden="true"
          :animate="presets.select.animate"
          :transition="presets.select.transition"
        >
          <img :src="selectedAvatar?.image || '/avatars/nova.svg'" alt="">
        </Motion>
        <div class="companion-speech-content">
          <strong class="companion-speech-title">
            {{ greetingText }}
          </strong>
        </div>
      </div>
    </aside>

    <!-- Right Column: Personal Data & Area Form -->
    <form class="personal-form-card" novalidate @submit.prevent="submit">
      <div class="form-card-header">
        <h2 class="form-card-title">Tus datos personales</h2>
        <span class="form-card-required-note">Todos los campos son obligatorios</span>
      </div>

      <!-- 3 Inputs in a Row -->
      <div class="personal-inputs-row">
        <BaseInput
          id="name"
          v-model="form.name"
          label="Nombre"
          placeholder="Valeria Hernández"
          autocomplete="name"
          :required="true"
          :error="touched.name ? errors.name : ''"
          @blur="touch('name')"
        />

        <BaseInput
          id="email"
          v-model="form.email"
          type="email"
          label="Correo electrónico"
          placeholder="valeria.h@email.com"
          autocomplete="email"
          :required="true"
          :error="touched.email ? errors.email : ''"
          @blur="touch('email')"
        />

        <BaseInput
          id="age"
          v-model="form.age"
          type="number"
          label="Edad"
          placeholder="18"
          :min="12"
          :max="100"
          :required="true"
          :error="touched.age ? errors.age : ''"
          @blur="touch('age')"
        />
      </div>

      <!-- Academic Area Selector -->
      <AreaSelector
        :areas="areas"
        :selected-id="form.selectedAreaId"
        :loading="loadingAreas"
        :api-error="apiError"
        :error="touched.area ? errors.area : ''"
        @select="selectArea"
        @retry="loadAreas"
      />

      <!-- Terms and Conditions Checkbox -->
      <div class="terms-container">
        <label class="terms-row">
          <input
            v-model="form.termsAccepted"
            type="checkbox"
            class="terms-checkbox"
            @change="touch('terms')"
          >
          <span>
            Acepto los
            <a href="#terminos" class="terms-link" @click.prevent="openTermsModal">términos y condiciones.</a>
          </span>
        </label>
        <span v-if="touched.terms && errors.terms" class="input-error" role="alert">
          {{ errors.terms }}
        </span>
      </div>

      <!-- Navigation buttons row -->
      <div class="form-actions-row">
        <NuxtLink to="/" class="back-text-btn">
          <span aria-hidden="true">←</span>
          <span>Atrás</span>
        </NuxtLink>

        <BaseButton
          type="submit"
          variant="primary"
          size="md"
          :disabled="!isFormValid || loadingSubmit"
          :loading="loadingSubmit"
        >
          <span>Continuar</span>
          <template #suffix>
            <span aria-hidden="true">→</span>
          </template>
        </BaseButton>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { AVATARS } from '../../../config/avatars'
import { usePersonalDataForm } from '../composables/usePersonalDataForm'
import AvatarSelector from './AvatarSelector.vue'
import AreaSelector from './AreaSelector.vue'
import BaseInput from '../../../components/ui/BaseInput.vue'
import BaseButton from '../../../components/ui/BaseButton.vue'
import { useMotionPresets } from '../../../composables/useMotionPresets'

const {
  form,
  areas,
  selectedAvatar,
  loadingAreas,
  loadingSubmit,
  apiError,
  errors,
  touched,
  isFormValid,
  selectAvatar,
  selectArea,
  touch,
  submit,
  loadAreas
} = usePersonalDataForm()

const avatarsList = AVATARS
const presets = useMotionPresets()

const greetingText = computed(() => {
  const firstName = form.name.trim().split(' ')[0]
  const greeting = selectedAvatar.value?.greeting || '¡Qué gusto conocerte'
  if (firstName) {
    return `${greeting}, ${firstName}!`
  }
  return `${greeting}!`
})

const openTermsModal = () => {
  alert('Términos y condiciones de ATHENA: La información recopilada se utiliza exclusivamente con fines de orientación vocacional académica y está protegida conforme a las leyes de privacidad aplicables.')
}
</script>

<style scoped>
@import '../styles/personal-data.css';
</style>
