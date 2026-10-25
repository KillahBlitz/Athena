import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import type { RouteLocationNormalized } from 'vue-router'
import { useRiasecForm } from '../../app/features/riasec/composables/useRiasecForm'
import { useAthenaSessionStore } from '../../app/stores/athenaSession'
import { EVALUATION_UUID_KEY } from '../../app/utils/evaluationStorage'
import ObjectivesPage from '../../app/pages/objetivos.vue'
import AvatarCompanion from '../../app/components/avatar/AvatarCompanion.vue'

const { router } = vi.hoisted(() => ({ router: { push: vi.fn(), replace: vi.fn() } }))
vi.mock('vue-router', () => ({ useRouter: () => router }))

const UUID = 'USER-1021d1ae-4183-43e9-9172-1a05504526b8'
const fetchMock = vi.fn()
const navigate = vi.fn()

beforeEach(() => {
  setActivePinia(createPinia())
  localStorage.clear()
  vi.clearAllMocks()
  vi.stubGlobal('$fetch', fetchMock)
  vi.stubGlobal('useRuntimeConfig', () => ({ public: { apiBase: 'http://localhost:8000' } }))
  vi.stubGlobal('defineNuxtRouteMiddleware', (handler: unknown) => handler)
  vi.stubGlobal('navigateTo', navigate)
})

afterEach(() => {
  localStorage.clear()
  vi.unstubAllGlobals()
})

function mountCompletedForm() {
  const session = useAthenaSessionStore()
  session.setAreaData({
    area_id: 1,
    nom_area: 'Área de prueba',
    objetivos: [{ id_objetivo: 101, id_carrera: 101, pregunta: 'Construir soluciones' }],
    preguntas: [{ riasec_id: 1, texto_pregunta: '¿Qué disfrutas?', pregunta_abierta: 'Cuéntanos', opciones: { '11': 'Reparar' } }]
  })
  session.$patch({
    name: 'Prueba', email: 'test@example.com', age: 20, selectedAreaId: 1,
    answers: { 101: { valoracion: 4, justificacion: 'Me interesa' } },
    riasecAnswers: { 1: { opcionIds: [11], respuestaAbierta: 'Reparo aparatos' } }
  })
  session.persist()
  let form!: ReturnType<typeof useRiasecForm>
  const wrapper = mount({
    setup() {
      form = useRiasecForm()
      return () => null
    }
  })
  return { form, wrapper }
}

describe('respuestas abiertas RISEC obligatorias', () => {
  it('bloquea el envío cuando una dimensión del diccionario no tiene criterios seleccionados', async () => {
    const { form, wrapper } = mountCompletedForm()
    form.toggleOption(11)

    await form.handleFinish()

    expect(fetchMock).not.toHaveBeenCalled()
    expect(form.submitError.value).toContain('habilidad seleccionada')
    wrapper.unmount()
  })

  it.each(['', '   ', '\n\t'])('bloquea avance y envío con una respuesta vacía: %j', async (answer) => {
    const { form, wrapper } = mountCompletedForm()
    const session = useAthenaSessionStore()
    form.setOpenAnswer(answer)

    expect(form.isCurrentComplete.value).toBe(false)
    expect(form.tabs.value[0]?.isAnswered).toBe(false)
    expect(form.progress.value.answeredCount).toBe(0)
    form.handleNext()
    expect(session.status).not.toBe('riasec-completed')

    await form.handleFinish()
    expect(fetchMock).not.toHaveBeenCalled()
    expect(form.submitError.value).toContain('pregunta abierta')

    form.setOpenAnswer(' Reparo aparatos ')
    expect(form.isCurrentComplete.value).toBe(true)
    expect(form.tabs.value[0]?.isAnswered).toBe(true)
    expect(form.progress.value.answeredCount).toBe(1)
    wrapper.unmount()
  })
})

