import { create } from 'zustand'
import type { SuggestionSet } from '../api/suggestions'

interface SuggestionState {
  suggestions: SuggestionSet | null
  isLoading: boolean
  error: string | null
  setSuggestions: (s: SuggestionSet) => void
  setLoading: (v: boolean) => void
  setError: (e: string | null) => void
}

export const useSuggestionStore = create<SuggestionState>((set) => ({
  suggestions: null,
  isLoading: false,
  error: null,
  setSuggestions: (s) => set({ suggestions: s, error: null }),
  setLoading: (v) => set({ isLoading: v }),
  setError: (e) => set({ error: e }),
}))
