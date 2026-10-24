import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAthenaSessionStore } from '../../../stores/athenaSession'
import { useAreasApi } from '../../../composables/useAreasApi'
import { validatePersonalData, type ValidationErrors } from '../validation/personalDataValidation'
import type { BackendAreaDTO, Area } from '../../../types/area'
import type { Avatar } from '../../../types/avatar'
import { AVATARS } from '../../../config/avatars'

export function usePersonalDataForm() {
  const router = useRouter()
  const session = useAthenaSessionStore()
  const { fetchAreas, fetchAreaData } = useAreasApi()

  const loadingAreas = ref(false)
  const loadingSubmit = ref(false)
  const apiError = ref<string | null>(null)
  const rawAreas = ref<BackendAreaDTO[]>([])
  const touched = reactive<Record<string, boolean>>({})

  const form = reactive({
    name: session.name,
    email: session.email,
    age: session.age,
    selectedAvatarId: session.selectedAvatarId || 'nova',
    selectedAreaId: session.selectedAreaId,
    termsAccepted: session.termsAccepted
  })

  const AREA_METADATA: Record<number, { tagline: string; icon: string }> = {
    1: {
      tagline: 'Ideas que explican el mundo',
      icon: '/icons/area-fisico-matematicas.svg'
    },
    2: {
      tagline: 'La vida en todas sus formas',
      icon: '/icons/area-medico-biologicas.svg'
    },
    3: {
      tagline: 'Personas, sociedad y decisiones',
      icon: '/icons/area-sociales-administrativas.svg'
    }
  }

  const areas = computed<Area[]>(() => {
    return rawAreas.value.map(a => {
      const meta = AREA_METADATA[a.area_id] || {
        tagline: 'Explora y conecta tu vocación',
        icon: '/icons/area-fisico-matematicas.svg'
      }
      return {
        id: a.area_id,
        name: a.nom_area,
        tagline: meta.tagline,
        icon: meta.icon
      }
    })
  })

  const selectedAvatar = computed<Avatar>(() => {
    return AVATARS.find(a => a.id === form.selectedAvatarId) ?? AVATARS[1] ?? session.selectedAvatar
  })

  const validation = computed(() => {
    return validatePersonalData(form)
  })

  const isFormValid = computed(() => validation.value.isValid)
  const errors = computed<ValidationErrors>(() => validation.value.errors)

  const loadAreas = async () => {
    loadingAreas.value = true
    apiError.value = null
    try {
      rawAreas.value = await fetchAreas()
      if (session.selectedAreaId && !form.selectedAreaId) {
        form.selectedAreaId = session.selectedAreaId
      }
    } catch (err: unknown) {
      apiError.value = err instanceof Error ? err.message : 'Error al cargar las áreas disponibles.'
    } finally {
      loadingAreas.value = false
    }
  }

  const selectAvatar = (avatarId: string) => {
    form.selectedAvatarId = avatarId
    session.selectAvatar(avatarId)
  }

  const selectArea = (areaId: number) => {
    form.selectedAreaId = areaId
    const found = rawAreas.value.find(a => a.area_id === areaId)
    session.selectArea(areaId, found?.nom_area || `Área ${areaId}`)
  }

  const touch = (field: string) => {
    touched[field] = true
  }

  const submit = async () => {
    ['name', 'email', 'age', 'avatar', 'area', 'terms'].forEach(f => {
      touched[f] = true
    })

    if (!isFormValid.value || form.selectedAreaId === null) {
      return
    }

    loadingSubmit.value = true
    apiError.value = null

    try {
      session.setPersonalData({
        name: form.name,
        email: form.email,
        age: form.age,
        termsAccepted: form.termsAccepted
      })
      session.selectAvatar(form.selectedAvatarId)

      const areaData = await fetchAreaData(form.selectedAreaId)

      if (!areaData || !Array.isArray(areaData.objetivos) || areaData.objetivos.length === 0) {
        throw new Error('La respuesta del servidor no contiene objetivos válidos para esta área.')
      }

      session.setAreaData(areaData)
      await router.push('/objetivos')
    } catch (err: unknown) {
      apiError.value = err instanceof Error ? err.message : 'No se pudo conectar con el servidor para obtener los objetivos del área.'
    } finally {
      loadingSubmit.value = false
    }
  }

  onMounted(async () => {
    session.restore()
    form.name = session.name
    form.email = session.email
    form.age = session.age
    if (session.selectedAvatarId) form.selectedAvatarId = session.selectedAvatarId
    if (session.selectedAreaId) form.selectedAreaId = session.selectedAreaId
    form.termsAccepted = session.termsAccepted

    await loadAreas()
  })

  return {
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
  }
}