describe('envío del cuestionario con UUID', () => {
  it('envía cada justificación escrita en objetivos como description después de restaurar la sesión', async () => {
    vi.stubGlobal('useHead', vi.fn())
    fetchMock.mockResolvedValueOnce(UUID)
    const session = useAthenaSessionStore()
    session.setAreaData({
      area_id: 1,
      nom_area: 'Área de prueba',
      objetivos: [
        { id_objetivo: 7, id_carrera: 42, pregunta: 'Construir soluciones' },
        { id_objetivo: 8, id_carrera: 43, pregunta: 'Ayudar a las personas' }
      ],
      preguntas: [{ riasec_id: 1, texto_pregunta: '¿Qué disfrutas?', pregunta_abierta: 'Cuéntanos', opciones: { '11': 'Reparar' } }]
    })
    session.$patch({ name: 'Prueba', email: 'test@example.com', age: 20, selectedAreaId: 1 })
    session.persist()
    const page = mount(ObjectivesPage, {
      global: {
        stubs: {
          Motion: { props: ['as'], template: '<component :is="as || \'div\'"><slot /></component>' },
          AnimatePresence: { template: '<div><slot /></div>' },
          AvatarCompanion: true,
          StageCelebration: true,
          ObjectiveProgress: true
        }
      }
    })
    const cards = page.findAll('article')
    const justifications = ['Me interesa construir robots', 'Quiero ayudar a mi comunidad']
    for (const [index, card] of cards.entries()) {
      await card.get('[aria-label="Valoración 4 de 5"]').trigger('click')
      await card.get('textarea').setValue(justifications[index])
    }
    expect(cards).toHaveLength(2)
    // Block navigation now lives inside the (stubbed) AvatarCompanion box.
    await page.findComponent(AvatarCompanion).vm.$emit('go-next')
    expect(router.push).toHaveBeenCalledWith('/riasec')
    page.unmount()

    // Recreate the store to exercise localStorage restoration between stages.
    setActivePinia(createPinia())
    let form!: ReturnType<typeof useRiasecForm>
    const wrapper = mount({ setup() { form = useRiasecForm(); return () => null } })
    form.toggleOption(11)
    form.setOpenAnswer('Reparo aparatos')
    await form.handleFinish()

    expect(fetchMock).toHaveBeenCalledWith('http://localhost:8000/save-user', expect.objectContaining({
      body: expect.objectContaining({
        objetives: [
          { id_objetive: 7, id_carrera: 42, puntuation: 4, description: justifications[0] },
          { id_objetive: 8, id_carrera: 43, puntuation: 4, description: justifications[1] }
        ]
      })
    }))
    wrapper.unmount()
  })

  it('conserva la evaluación enviada al intentar reiniciar desde el logo', () => {
    const { wrapper } = mountCompletedForm()
    const session = useAthenaSessionStore()
    localStorage.setItem(EVALUATION_UUID_KEY, UUID)
    const snapshot = JSON.stringify(session.$state)
    localStorage.setItem('athena_session_v2', snapshot)

    session.reset()

    expect(localStorage.getItem(EVALUATION_UUID_KEY)).toBe(UUID)
    expect(localStorage.getItem('athena_session_v2')).toBe(snapshot)
    expect(JSON.stringify(session.$state)).toBe(snapshot)
    wrapper.unmount()
  })

  it('evita un segundo envío si el navegador ya tiene un UUID', async () => {
    const { form, wrapper } = mountCompletedForm()
    localStorage.setItem(EVALUATION_UUID_KEY, UUID)

    await form.handleFinish()

    expect(fetchMock).not.toHaveBeenCalled()
    expect(router.replace).toHaveBeenCalledWith('/espera')
    expect(localStorage.getItem(EVALUATION_UUID_KEY)).toBe(UUID)
    wrapper.unmount()
  })

  it('guarda el UUID devuelto antes de abrir la pantalla de espera', async () => {
    fetchMock.mockResolvedValueOnce(UUID)
    const { form, wrapper } = mountCompletedForm()
    router.push.mockImplementationOnce(() => {
      expect(localStorage.getItem(EVALUATION_UUID_KEY)).toBe(UUID)
    })

    await form.handleFinish()

    expect(fetchMock).toHaveBeenCalledWith('http://localhost:8000/save-user', expect.objectContaining({
      method: 'POST',
      body: expect.objectContaining({
        objetives: [{ id_objetive: 101, id_carrera: 101, puntuation: 4, description: 'Me interesa' }],
        risec_questions: { 1: { risec_id: 1, criteria_list: [{ 11: 'Reparar' }], open_question: 'Reparo aparatos' } }
      })
    }))
    expect(router.push).toHaveBeenCalledWith('/espera')
    expect(form.submitError.value).toBeNull()
    expect(form.isSubmitting.value).toBe(false)
    wrapper.unmount()
  })

  it.each([true, false, '', '   ', null])('no guarda ni navega con una respuesta inválida: %s', async (response) => {
    fetchMock.mockResolvedValueOnce(response)
    const { form, wrapper } = mountCompletedForm()

    await form.handleFinish()

    expect(localStorage.getItem(EVALUATION_UUID_KEY)).toBeNull()
    expect(router.push).not.toHaveBeenCalled()
    expect(form.submitError.value).toContain('identificador')
    expect(form.isSubmitting.value).toBe(false)
    wrapper.unmount()
  })
})

describe('navegación con evaluación pendiente', () => {
  async function visit(path: string) {
    const { default: middleware } = await import('../../app/middleware/pending-evaluation.global')
    return middleware({ path } as RouteLocationNormalized, {} as RouteLocationNormalized)
  }

  it.each(['/datos-personales', '/objetivos', '/riasec', '/resultados', '/otra-ruta'])('bloquea el acceso a %s después del envío', async (path) => {
    localStorage.setItem(EVALUATION_UUID_KEY, UUID)

    await visit(path)

    expect(navigate).toHaveBeenCalledWith('/espera', { replace: true })
    expect(localStorage.getItem(EVALUATION_UUID_KEY)).toBe(UUID)
  })

  it.each(['/', '/espera'])('permite acceder a %s después del envío', async (path) => {
    localStorage.setItem(EVALUATION_UUID_KEY, UUID)

    await visit(path)

    expect(navigate).not.toHaveBeenCalled()
  })

  it('deja de forzar la espera cuando se elimina el UUID', async () => {
    localStorage.setItem(EVALUATION_UUID_KEY, UUID)
    localStorage.removeItem(EVALUATION_UUID_KEY)

    await visit('/')
    expect(navigate).not.toHaveBeenCalled()

    await visit('/espera')
    expect(navigate).toHaveBeenCalledWith('/riasec', { replace: true })
  })

  it('no confunde la antigua bandera true con un UUID', async () => {
    localStorage.setItem('athena_test_submitted', 'true')

    await visit('/')

    expect(navigate).not.toHaveBeenCalled()
  })
})
