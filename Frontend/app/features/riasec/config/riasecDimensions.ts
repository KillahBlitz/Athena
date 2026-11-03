import type { RiasecDimension } from '../../../types/riasec'

export const RIASEC_DIMENSIONS: Record<number, RiasecDimension> = {
  1: {
    name: 'Realista',
    tagline: 'Hacer · construir · operar',
    icon: ['M14.7 6.3a4 4 0 0 0-5.4 5.4L3 18l3 3 6.3-6.3a4 4 0 0 0 5.4-5.4l-2.6 2.6-2.4-.6-.6-2.4z']
  },
  2: {
    name: 'Investigador',
    tagline: 'Explorar · comprender · descubrir',
    icon: ['M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14z', 'M20 20l-4-4']
  },
  3: {
    name: 'Artístico',
    tagline: 'Crear · imaginar · expresar',
    icon: ['M12 3a9 9 0 1 0 0 18c1.1 0 1.5-.8 1.5-1.5 0-1.2-1-1.5-1-2.5 0-.8.7-1.5 1.5-1.5H16a5 5 0 0 0 5-5c0-4.1-4-7.5-9-7.5z', 'M7.5 11.5h.01M10 7.5h.01M15 7.5h.01']
  },
  4: {
    name: 'Social',
    tagline: 'Ayudar · enseñar · colaborar',
    icon: ['M9 11a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7z', 'M2.5 20a6.5 6.5 0 0 1 13 0', 'M16 4.5a3.5 3.5 0 0 1 0 6.5', 'M18 14a6.5 6.5 0 0 1 3.5 6']
  },
  5: {
    name: 'Emprendedor',
    tagline: 'Liderar · persuadir · emprender',
    icon: ['M3 17l6-6 4 4 8-8', 'M15 7h6v6']
  },
  6: {
    name: 'Convencional',
    tagline: 'Organizar · ordenar · verificar',
    icon: ['M9 4h6v3H9z', 'M15 5.5h2a2 2 0 0 1 2 2V19a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V7.5a2 2 0 0 1 2-2h2', 'M9 14l2 2 4-4']
  }
}

export const FALLBACK_DIMENSION: RiasecDimension = {
  name: 'Perfil',
  tagline: 'Reconoce lo que se te da bien',
  icon: ['M12 3l2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5z']
}

export function getRiasecDimension(riasecId: number): RiasecDimension {
  return RIASEC_DIMENSIONS[riasecId] ?? FALLBACK_DIMENSION
}
