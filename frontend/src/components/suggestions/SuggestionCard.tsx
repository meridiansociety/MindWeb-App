import type { SuggestionItem } from '../../api/suggestions'
import { formatConfidence } from '../../utils/formatters'

interface Props {
  item: SuggestionItem
  type: 'adjacent' | 'bridge' | 'gap'
}

const TYPE_STYLES = {
  adjacent: { badge: 'bg-brand-900 text-brand-300', label: 'Adjacent' },
  bridge:   { badge: 'bg-amber-900/60 text-amber-300', label: 'Bridge' },
  gap:      { badge: 'bg-rose-900/60 text-rose-300', label: 'Gap' },
}

export default function SuggestionCard({ item, type }: Props) {
  const style = TYPE_STYLES[type]

  return (
    <div className="bg-gray-800/60 border border-gray-700/60 rounded-xl p-4 space-y-2 hover:border-brand-600/50 transition-colors">
      <div className="flex items-start justify-between gap-2">
        <span className="text-white font-medium text-sm leading-snug">{item.label}</span>
        <span className={`shrink-0 text-xs font-medium px-2 py-0.5 rounded-full ${style.badge}`}>
          {style.label}
        </span>
      </div>
      <p className="text-gray-400 text-xs leading-relaxed">{item.rationale}</p>
      <div className="text-gray-600 text-xs">
        Confidence: <span className="text-gray-400">{formatConfidence(item.confidence)}</span>
      </div>
    </div>
  )
}
