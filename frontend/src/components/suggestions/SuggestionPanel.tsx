import { useEffect } from 'react'
import { useSuggestions } from '../../hooks/useSuggestions'
import SuggestionCard from './SuggestionCard'

export default function SuggestionPanel() {
  const { suggestions, isLoading, error, fetchSuggestions } = useSuggestions()

  useEffect(() => {
    fetchSuggestions()
  }, [fetchSuggestions])

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-800">
        <h2 className="text-sm font-semibold text-gray-200">Suggestions</h2>
        <button
          onClick={fetchSuggestions}
          disabled={isLoading}
          className="text-xs text-brand-400 hover:text-brand-300 disabled:opacity-40 transition-colors"
        >
          {isLoading ? 'Loading…' : 'Refresh'}
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3">
        {error && (
          <p className="text-xs text-red-400 bg-red-950/40 border border-red-800 rounded-lg px-3 py-2">
            {error}
          </p>
        )}

        {isLoading && !suggestions && (
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-20 bg-gray-800/40 rounded-xl animate-pulse" />
            ))}
          </div>
        )}

        {suggestions && (
          <>
            {suggestions.adjacent.map((item, i) => (
              <SuggestionCard key={`adj-${i}`} item={item} type="adjacent" />
            ))}
            {suggestions.bridge.map((item, i) => (
              <SuggestionCard key={`br-${i}`} item={item} type="bridge" />
            ))}
            {suggestions.gap.map((item, i) => (
              <SuggestionCard key={`gap-${i}`} item={item} type="gap" />
            ))}
          </>
        )}
      </div>
    </div>
  )
}
