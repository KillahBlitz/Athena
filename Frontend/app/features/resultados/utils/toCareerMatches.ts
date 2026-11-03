import type { GetResultsCareerDTO } from '../../../types/api'
import type { CareerMatch } from '../types'

const RANKS = [1, 2, 3] as const

export function toCareerMatches(results: GetResultsCareerDTO[] | null | undefined): CareerMatch[] {
  if (!Array.isArray(results) || results.length === 0) {
    throw new Error('Tu evaluación terminó, pero no encontramos carreras recomendadas.')
  }
  const valid = results.filter(r =>
    typeof r?.carrera === 'string' && r.carrera.trim().length > 0 &&
    Number.isFinite(r.puntaje) && Number.isFinite(r.top)
  )
  if (valid.length === 0) {
    throw new Error('El servidor devolvió resultados con un formato inválido.')
  }

  return [...valid]
    .sort((a, b) => a.top - b.top)
    .slice(0, RANKS.length)
    .map((r, i) => ({
      rank: RANKS[i]!,
      name: r.carrera.trim(),
      schools: Array.isArray(r.escuelas) ? r.escuelas.filter(e => typeof e === 'string' && e.trim()) : [],
      match: Math.min(100, Math.max(0, r.puntaje))
    }))
}
