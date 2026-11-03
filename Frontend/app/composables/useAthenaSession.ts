import { useAthenaSessionStore } from '../stores/athenaSession'

export function useAthenaSession() {
  const store = useAthenaSessionStore()
  return store
}
