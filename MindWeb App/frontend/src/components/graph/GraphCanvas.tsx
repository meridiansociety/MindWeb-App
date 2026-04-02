import { useCallback, useMemo } from 'react'
import ReactFlow, {
  Background,
  BackgroundVariant,
  Controls,
  MiniMap,
  NodeMouseHandler,
  useEdgesState,
  useNodesState,
} from 'reactflow'
import 'reactflow/dist/style.css'
import type { NodeResponse, EdgeResponse } from '../../api/graph'
import { useGraphStore } from '../../store/graphStore'
import { nodeColor } from '../../utils/theme'

interface Props {
  nodes: NodeResponse[]
  edges: EdgeResponse[]
  onNodeClick: (nodeId: string) => void
}

function toFlowNodes(nodes: NodeResponse[]) {
  return nodes.map((n, i) => ({
    id: n.id,
    type: 'default',
    position: {
      x: (Math.cos((i / nodes.length) * 2 * Math.PI) * 400) + 600,
      y: (Math.sin((i / nodes.length) * 2 * Math.PI) * 300) + 400,
    },
    data: { label: n.label },
    style: {
      background: nodeColor(n.type),
      color: '#fff',
      border: 'none',
      borderRadius: '8px',
      padding: '8px 14px',
      fontSize: '13px',
      fontWeight: 500,
      boxShadow: '0 2px 8px rgba(0,0,0,0.4)',
      maxWidth: 160,
    },
  }))
}

function toFlowEdges(edges: EdgeResponse[]) {
  return edges.map((e) => ({
    id: `${e.source_id}-${e.target_id}`,
    source: e.source_id,
    target: e.target_id,
    type: 'default',
    animated: false,
    style: {
      stroke: `rgba(91,106,245,${Math.max(0.2, e.weight).toFixed(2)})`,
      strokeWidth: Math.max(1, e.weight * 3),
    },
    label: e.type,
    labelStyle: { fill: '#9ca3af', fontSize: 10 },
    labelBgStyle: { fill: 'transparent' },
  }))
}

export default function GraphCanvas({ nodes, edges, onNodeClick }: Props) {
  const [flowNodes, , onNodesChange] = useNodesState(useMemo(() => toFlowNodes(nodes), [nodes]))
  const [flowEdges, , onEdgesChange] = useEdgesState(useMemo(() => toFlowEdges(edges), [edges]))

  const handleNodeClick: NodeMouseHandler = useCallback(
    (_, node) => onNodeClick(node.id),
    [onNodeClick]
  )

  return (
    <div className="w-full h-full">
      <ReactFlow
        nodes={flowNodes}
        edges={flowEdges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={handleNodeClick}
        fitView
        minZoom={0.1}
        maxZoom={2}
        attributionPosition="bottom-right"
      >
        <Background variant={BackgroundVariant.Dots} gap={24} size={1} color="#1f2937" />
        <Controls className="!bg-gray-900 !border-gray-700" />
        <MiniMap
          nodeColor={(n) => {
            const original = nodes.find((node) => node.id === n.id)
            return original ? nodeColor(original.type) : '#374151'
          }}
          maskColor="rgba(3,7,18,0.8)"
          style={{ background: '#111827', border: '1px solid #1f2937' }}
        />
      </ReactFlow>
    </div>
  )
}
