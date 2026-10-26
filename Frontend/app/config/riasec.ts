// Límite de habilidades/criterios que el usuario puede marcar como prioritarios
// por dimensión RIASEC. No es solo una decisión de UX: el backend evalúa cada
// criterio marcado como prioritario con una pregunta adicional a Jev, y el área
// más grande (43 carreras) excede el límite de contexto de Jev si se permite
// marcar todos los criterios disponibles. 11 por dimensión es el máximo medido
// que mantiene la llamada dentro del límite con margen de seguridad.
export const MAX_CRITERIOS_POR_DIMENSION = 11
