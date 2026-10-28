import type { VocationalProfile } from '../types'

export const SAMPLE_PROFILE: VocationalProfile = {
  dominantRiasecId: 2,
  title: 'Investigador',
  tagline: 'Encuentras posibilidades donde otros ven preguntas.',
  summary: 'tu curiosidad abre caminos donde investigar, analizar y crear soluciones.',
  traits: ['Analítico', 'Curioso', 'Reflexivo'],
  scores: [
    { riasecId: 1, score: 0.72 },
    { riasecId: 2, score: 0.96 },
    { riasecId: 3, score: 0.84 },
    { riasecId: 4, score: 0.7 },
    { riasecId: 5, score: 0.55 },
    { riasecId: 6, score: 0.5 }
  ],
  careers: [
    { rank: 1, name: 'Ciencia de Datos', schools: ['ESCOM'], match: 96 },
    { rank: 2, name: 'Ingeniería en Sistemas Computacionales', schools: ['ESCOM'], match: 92 },
    { rank: 3, name: 'Física', schools: ['ESFM'], match: 88 }
  ]
}
