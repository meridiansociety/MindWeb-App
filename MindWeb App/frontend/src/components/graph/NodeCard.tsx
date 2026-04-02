import { useState } from 'react'
import type { NodeDetailResponse } from '../../api/graph'
import { capitalize, formatDate } from '../../utils/formatters'
import { nodeColor } from '../../utils/theme'

interface Props {
  node: NodeDetailResponse
  onClose: () => void
  onDelete: (nodeId: string) => void
}

export default function NodeCard({ node, onClose, onDelete }: Props) {
  const [confirmDelete, setConfirmDelete] = useState(false)

  return (
    <div className="absolute right-4 top-4 z-10 w-72 bg-gray-900 border border-gray-700 rounded-xl shadow-2xl overflow-hidden">
      {/* Header */}
      <div
        className="px-4 py-3 flex items-center justify-between"
        style={{ borderBottom: `2px solid ${nodeColor(node.type)}` }}
      >
        <div>
          <span
            className="text-xs font-semibold uppercase tracking-widest px-2 py-0.5 rounded"
            style={{ background: nodeColor(node.type), color: '#fff' }}
          >
            {node.type}
          </span>
          <h3 className="mt-1.5 text-white font-semibold text-base leading-tight">{node.label}</h3>
        </div>
        <button
          onClick={onClose}
          className="text-gray-500 hover:text-gray-300 ml-3 shrink-0"
          aria-label="Close"
        >
          ✕
        </button>
      </div>

      {/* Meta */}
      <div className="px-4 py-3 space-y-2 text-sm text-gray-400">
        <div className="flex justify-between">
          <span>Added</span>
          <span className="text-gray-300">{formatDate(node.created_at)}</span>
        </div>
        <div className="flex justify-between">
          <span>Connections</span>
          <span className="text-gray-300">{node.connection_count}</span>
        </div>
      </div>

      {/* Edges */}
      {node.edges.length > 0 && (
        <div className="px-4 pb-3">
          <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">Connected to</p>
          <ul className="space-y-1">
            {node.edges.slice(0, 5).map((e) => (
              <li key={`${e.source_id}-${e.target_id}`} className="text-xs text-gray-400 flex gap-2">
                <span className="text-gray-600">{capitalize(e.type)}</span>
                <span className="text-gray-300 truncate">{e.target_id.slice(0, 8)}…</span>
                <span className="ml-auto text-gray-600">{Math.round(e.weight * 100)}%</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Delete */}
      <div className="px-4 pb-4">
        {confirmDelete ? (
          <div className="flex gap-2">
            <button
              onClick={() => onDelete(node.id)}
              className="flex-1 bg-red-700 hover:bg-red-600 text-white text-sm py-1.5 rounded-lg transition-colors"
            >
              Confirm delete
            </button>
            <button
              onClick={() => setConfirmDelete(false)}
              className="flex-1 bg-gray-800 hover:bg-gray-700 text-gray-300 text-sm py-1.5 rounded-lg transition-colors"
            >
              Cancel
            </button>
          </div>
        ) : (
          <button
            onClick={() => setConfirmDelete(true)}
            className="w-full text-red-500 hover:text-red-400 text-sm py-1.5 hover:bg-red-950/30 rounded-lg transition-colors"
          >
            Delete node
          </button>
        )}
      </div>
    </div>
  )
}
