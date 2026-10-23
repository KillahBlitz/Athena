import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import type { RouteLocationNormalized } from 'vue-router'
import { useRiasecForm } from '../../app/features/riasec/composables/useRiasecForm'
import { useAthenaSessionStore } from '../../app/stores/athenaSession'
import { EVALUATION_UUID_KEY } from '../../app/utils/evaluationStorage'

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
    objetivos: { '101': 'Construir soluciones' },
    preguntas: [{ riasec_id: 1, texto_pregunta: '¿Qué disfrutas?', pregunta_abierta: 'Cuéntanos', opciones: { '11': 'Reparar' } }]
  })
  session.$patch({
    name: 'Prueba', email: 'test@example.com', age: 20, selectedAreaId: 1,
    answers: { 101: { valoracion: 4, justificacion: 'Me interesa' } },
    riasecAnswers: { 1: { opcionIds: [11], respuestaAbierta: 'Reparo aparatos' } }
  })
  let form!: ReturnType<typeof useRiasecForm>
  const wrapper = mount({
    setup() {
      form = useRiasecForm()
      return () => null
    }
  })
  return { form, wrapper }
}

describe('envío del cuestionario con UUID', () => {
  it('guarda el UUID devuelto antes de abrir la pantalla de espera', async () => {
    fetchMock.mockResolvedValueOnce(UUID)
    const { form, wrapper } = mountCompletedForm()
    router.push.mockImplementationOnce(() => {
      expect(localStorage.getItem(EVALUATION_UUID_KEY)).toBe(UUID)
    })

    await form.handleFinish()

    expect(fetchMock).toHaveBeenCalledWith('http://localhost:8000/save-user', expect.objectContaining({ method: 'POST' }))
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

  it.each(['/', '/datos-personales', '/objetivos', '/riasec'])('recupera el UUID persistido al entrar a %s', async (path) => {
    localStorage.setItem(EVALUATION_UUID_KEY, UUID)

    await visit(path)

    expect(navigate).toHaveBeenCalledWith('/espera', { replace: true })
    expect(localStorage.getItem(EVALUATION_UUID_KEY)).toBe(UUID)
  })

  it('permite permanecer en espera sin un ciclo de redirecciones', async () => {
    localStorage.setItem(EVALUATION_UUID_KEY, UUID)

    await visit('/espera')

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
