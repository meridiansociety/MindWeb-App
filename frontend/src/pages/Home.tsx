import { useState } from 'react'
import GraphCanvas from '../components/graph/GraphCanvas'
import NodeCard from '../components/graph/NodeCard'
import KnowledgeInputBar from '../components/input/KnowledgeInputBar'
import SuggestionPanel from '../components/suggestions/SuggestionPanel'
import GatingBanner from '../components/layout/GatingBanner'
import { useGraph } from '../hooks/useGraph'
import { graphApi } from '../api/graph'
import type { NodeDetailResponse } from '../api/graph'
import { FREE_NODE_LIMIT } from '../utils/constants'

export default function Home() {
  const { nodes, edges, isLoading, submitEntry, deleteNode, selectNode } = useGraph()
  const [selectedNode, setSelectedNode] = useState<NodeDetailResponse | null>(null)

  const handleNodeClick = async (nodeId: string) => {
    selectNode(nodeId)
    try {
      const { data } = await graphApi.fetchNode(nodeId)
      setSelectedNode(data)
    } catch {
      // node fetch failed silently
    }
  }

  const handleDeleteNode = async (nodeId: string) => {
    await deleteNode(nodeId)
    setSelectedNode(null)
  }

  const handleClose = () => {
    setSelectedNode(null)
    selectNode(null)
  }

  return (
    <div className="flex flex-col h-full">
      <GatingBanner type="nodes" current={nodes.length} />

      {/* Input bar */}
      <div className="shrink-0 border-b border-gray-800 px-4 py-3">
        <KnowledgeInputBar />
      </div>

      {/* Main area: graph + suggestions sidebar */}
      <div className="flex flex-1 min-h-0">
        {/* Graph canvas */}
        <div className="flex-1 relative min-w-0">
          {isLoading && nodes.length === 0 ? (
            <div className="flex items-center justify-center h-full text-gray-600 text-sm">
              Loading your graph…
            </div>
          ) : nodes.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center px-8">
              <div className="text-5xl mb-4 opacity-20">◎</div>
              <p className="text-gray-500 text-sm max-w-xs">
                Your knowledge graph is empty. Add your first entry above to get started.
              </p>
            </div>
          ) : (
            <GraphCanvas
              nodes={nodes}
              edges={edges}
              onNodeClick={handleNodeClick}
            />
          )}

          {selectedNode && (
            <NodeCard
              node={selectedNode}
              onClose={handleClose}
              onDelete={handleDeleteNode}
            />
          )}
        </div>

        {/* Suggestions sidebar */}
        <div className="w-72 shrink-0 border-l border-gray-800 overflow-hidden">
          <SuggestionPanel />
        </div>
      </div>
    </div>
  )
}
