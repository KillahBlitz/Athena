import { beforeEach, describe, expect, it } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useAthenaSessionStore } from '../../app/stores/athenaSession'
import type { BackendQuestionaryResponseDTO } from '../../app/types/area'

function areaWithObjectives(count: number): BackendQuestionaryResponseDTO {
  const objetivos: BackendQuestionaryResponseDTO['objetivos'] = []
  for (let i = 1; i <= count; i++) {
    objetivos.push({ id_objetivo: 100 + i, id_carrera: 100 + i, pregunta: `Objetivo ${i}` })
  }
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
    localStorage.clear()
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

  it('un 4 sin justificación no bloquea el avance (es opcional)', () => {
    const store = storeWith(6)
    answerCurrentBlock(store, 3)

    store.setAnswer(101, 4, '')

    expect(store.isCurrentBlockComplete).toBe(true)
  })
})

describe('athenaSession · sesión restaurada', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
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

  it('guarda y restaura la carrera del objetivo para enviarla a save-user', () => {
    const store = useAthenaSessionStore()
    store.setAreaData({
      area_id: 1,
      nom_area: 'Área de prueba',
      objetivos: [{ id_objetivo: 7, id_carrera: 42, pregunta: 'Diseñar soluciones' }],
      preguntas: [
        { riasec_id: 1, texto_pregunta: 'Actividades', pregunta_abierta: 'Explica', opciones: { '11': 'Reparar' } },
        { riasec_id: 6, texto_pregunta: 'Organización', pregunta_abierta: 'Explica', opciones: { '61': 'Organizar' } }
      ]
    })
    store.setAnswer(42, 4, ' Me interesa ')
    store.toggleRiasecOption(1, 11)
    store.setRiasecOpenAnswer(1, ' Reparo aparatos ')
    store.toggleRiasecOption(6, 61)
    store.setRiasecOpenAnswer(6, ' Organizo tareas ')

    const saved = JSON.parse(localStorage.getItem('athena_session_v2')!)
    expect(saved.areaData.objetivos[0]).toMatchObject({ id_objetivo: 7, id_carrera: 42, pregunta: 'Diseñar soluciones' })
    expect(saved.objectives[0]).toMatchObject({ objectiveId: 7, carreraId: 42 })

    setActivePinia(createPinia())
    const restored = useAthenaSessionStore()
    restored.restore()

    expect(restored.objectives[0]?.pregunta).toBe('Diseñar soluciones')
    expect(restored.progress.answeredCount).toBe(1)
    expect(restored.saveUserPayload.objetives).toEqual([
      { id_objetive: 7, id_carrera: 42, puntuation: 4, description: 'Me interesa' }
    ])
    expect(restored.saveUserPayload.risec_questions).toEqual({
      1: { risec_id: 1, criteria_list: [{ 11: 'Reparar' }], open_question: 'Reparo aparatos' },
      6: { risec_id: 6, criteria_list: [{ 61: 'Organizar' }], open_question: 'Organizo tareas' }
    })
  })

  it.each([
    'Diseñar soluciones',
    { id_carrera: 101, pregunta_objetivo: 'Diseñar soluciones' }
  ])('restaura el formato anterior %j sin perder respuestas', (objetivo) => {
    localStorage.setItem('athena_session_v2', JSON.stringify({
      areaData: { area_id: 1, nom_area: 'Área', objetivos: { '101': objetivo }, preguntas: [] },
      objectives: [{ carreraId: 101, pregunta: 'Diseñar soluciones' }],
      answers: { 101: { valoracion: 4, justificacion: 'Me interesa' } }
    }))
    const store = useAthenaSessionStore()

    store.restore()

    expect(store.objectives[0]).toMatchObject({ objectiveId: 101, carreraId: 101 })
    expect(store.saveUserPayload.objetives).toEqual([
      { id_objetive: 101, id_carrera: 101, puntuation: 4, description: 'Me interesa' }
    ])
  })
})
