import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import AvatarCompanion from '../../app/components/avatar/AvatarCompanion.vue'
import { AVATARS, DEFAULT_AVATAR } from '../../app/config/avatars'

describe('acompañamiento interactivo', () => {
  it('saluda por nombre y responde al tocar el avatar', async () => {
    const wrapper = mount(AvatarCompanion, { props: { avatar: DEFAULT_AVATAR, stage: 'personal', name: 'Ana López' } })
    expect(wrapper.get('[role="status"]').text()).toContain('Ana')
    await wrapper.get('button').trigger('click')
    expect(wrapper.get('[role="status"]').text()).toContain('¡Aquí estoy!')
    wrapper.unmount()
  })

  it('cambia los consejos y los reinicia al cambiar de etapa', async () => {
    const wrapper = mount(AvatarCompanion, { props: { avatar: DEFAULT_AVATAR, stage: 'riasec' } })
    const tip = wrapper.findAll('button')[1]!
    await tip.trigger('click')
    expect(wrapper.get('[role="status"]').text()).toContain('pregunta abierta')
    await tip.trigger('click')
    expect(wrapper.get('[role="status"]').text()).toContain('situación concreta')
    await wrapper.setProps({ stage: 'waiting' })
    await tip.trigger('click')
    expect(wrapper.get('[role="status"]').text()).toContain('ya fueron enviadas')
    wrapper.unmount()
  })

  it('celebra al completar una dimensión y cambia de personalidad al elegir otro avatar', async () => {
    const wrapper = mount(AvatarCompanion, { props: { avatar: DEFAULT_AVATAR, stage: 'riasec', complete: false } })
    await wrapper.setProps({ complete: true })
    expect(wrapper.get('[role="status"]').text()).toContain('completado esta dimensión')
    await wrapper.setProps({ avatar: AVATARS[0]! })
    expect(wrapper.get('[role="status"]').text()).toContain('Atlas')
    await wrapper.findAll('button')[2]!.trigger('click')
    expect(wrapper.get('[role="status"]').text()).toContain('Paso a paso')
    wrapper.unmount()
  })
})
