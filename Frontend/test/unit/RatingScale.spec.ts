import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import RatingScale from '../../app/features/objetivos/components/RatingScale.vue'

const MotionStub = {
  props: ['as'],
  template: '<component :is="as || \'div\'"><slot /></component>'
}

function mountScale(modelValue: number | null) {
  return mount(RatingScale, {
    props: { carreraId: 101, modelValue },
    global: { stubs: { Motion: MotionStub } }
  })
}

describe('RatingScale', () => {
  it('expone cinco opciones como radiogroup accesible', () => {
    const wrapper = mountScale(null)

    expect(wrapper.find('[role="radiogroup"]').exists()).toBe(true)
    const radios = wrapper.findAll('[role="radio"]')
    expect(radios).toHaveLength(5)
    expect(radios.every(r => r.attributes('aria-checked') === 'false')).toBe(true)
  })

  it('marca solo la valoración seleccionada', () => {
    const wrapper = mountScale(4)

    const checked = wrapper.findAll('[role="radio"]').map(r => r.attributes('aria-checked'))
    expect(checked).toEqual(['false', 'false', 'false', 'true', 'false'])
    expect(wrapper.find('.rating-btn.is-selected').text()).toContain('4')
  })

  it('emite el valor elegido al pulsar una opción', async () => {
    const wrapper = mountScale(null)

    await wrapper.findAll('[role="radio"]')[2]!.trigger('click')

    expect(wrapper.emitted('update:modelValue')).toEqual([[3]])
  })
})
