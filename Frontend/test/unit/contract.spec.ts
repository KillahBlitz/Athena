import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import ObjectiveCard from '../../app/features/objetivos/components/ObjectiveCard.vue'
import type { BackendQuestionaryResponseDTO } from '../../app/types/area'
import { createObjectiveBlocks, normalizeObjectives } from '../../app/features/objetivos/utils/createObjectiveBlocks'
import { OBJECTIVES_PER_BLOCK } from '../../app/config/objectives'

const SAMPLE_PATH = resolve(import.meta.dirname, '../../../Backend/src/tests/fixtures/questionary_response.sample.json')
const sample = JSON.parse(readFileSync(SAMPLE_PATH, 'utf-8')) as BackendQuestionaryResponseDTO

describe('contrato GET /{area_id}', () => {
  it('expone los campos que consume el frontend con sus tipos', () => {
    expect(typeof sample.area_id).toBe('number')
    expect(typeof sample.nom_area).toBe('string')
    expect(Array.isArray(sample.objetivos)).toBe(true)
    for (const objetivo of sample.objetivos) {
      expect(Number.isInteger(objetivo.id_carrera)).toBe(true)
      expect(Number.isInteger(objetivo.id_objetivo)).toBe(true)
      expect(objetivo.pregunta === null || typeof objetivo.pregunta === 'string').toBe(true)
    }
    for (const pregunta of sample.preguntas) {
      expect(typeof pregunta.riasec_id).toBe('number')
      expect(typeof pregunta.texto_pregunta).toBe('string')
      expect(typeof pregunta.pregunta_abierta).toBe('string')
      expect(Object.keys(pregunta.opciones).every(id => Number.isInteger(Number(id)))).toBe(true)
    }
  })

  it('lee pregunta de la lista de objetivos y descarta los textos nulos', () => {
    const objectives = normalizeObjectives(sample.objetivos)

    expect(objectives.map(o => o.carreraId)).toEqual([101, 102, 103, 104, 105, 106, 107])
    expect(objectives.every(o => o.pregunta.length > 0 && o.valoracion === null)).toBe(true)
  })

  it('conserva ambos identificadores sin usar la posición en la lista como id', () => {
    const objectives = normalizeObjectives([{ id_objetivo: 7, id_carrera: 42, pregunta: ' Diseñar soluciones ' }])

    expect(objectives[0]).toMatchObject({ objectiveId: 7, carreraId: 42, pregunta: 'Diseñar soluciones' })
  })

  it('pinta el valor de pregunta en la tarjeta del objetivo', () => {
    const objective = normalizeObjectives(sample.objetivos)[0]!
    const wrapper = mount(ObjectiveCard, {
      props: { objective, answer: { valoracion: null, justificacion: '' } },
      global: { stubs: { RatingScale: true } }
    })

    expect(wrapper.get('h2').text()).toBe(sample.objetivos[0]!.pregunta)
    wrapper.unmount()
  })

  it('muestra etiqueta opcional al seleccionar valoración 2 o 3', () => {
    const objective = normalizeObjectives(sample.objetivos)[0]!
    const wrapper = mount(ObjectiveCard, {
      props: { objective, answer: { valoracion: 2, justificacion: '' } },
      global: { stubs: { RatingScale: true } }
    })
    expect(wrapper.find('.justification-optional').text()).toBe('· Es opcional')
    expect(wrapper.find('.justification-required').exists()).toBe(false)
    wrapper.unmount()

    const wrapper3 = mount(ObjectiveCard, {
      props: { objective, answer: { valoracion: 3, justificacion: '' } },
      global: { stubs: { RatingScale: true } }
    })
    expect(wrapper3.find('.justification-optional').text()).toBe('· Es opcional')
    expect(wrapper3.find('.justification-required').exists()).toBe(false)
    wrapper3.unmount()
  })

  it('muestra etiqueta obligatorio al seleccionar valoración 4 o 5', () => {
    const objective = normalizeObjectives(sample.objetivos)[0]!
    const wrapper = mount(ObjectiveCard, {
      props: { objective, answer: { valoracion: 4, justificacion: '' } },
      global: { stubs: { RatingScale: true } }
    })
    expect(wrapper.find('.justification-required').text()).toBe('· Obligatorio contestar')
    expect(wrapper.find('.justification-optional').exists()).toBe(false)
    wrapper.unmount()
  })

  it('no muestra etiquetas cuando la valoración es 1 o null', () => {
    const objective = normalizeObjectives(sample.objetivos)[0]!
    const wrapper1 = mount(ObjectiveCard, {
      props: { objective, answer: { valoracion: 1, justificacion: '' } },
      global: { stubs: { RatingScale: true } }
    })
    expect(wrapper1.find('.justification-optional').exists()).toBe(false)
    expect(wrapper1.find('.justification-required').exists()).toBe(false)
    wrapper1.unmount()

    const wrapperNull = mount(ObjectiveCard, {
      props: { objective, answer: { valoracion: null, justificacion: '' } },
      global: { stubs: { RatingScale: true } }
    })
    expect(wrapperNull.find('.justification-optional').exists()).toBe(false)
    expect(wrapperNull.find('.justification-required').exists()).toBe(false)
    wrapperNull.unmount()
  })

  it('agrupa los objetivos normalizados en bloques de como máximo 6', () => {
    const blocks = createObjectiveBlocks(normalizeObjectives(sample.objetivos), OBJECTIVES_PER_BLOCK)

    expect(OBJECTIVES_PER_BLOCK).toBe(6)
    expect(blocks.map(b => b.objectives.length)).toEqual([6, 1])
    expect(blocks.map(b => b.totalBlocks)).toEqual([2, 2])
  })
})
