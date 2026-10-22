import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'
import type { BackendQuestionaryResponseDTO } from '../../app/types/area'
import { createObjectiveBlocks, normalizeObjectives } from '../../app/features/objetivos/utils/createObjectiveBlocks'
import { OBJECTIVES_PER_BLOCK } from '../../app/config/objectives'

const SAMPLE_PATH = resolve(import.meta.dirname, '../../../Backend/src/tests/fixtures/questionary_response.sample.json')
const sample = JSON.parse(readFileSync(SAMPLE_PATH, 'utf-8')) as BackendQuestionaryResponseDTO

describe('contrato GET /{area_id}', () => {
  it('expone los campos que consume el frontend con sus tipos', () => {
    expect(typeof sample.area_id).toBe('number')
    expect(typeof sample.nom_area).toBe('string')
    for (const pregunta of sample.preguntas) {
      expect(typeof pregunta.riasec_id).toBe('number')
      expect(typeof pregunta.texto_pregunta).toBe('string')
      expect(typeof pregunta.pregunta_abierta).toBe('string')
      expect(Object.keys(pregunta.opciones).every(id => Number.isInteger(Number(id)))).toBe(true)
    }
  })

  it('normaliza objetivos con claves string a carreraId numérico y descarta los nulos', () => {
    const objectives = normalizeObjectives(sample.objetivos)

    expect(objectives.map(o => o.carreraId)).toEqual([101, 102, 103, 104, 105, 106, 107])
    expect(objectives.every(o => o.pregunta.length > 0 && o.valoracion === null)).toBe(true)
  })

  it('agrupa los objetivos normalizados en bloques de como máximo 6', () => {
    const blocks = createObjectiveBlocks(normalizeObjectives(sample.objetivos), OBJECTIVES_PER_BLOCK)

    expect(OBJECTIVES_PER_BLOCK).toBe(6)
    expect(blocks.map(b => b.objectives.length)).toEqual([6, 1])
    expect(blocks.map(b => b.totalBlocks)).toEqual([2, 2])
  })
})
