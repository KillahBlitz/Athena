import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { AnimatePresence, Motion } from 'motion-v'
import AvatarStoryCard from '../../app/features/riasec/components/AvatarStoryCard.vue'
import { AVATARS } from '../../app/config/avatars'

const pixel = AVATARS.find(a => a.id === 'pixel')!

function mountCard(selectedCount = 0) {
  return mount(AvatarStoryCard, {
    props: { avatar: pixel, riasecId: 1, selectedCount },
    global: { components: { Motion, AnimatePresence } }
  })
}

describe('AvatarStoryCard', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('cuenta la primera escena de la dimensión con el avatar elegido', () => {
    const wrapper = mountCard()

    expect(wrapper.find('.story-line').text()).toBe('Pixel encontró un taller lleno de piezas sueltas.')
    expect(wrapper.find('.story-avatar img').attributes('src')).toBe(pixel.image)
    expect(wrapper.find('.story-indicator').text()).toContain('Escena 1 de 3')
    expect(wrapper.find('.story-indicator').attributes('aria-live')).toBeUndefined()
  })

  it('el botón siguiente avanza y anuncia el cambio en la región oculta', async () => {
    const wrapper = mountCard()

    await wrapper.find('button[aria-label="Escena siguiente"]').trigger('click')

    expect(wrapper.find('.story-indicator').text()).toContain('Escena 2 de 3')
    const status = wrapper.find('[role="status"]')
    expect(status.text()).toContain('Escena 2 de 3')
    expect(status.text()).toContain('Con las manos y un plan')
  })

  it('el botón de pausa alterna aria-pressed', async () => {
    const wrapper = mountCard()
    const pause = wrapper.find('button[aria-label="Pausar historia"]')
    expect(pause.attributes('aria-pressed')).toBe('false')

    await pause.trigger('click')

    expect(pause.attributes('aria-pressed')).toBe('true')
  })

  it('reacciona cuando aumentan las selecciones y no cuando disminuyen', async () => {
    const wrapper = mountCard(2)
    expect(wrapper.find('.story-reaction').exists()).toBe(false)

    await wrapper.setProps({ selectedCount: 1 })
    expect(wrapper.find('.story-reaction').exists()).toBe(false)

    await wrapper.setProps({ selectedCount: 2 })
    expect(wrapper.find('.story-reaction').text()).toBe('¡Eso dice mucho de ti!')
    expect(wrapper.find('.story-indicator').text()).toContain('Escena 2 de 3')
  })

  it('el avatar y el icono de la dimensión vuelven a entrar en cada escena', async () => {
    const wrapper = mountCard()
    const avatarBefore = wrapper.find('.story-avatar-enter').element
    const propBefore = wrapper.find('.story-prop').element

    await wrapper.find('button[aria-label="Escena siguiente"]').trigger('click')

    expect(wrapper.find('.story-avatar-enter').element).not.toBe(avatarBefore)
    expect(wrapper.find('.story-prop').element).not.toBe(propBefore)
  })

  it('la reacción desaparece a los 1500 ms', async () => {
    const wrapper = mountCard(0)
    await wrapper.setProps({ selectedCount: 1 })
    expect(wrapper.find('.story-reaction').exists()).toBe(true)

    vi.advanceTimersByTime(1500)
    await wrapper.vm.$nextTick()

    expect(wrapper.find('.story-reaction').exists()).toBe(false)
  })

  it('una reacción con la historia en pausa no reanuda el avance automático', async () => {
    const wrapper = mountCard(0)
    await wrapper.find('button[aria-label="Pausar historia"]').trigger('click')

    await wrapper.setProps({ selectedCount: 1 })
    expect(wrapper.find('.story-indicator').text()).toContain('Escena 2 de 3')
    vi.advanceTimersByTime(12000)
    await wrapper.vm.$nextTick()

    expect(wrapper.find('.story-indicator').text()).toContain('Escena 2 de 3')
  })

  it('montar con selecciones ya guardadas no cuenta como reacción', () => {
    const wrapper = mountCard(3)

    expect(wrapper.find('.story-reaction').exists()).toBe(false)
    expect(wrapper.find('.story-indicator').text()).toContain('Escena 1 de 3')
  })

  it('tiene controles accesibles con anterior deshabilitado en la primera escena', () => {
    const wrapper = mountCard()

    expect(wrapper.find('button[aria-label="Escena anterior"]').attributes('disabled')).toBeDefined()
    expect(wrapper.findAll('.story-controls button')).toHaveLength(3)
  })
})
