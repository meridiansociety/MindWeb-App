import { api } from './client'

export interface EntryResponse {
  entry_id: string
  status: 'pending' | 'processing' | 'complete' | 'failed'
  nodes_created: number
}

export const entriesApi = {
  submit: (text: string) =>
    api.post<EntryResponse>('/entries', { text }),

  poll: (entryId: string) =>
    api.get<EntryResponse>(`/entries/${entryId}`),
}
