import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import { Motion } from 'motion-v'
import BaseButton from '../../app/components/ui/BaseButton.vue'

function mountButton(props: Record<string, unknown> = {}) {
  return mount(BaseButton, {
    props,
    slots: { default: 'Continuar' },
    global: { components: { Motion } }
  })
}

describe('BaseButton', () => {
  it('renderiza un button nativo con el type indicado', () => {
    const wrapper = mountButton({ type: 'submit' })

    const button = wrapper.find('button')
    expect(button.exists()).toBe(true)
    expect(button.attributes('type')).toBe('submit')
    expect(button.text()).toContain('Continuar')
  })

  it('emite click cuando está habilitado', async () => {
    const wrapper = mountButton()

    await wrapper.find('button').trigger('click')

    expect(wrapper.emitted('click')).toHaveLength(1)
  })

  it('queda deshabilitado mientras carga', () => {
    const wrapper = mountButton({ loading: true })

    expect(wrapper.find('button').attributes('disabled')).toBeDefined()
    expect(wrapper.find('.spinner').exists()).toBe(true)
  })
})
