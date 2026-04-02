import { create } from 'zustand'
import type { NodeResponse, EdgeResponse } from '../api/graph'

interface GraphState {
  nodes: NodeResponse[]
  edges: EdgeResponse[]
  selectedNodeId: string | null
  isLoading: boolean
  setGraph: (nodes: NodeResponse[], edges: EdgeResponse[]) => void
  addNodes: (nodes: NodeResponse[]) => void
  removeNode: (nodeId: string) => void
  selectNode: (nodeId: string | null) => void
  setLoading: (v: boolean) => void
}

export const useGraphStore = create<GraphState>((set) => ({
  nodes: [],
  edges: [],
  selectedNodeId: null,
  isLoading: false,

  setGraph: (nodes, edges) => set({ nodes, edges }),

  addNodes: (newNodes) =>
    set((state) => ({
      nodes: [
        ...state.nodes.filter((n) => !newNodes.find((nn) => nn.id === n.id)),
        ...newNodes,
      ],
    })),

  removeNode: (nodeId) =>
    set((state) => ({
      nodes: state.nodes.filter((n) => n.id !== nodeId),
      edges: state.edges.filter(
        (e) => e.source_id !== nodeId && e.target_id !== nodeId
      ),
      selectedNodeId: state.selectedNodeId === nodeId ? null : state.selectedNodeId,
    })),

  selectNode: (nodeId) => set({ selectedNodeId: nodeId }),

  setLoading: (v) => set({ isLoading: v }),
}))
