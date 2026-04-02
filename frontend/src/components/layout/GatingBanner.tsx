import { useNavigate } from 'react-router-dom'
import { FREE_NODE_LIMIT, FREE_SUGGESTIONS_PER_DAY } from '../../utils/constants'

interface Props {
  type: 'nodes' | 'suggestions'
  current?: number
}

export default function GatingBanner({ type, current }: Props) {
  const navigate = useNavigate()
  const limit = type === 'nodes' ? FREE_NODE_LIMIT : FREE_SUGGESTIONS_PER_DAY

  const isAtLimit = current !== undefined && current >= limit
  const isNearLimit = current !== undefined && current >= limit * 0.8 && !isAtLimit

  if (!isAtLimit && !isNearLimit) return null

  return (
    <div
      className={`px-4 py-2.5 text-sm flex items-center justify-between gap-4 ${
        isAtLimit
          ? 'bg-red-950/60 border-b border-red-800 text-red-300'
          : 'bg-amber-950/40 border-b border-amber-800/60 text-amber-300'
      }`}
    >
      <span>
        {isAtLimit
          ? type === 'nodes'
            ? `You've reached the free limit of ${limit} nodes.`
            : `You've used all ${limit} suggestions for today.`
          : type === 'nodes'
          ? `${limit - (current ?? 0)} node slots remaining on free tier.`
          : `${limit - (current ?? 0)} suggestion${limit - (current ?? 0) !== 1 ? 's' : ''} remaining today.`}
      </span>
      <button
        onClick={() => navigate('/settings')}
        className={`shrink-0 text-xs font-medium px-3 py-1 rounded-full transition-colors ${
          isAtLimit
            ? 'bg-red-700 hover:bg-red-600 text-white'
            : 'bg-amber-700/60 hover:bg-amber-600/60 text-amber-100'
        }`}
      >
        Upgrade to Premium
      </button>
    </div>
  )
}
