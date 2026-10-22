import { describe, expect, it } from 'vitest'
import { reactionFor, storyFor, STORY_SCENE_COUNT } from '../../app/features/riasec/config/riasecStories'

describe('storyFor', () => {
  it.each([1, 2, 3, 4, 5, 6])('la dimensión %i tiene 3 escenas con el nombre del avatar', (riasecId) => {
    const scenes = storyFor(riasecId, 'Pixel')

    expect(scenes).toHaveLength(STORY_SCENE_COUNT)
    expect(scenes[0]!.line).toContain('Pixel')
    expect(scenes.every(s => s.title.length > 0 && s.line.length > 0)).toBe(true)
    expect(scenes.some(s => s.line.includes('{avatar}'))).toBe(false)
  })

  it('cada dimensión cuenta una historia distinta', () => {
    const openings = [1, 2, 3, 4, 5, 6].map(id => storyFor(id, 'Nova')[0]!.line)

    expect(new Set(openings).size).toBe(6)
  })

  it('usa la historia genérica para una dimensión desconocida', () => {
    const scenes = storyFor(99, 'Atlas')

    expect(scenes).toHaveLength(STORY_SCENE_COUNT)
    expect(scenes[0]!.line).toBe('Atlas empieza una nueva aventura.')
  })
})

describe('reactionFor', () => {
  it('rota las frases de forma determinista', () => {
    const first = [1, 2, 3, 4].map(reactionFor)

    expect(new Set(first).size).toBe(4)
    expect(reactionFor(5)).toBe(reactionFor(1))
    expect(reactionFor(1)).toBe('¡Buena elección!')
  })
})
