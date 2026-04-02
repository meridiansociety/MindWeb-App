import { useMemo, useState } from 'react'
import { useGraph } from '../hooks/useGraph'
import { graphApi } from '../api/graph'
import type { NodeDetailResponse } from '../api/graph'
import NodeCard from '../components/graph/NodeCard'
import { nodeColor } from '../utils/theme'
import { capitalize, formatDate } from '../utils/formatters'

const TYPE_FILTERS = ['all', 'concept', 'book', 'author', 'skill'] as const
type Filter = (typeof TYPE_FILTERS)[number]

export default function Explore() {
  const { nodes, isLoading, deleteNode } = useGraph()
  const [filter, setFilter] = useState<Filter>('all')
  const [search, setSearch] = useState('')
  const [selectedNode, setSelectedNode] = useState<NodeDetailResponse | null>(null)

  const filtered = useMemo(() => {
    return nodes.filter((n) => {
      const matchType = filter === 'all' || n.type === filter
      const matchSearch =
        !search || n.label.toLowerCase().includes(search.toLowerCase())
      return matchType && matchSearch
    })
  }, [nodes, filter, search])

  const handleNodeClick = async (nodeId: string) => {
    try {
      const { data } = await graphApi.fetchNode(nodeId)
      setSelectedNode(data)
    } catch {
      // silent
    }
  }

  const handleDelete = async (nodeId: string) => {
    await deleteNode(nodeId)
    setSelectedNode(null)
  }

  return (
    <div className="flex h-full">
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Toolbar */}
        <div className="shrink-0 px-6 py-4 border-b border-gray-800 flex flex-wrap items-center gap-3">
          <input
            type="text"
            placeholder="Search nodes…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="bg-gray-900 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-brand-500/40 w-56"
          />
          <div className="flex gap-1">
            {TYPE_FILTERS.map((t) => (
              <button
                key={t}
                onClick={() => setFilter(t)}
                className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                  filter === t
                    ? 'bg-brand-700 text-white'
                    : 'text-gray-500 hover:text-gray-300 hover:bg-gray-800'
                }`}
              >
                {capitalize(t)}
              </button>
            ))}
          </div>
          <span className="text-xs text-gray-600 ml-auto">
            {filtered.length} node{filtered.length !== 1 ? 's' : ''}
          </span>
        </div>

        {/* Node grid */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {isLoading && nodes.length === 0 ? (
            <div className="text-gray-600 text-sm text-center mt-16">Loading…</div>
          ) : filtered.length === 0 ? (
            <div className="text-gray-600 text-sm text-center mt-16">No nodes match your filter.</div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
              {filtered.map((node) => (
                <button
                  key={node.id}
                  onClick={() => handleNodeClick(node.id)}
                  className="group text-left bg-gray-900 border border-gray-700 hover:border-brand-600/60 rounded-xl p-3 transition-colors"
                >
                  <div
                    className="w-2 h-2 rounded-full mb-2"
                    style={{ background: nodeColor(node.type) }}
                  />
                  <p className="text-white text-sm font-medium leading-snug line-clamp-2 group-hover:text-brand-300 transition-colors">
                    {node.label}
                  </p>
                  <p className="text-gray-600 text-xs mt-1.5">{capitalize(node.type)}</p>
                  <p className="text-gray-700 text-xs mt-0.5">{formatDate(node.created_at)}</p>
                  <p className="text-gray-600 text-xs mt-1">
                    {node.connection_count} connection{node.connection_count !== 1 ? 's' : ''}
                  </p>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Node detail panel */}
      {selectedNode && (
        <div className="w-72 shrink-0 border-l border-gray-800 relative">
          <NodeCard
            node={selectedNode}
            onClose={() => setSelectedNode(null)}
            onDelete={handleDelete}
          />
        </div>
      )}
    </div>
  )
}
