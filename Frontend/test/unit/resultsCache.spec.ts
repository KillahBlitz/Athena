import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount, type VueWrapper } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ResultsPage from '../../app/pages/resultados.vue'
import { EVALUATION_UUID_KEY } from '../../app/utils/evaluationStorage'
import { RESULTS_READY_KEY } from '../../app/utils/resultsStorage'

const { router } = vi.hoisted(() => ({ router: { replace: vi.fn() } }))
vi.mock('vue-router', () => ({ useRouter: () => router }))

const UUID = 'USER-results-cache-test'
const READY_RESULTS = [
  { top: 1, carrera_id: 10, carrera: 'Ingeniería en Sistemas', puntaje: 85, escuelas: ['ESCOM'] },
  { top: 2, carrera_id: 11, carrera: 'Ingeniería en IA', puntaje: 78, escuelas: ['UPIITA'] }
]
const fetchMock = vi.fn()
let wrapper: VueWrapper | undefined

function mountPage() {
  wrapper = mount(ResultsPage, {
    global: {
      stubs: {
        BaseButton: { template: '<button><slot /></button>' },
        CareerMatchCard: { props: ['career'], template: '<div class="career-stub">{{ career.name }}</div>' }
      }
    }
  })
  return wrapper
}

beforeEach(() => {
  setActivePinia(createPinia())
  localStorage.clear()
  localStorage.setItem(EVALUATION_UUID_KEY, UUID)
  fetchMock.mockReset()
  router.replace.mockReset()
  vi.stubGlobal('$fetch', fetchMock)
  vi.stubGlobal('useRuntimeConfig', () => ({ public: { apiBase: 'http://localhost:8000' } }))
  vi.stubGlobal('useHead', vi.fn())
})

afterEach(() => {
  wrapper?.unmount()
  wrapper = undefined
  localStorage.clear()
  vi.unstubAllGlobals()
})

describe('persistencia de resultados en /resultados', () => {
  it('guarda los resultados en caché tras obtenerlos de la API', async () => {
    fetchMock.mockResolvedValue({ user_uuid: UUID, status_id: 4, results: READY_RESULTS })
    const page = mountPage()
    await flushPromises()

    expect(fetchMock).toHaveBeenCalledTimes(1)
    expect(JSON.parse(localStorage.getItem(RESULTS_READY_KEY)!)).toEqual({ user_uuid: UUID, results: READY_RESULTS })
    expect(page.findAll('.career-stub')).toHaveLength(2)
  })

  it('muestra los resultados cacheados sin volver a llamar a la API', async () => {
    localStorage.setItem(RESULTS_READY_KEY, JSON.stringify({ user_uuid: UUID, results: READY_RESULTS }))
    const page = mountPage()
    await flushPromises()

    expect(fetchMock).not.toHaveBeenCalled()
    expect(router.replace).not.toHaveBeenCalled()
    expect(page.findAll('.career-stub')).toHaveLength(2)
    expect(page.get('.career-stub').text()).toBe('Ingeniería en Sistemas')
  })

  it('ignora una caché de otro uuid y consulta la API', async () => {
    localStorage.setItem(RESULTS_READY_KEY, JSON.stringify({ user_uuid: 'OTRO-UUID', results: READY_RESULTS }))
    fetchMock.mockResolvedValue({ user_uuid: UUID, status_id: 4, results: READY_RESULTS })
    mountPage()
    await flushPromises()

    expect(fetchMock).toHaveBeenCalledTimes(1)
  })
})
