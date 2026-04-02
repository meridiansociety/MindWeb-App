import { useMemo } from 'react'
import { useGraph } from '../hooks/useGraph'
import { nodeColor } from '../utils/theme'
import { capitalize, formatDate } from '../utils/formatters'
import type { NodeResponse } from '../api/graph'

function groupByDate(nodes: NodeResponse[]): Record<string, NodeResponse[]> {
  return nodes.reduce<Record<string, NodeResponse[]>>((acc, node) => {
    const date = formatDate(node.created_at)
    if (!acc[date]) acc[date] = []
    acc[date].push(node)
    return acc
  }, {})
}

export default function Timeline() {
  const { nodes, isLoading } = useGraph()

  const sorted = useMemo(
    () => [...nodes].sort((a, b) => b.created_at.localeCompare(a.created_at)),
    [nodes]
  )

  const grouped = useMemo(() => groupByDate(sorted), [sorted])
  const dates = Object.keys(grouped)

  return (
    <div className="h-full overflow-y-auto px-8 py-6 max-w-2xl mx-auto w-full">
      <h1 className="text-xl font-semibold text-white mb-6">Knowledge Timeline</h1>

      {isLoading && nodes.length === 0 && (
        <div className="text-gray-600 text-sm">Loading…</div>
      )}

      {!isLoading && nodes.length === 0 && (
        <p className="text-gray-600 text-sm">
          No knowledge nodes yet. Add your first entry from the graph view.
        </p>
      )}

      <div className="space-y-8">
        {dates.map((date) => (
          <div key={date}>
            {/* Date header */}
            <div className="flex items-center gap-4 mb-3">
              <div className="h-px flex-1 bg-gray-800" />
              <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                {date}
              </span>
              <div className="h-px flex-1 bg-gray-800" />
            </div>

            {/* Nodes for this date */}
            <div className="space-y-2 pl-2">
              {grouped[date].map((node) => (
                <div
                  key={node.id}
                  className="flex items-start gap-3 bg-gray-900/60 border border-gray-800 rounded-xl px-4 py-3"
                >
                  {/* Type dot */}
                  <div
                    className="w-2 h-2 rounded-full mt-1.5 shrink-0"
                    style={{ background: nodeColor(node.type) }}
                  />
                  <div className="flex-1 min-w-0">
                    <p className="text-white text-sm font-medium leading-snug">{node.label}</p>
                    <p className="text-gray-600 text-xs mt-0.5">{capitalize(node.type)}</p>
                  </div>
                  <span className="text-gray-700 text-xs shrink-0">
                    {node.connection_count} conn
                  </span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
