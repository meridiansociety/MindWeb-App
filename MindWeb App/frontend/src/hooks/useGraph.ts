import { useCallback, useEffect } from 'react'
import { graphApi } from '../api/graph'
import { entriesApi } from '../api/entries'
import { useGraphStore } from '../store/graphStore'

export function useGraph() {
  const { nodes, edges, isLoading, setGraph, addNodes, removeNode, setLoading, selectedNodeId, selectNode } =
    useGraphStore()

  const fetchGraph = useCallback(async () => {
    setLoading(true)
    try {
      const { data } = await graphApi.fetchGraph()
      setGraph(data.nodes, data.edges)
    } finally {
      setLoading(false)
    }
  }, [setGraph, setLoading])

  useEffect(() => {
    fetchGraph()
  }, [fetchGraph])

  const submitEntry = useCallback(
    async (text: string): Promise<void> => {
      const { data: entry } = await entriesApi.submit(text)

      // Poll until complete (V1 polling; V2 will use WebSocket)
      const poll = async () => {
        const { data } = await entriesApi.poll(entry.entry_id)
        if (data.status === 'complete') {
          // Refresh graph to pull in new nodes
          const { data: graph } = await graphApi.fetchGraph()
          setGraph(graph.nodes, graph.edges)
        } else if (data.status === 'pending' || data.status === 'processing') {
          setTimeout(poll, 1500)
        }
        // On 'failed', stop polling silently — UI shows entry state
      }
      setTimeout(poll, 1500)
    },
    [setGraph]
  )

  const deleteNode = useCallback(
    async (nodeId: string) => {
      await graphApi.deleteNode(nodeId)
      removeNode(nodeId)
    },
    [removeNode]
  )

  return { nodes, edges, isLoading, fetchGraph, submitEntry, deleteNode, selectedNodeId, selectNode }
}
