export interface StepConfig {
  number: number
  label: string
  path?: string
  isFunctional: boolean
}

export const athenaSteps: StepConfig[] = [
  { number: 1, label: 'Introducción', path: '/', isFunctional: true },
  { number: 2, label: 'Datos personales', path: '/datos-personales', isFunctional: true },
  { number: 3, label: 'Objetivos', path: '/objetivos', isFunctional: true },
  { number: 4, label: 'RISEC', path: '/riasec', isFunctional: true },
  { number: 5, label: 'Resultados', isFunctional: false }
]
