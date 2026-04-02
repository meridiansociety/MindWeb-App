import { api } from './client'

export interface SuggestionItem {
  label: string
  rationale: string
  confidence: number
}

export interface SuggestionSet {
  adjacent: SuggestionItem[]
  bridge: SuggestionItem[]
  gap: SuggestionItem[]
}

export const suggestionsApi = {
  fetch: () => api.get<SuggestionSet>('/suggestions'),
}
