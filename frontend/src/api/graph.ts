import { api } from './client'

export interface NodeResponse {
  id: string
  label: string
  type: 'concept' | 'book' | 'author' | 'skill'
  created_at: string
  connection_count: number
}

export interface EdgeResponse {
  source_id: string
  target_id: string
  type: string
  weight: number
  inferred: boolean
}

export interface GraphPayload {
  nodes: NodeResponse[]
  edges: EdgeResponse[]
}

export interface NodeDetailResponse extends NodeResponse {
  edges: EdgeResponse[]
}

export const graphApi = {
  fetchGraph: (limit = 500, offset = 0) =>
    api.get<GraphPayload>('/graph', { params: { limit, offset } }),

  fetchNode: (nodeId: string) =>
    api.get<NodeDetailResponse>(`/graph/nodes/${nodeId}`),

  deleteNode: (nodeId: string) =>
    api.delete(`/graph/nodes/${nodeId}`),
}
