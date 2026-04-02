import type { EdgeResponse } from '../../api/graph'
import { capitalize, formatConfidence } from '../../utils/formatters'

interface Props {
  edge: EdgeResponse
  x: number
  y: number
}

export default function EdgeTooltip({ edge, x, y }: Props) {
  return (
    <div
      className="pointer-events-none absolute z-20 bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-xs shadow-xl"
      style={{ left: x + 8, top: y + 8 }}
    >
      <div className="text-gray-400">
        <span className="text-white font-medium">{capitalize(edge.type)}</span>
      </div>
      <div className="text-gray-500 mt-0.5">
        Strength: <span className="text-gray-300">{formatConfidence(edge.weight)}</span>
      </div>
      {edge.inferred && (
        <div className="text-gray-600 mt-0.5">Auto-inferred</div>
      )}
    </div>
  )
}
