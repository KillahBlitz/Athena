export function shuffle<T>(items: readonly T[]): T[] {
  const result = [...items]
  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    const temp = result[i]!
    result[i] = result[j]!
    result[j] = temp
  }
  return result
}

export function pickRandomOptionIds(
  opciones: Record<string, string>,
  limit: number,
  preferredIds: readonly number[] = []
): number[] {
  const available = Object.keys(opciones).map(Number)
  const preferred = [...new Set(preferredIds)].filter(id => available.includes(id)).slice(0, limit)
  const rest = shuffle(available.filter(id => !preferred.includes(id))).slice(0, limit - preferred.length)
  return shuffle([...preferred, ...rest])
}
