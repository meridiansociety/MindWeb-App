import { useCallback } from 'react'
import { suggestionsApi } from '../api/suggestions'
import { useSuggestionStore } from '../store/suggestionStore'

export function useSuggestions() {
  const { suggestions, isLoading, error, setSuggestions, setLoading, setError } =
    useSuggestionStore()

  const fetchSuggestions = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const { data } = await suggestionsApi.fetch()
      setSuggestions(data)
    } catch (err: any) {
      const detail = err.response?.data?.detail ?? 'Failed to load suggestions'
      setError(detail)
    } finally {
      setLoading(false)
    }
  }, [setSuggestions, setLoading, setError])

  return { suggestions, isLoading, error, fetchSuggestions }
}
