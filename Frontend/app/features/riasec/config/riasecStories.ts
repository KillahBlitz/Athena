export interface StoryScene {
  title: string
  line: string
}

export const STORY_SCENE_COUNT = 3

const STORIES: Record<number, [string, string, string]> = {
  1: [
    '{avatar} encontró un taller lleno de piezas sueltas.',
    'Con las manos y un plan, todo empieza a encajar.',
    '¿Qué construirías tú si tuvieras todas las herramientas?'
  ],
  2: [
    '{avatar} vio una señal extraña en el cielo nocturno.',
    'Cada pregunta abre una puerta nueva.',
    'Las respuestas llegan a quien se atreve a investigar.'
  ],
  3: [
    '{avatar} encontró un lienzo en blanco… y muchas ideas.',
    'Los colores cuentan lo que las palabras no alcanzan.',
    'Tu forma de ver el mundo es única.'
  ],
  4: [
    '{avatar} llegó a una ciudad donde nadie se conocía.',
    'Una conversación bastó para unir a todos.',
    'Ayudar también es un superpoder.'
  ],
  5: [
    '{avatar} tuvo una idea a medianoche.',
    'Reunió a su equipo y se lanzaron.',
    'Liderar es dar el primer paso aunque dé miedo.'
  ],
  6: [
    '{avatar} encontró un archivo lleno de pistas desordenadas.',
    'Paso a paso, todo tomó su lugar.',
    'El orden convierte el caos en resultados.'
  ]
}

const FALLBACK_STORY: [string, string, string] = [
  '{avatar} empieza una nueva aventura.',
  'Cada elección revela algo de ti.',
  'Sigue explorando, vas muy bien.'
]

const SCENE_TITLES = ['El comienzo', 'El descubrimiento', 'Tu turno']

const REACTIONS = ['¡Buena elección!', '¡Eso dice mucho de ti!', '¡Sigue así!', '¡Otra conexión!']

export function storyFor(riasecId: number, avatarName: string): StoryScene[] {
  const lines = STORIES[riasecId] ?? FALLBACK_STORY
  return lines.map((line, index) => ({
    title: SCENE_TITLES[index] ?? '',
    line: line.replaceAll('{avatar}', avatarName)
  }))
}

export function reactionFor(selectionCount: number): string {
  const index = (Math.max(1, selectionCount) - 1) % REACTIONS.length
  return REACTIONS[index] ?? REACTIONS[0]!
}
