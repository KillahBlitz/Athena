import { beforeEach, describe, expect, it } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useAthenaSessionStore } from '../../app/stores/athenaSession'
import type { BackendQuestionaryResponseDTO } from '../../app/types/area'

function areaWithObjectives(count: number): BackendQuestionaryResponseDTO {
  const objetivos: Record<string, string> = {}
  for (let i = 1; i <= count; i++) objetivos[String(100 + i)] = `Objetivo ${i}`
  return { area_id: 1, nom_area: 'Área de prueba', objetivos, preguntas: [] }
}

function storeWith(count: number) {
  const store = useAthenaSessionStore()
  store.setAreaData(areaWithObjectives(count))
  return store
}

function answerCurrentBlock(store: ReturnType<typeof useAthenaSessionStore>, rating: 1 | 2 | 3 | 4 | 5 = 3) {
  for (const objective of store.currentBlockData!.objectives) store.setAnswer(objective.carreraId, rating, '')
}

describe('athenaSession · bloques de objetivos', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it.each([
    [43, 8, 1],
    [12, 2, 6],
    [11, 2, 5]
  ])('con %i objetivos forma %i bloques de 6 y el último tiene %i', (count, totalBlocks, lastSize) => {
    const store = storeWith(count)

    expect(store.totalBlocks).toBe(totalBlocks)
    expect(store.blocks).toHaveLength(totalBlocks)
    expect(store.blocks.slice(0, -1).every(b => b.objectives.length === 6)).toBe(true)
    expect(store.blocks.at(-1)!.objectives).toHaveLength(lastSize)
    expect(store.progress.totalBlocks).toBe(totalBlocks)
    expect(store.currentBlockData!.objectives).toHaveLength(Math.min(6, count))
  })

  it('ignora goToBlock fuera de rango', () => {
    const store = storeWith(43)

    store.goToBlock(11)

    expect(store.currentBlock).toBe(1)
    store.goToBlock(8)
    expect(store.progress.currentBlock).toBe(8)
  })

  it('nextBlock en el último bloque marca la etapa como completada', () => {
    const store = storeWith(12)

    store.nextBlock()
    expect(store.currentBlock).toBe(2)
    store.nextBlock()

    expect(store.currentBlock).toBe(2)
    expect(store.status).toBe('objectives-completed')
  })

  it('un 5 sin justificación deja el bloque incompleto', () => {
    const store = storeWith(6)
    answerCurrentBlock(store, 3)
    expect(store.isCurrentBlockComplete).toBe(true)

    store.setAnswer(101, 5, '')

    expect(store.isCurrentBlockComplete).toBe(false)
    store.setAnswer(101, 5, 'Me apasiona')
    expect(store.isCurrentBlockComplete).toBe(true)
  })
})

describe('athenaSession · sesión restaurada', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('acota un bloque guardado mayor que el nuevo total sin perder respuestas', () => {
    const store = storeWith(43)
    store.$patch({ currentBlock: 11, answers: { 101: { valoracion: 4, justificacion: 'ok' } } })

    store.clampCurrentBlock()

    expect(store.currentBlock).toBe(8)
    expect(store.progress.currentBlock).toBe(8)
    expect(store.answers[101]).toEqual({ valoracion: 4, justificacion: 'ok' })
  })

  it.each([[Number.NaN], [0], [2.5], [-3]])('convierte un bloque guardado inválido (%s) en 1', (value) => {
    const store = storeWith(43)
    store.$patch({ currentBlock: value })

    store.clampCurrentBlock()

    expect(store.currentBlock).toBe(1)
  })

  it('sin objetivos deja el bloque en 1', () => {
    const store = useAthenaSessionStore()
    store.$patch({ currentBlock: 5 })

    store.clampCurrentBlock()

    expect(store.currentBlock).toBe(1)
  })
})
