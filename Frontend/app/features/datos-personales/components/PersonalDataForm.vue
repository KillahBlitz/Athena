<template>
  <div class="personal-data-layout">
    <aside class="companion-panel" aria-label="Acompañamiento vocacional">
      <div class="companion-badge-pill" role="status">
        <span class="companion-badge-avatar" aria-hidden="true">
          <TrackingAvatar v-if="hasChosenAvatar" class="badge-tracking" :avatar-id="selectedAvatar.id" :name="selectedAvatar.name" />
          <img v-else :src="selectedAvatar.image" alt="">
        </span>
        <span>Estoy aquí para acompañarte</span>
      </div>

      <AvatarSelector
        :avatars="avatarsList"
        :selected-id="form.selectedAvatarId"
        :selected-avatar="selectedAvatar"
        @select="chooseAvatar"
      />

      <AvatarCompanion :avatar="selectedAvatar" :name="form.name" stage="personal" :tracking-enabled="hasChosenAvatar" />
    </aside>

    <form class="personal-form-card" novalidate @submit.prevent="submit">
      <div class="form-card-header">
        <h2 class="form-card-title">Tus datos personales</h2>
        <span class="form-card-required-note">Todos los campos son obligatorios <span class="form-card-required-asterisk" aria-hidden="true">*</span></span>
      </div>

      <div class="personal-inputs-row">
        <BaseInput
          id="name"
          v-model="form.name"
          label="Nombre Completo"
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

      <AreaSelector
        :areas="areas"
        :selected-id="form.selectedAreaId"
        :loading="loadingAreas"
        :api-error="apiError"
        :error="touched.area ? errors.area : ''"
        @select="selectArea"
        @retry="loadAreas"
      />

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

      <div class="form-actions-row">
        <NuxtLink to="/" class="back-text-btn">
          <span aria-hidden="true">←</span>
          <span>Volver</span>
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
import { ref } from 'vue'
import TrackingAvatar from '../../../components/avatar/TrackingAvatar.vue'
import { AVATARS } from '../../../config/avatars'
import { usePersonalDataForm } from '../composables/usePersonalDataForm'
import AvatarSelector from './AvatarSelector.vue'
import AreaSelector from './AreaSelector.vue'
import BaseInput from '../../../components/ui/BaseInput.vue'
import BaseButton from '../../../components/ui/BaseButton.vue'
import AvatarCompanion from '../../../components/avatar/AvatarCompanion.vue'

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

const hasChosenAvatar = ref(false)
function chooseAvatar(id: string) {
  selectAvatar(id)
  hasChosenAvatar.value = true
}

const avatarsList = AVATARS
const openTermsModal = () => {
  alert('Términos y condiciones de ATHENA: La información recopilada se utiliza exclusivamente con fines de orientación vocacional académica y está protegida conforme a las leyes de privacidad aplicables.')
}
</script>

<style scoped>
@import '../styles/personal-data.css';
.badge-tracking { width: 16px; }
</style>
