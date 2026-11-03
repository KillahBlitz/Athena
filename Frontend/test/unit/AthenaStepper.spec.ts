import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mount, RouterLinkStub } from '@vue/test-utils'
import AthenaStepper from '../../app/components/layout/AthenaStepper.vue'

const route = { path: '/' }
vi.mock('vue-router', () => ({ useRoute: () => route }))

function mountAt(path: string) {
  route.path = path
  return mount(AthenaStepper, { global: { stubs: { NuxtLink: RouterLinkStub } } })
}

describe('AthenaStepper', () => {
  beforeEach(() => {
    route.path = '/'
  })

  it('marca como actual el paso de la ruta y enlaza solo los pasos anteriores', () => {
    const wrapper = mountAt('/objetivos')

    const current = wrapper.find('.stepper-list [aria-current="step"]')
    expect(current.text()).toContain('Objetivos')
    const links = wrapper.findAllComponents(RouterLinkStub).map(l => l.props('to'))
    expect(links).toEqual(['/', '/datos-personales'])
  })

  it('muestra el resumen compacto con el paso actual y su progreso', () => {
    const wrapper = mountAt('/datos-personales')

    const compact = wrapper.find('.stepper-compact')
    expect(compact.text()).toContain('Paso 2 de 5')
    expect(compact.text()).toContain('Datos personales')
    const bar = compact.find('[role="progressbar"]')
    expect(bar.attributes('aria-valuenow')).toBe('40')
  })

  it('en la introducción no hay pasos completados', () => {
    const wrapper = mountAt('/')

    expect(wrapper.findAll('.step-item.is-completed')).toHaveLength(0)
    expect(wrapper.find('.stepper-compact').text()).toContain('Paso 1 de 5')
  })
})
