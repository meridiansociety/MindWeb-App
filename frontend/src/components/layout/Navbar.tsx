import { useAuth } from '../../hooks/useAuth'
import { useGraphStore } from '../../store/graphStore'

export default function Navbar() {
  const { signOut } = useAuth()
  const nodeCount = useGraphStore((s) => s.nodes.length)

  return (
    <header className="h-12 bg-gray-950 border-b border-gray-800 flex items-center justify-between px-4 shrink-0">
      <div className="flex items-center gap-3">
        <span className="text-white font-bold tracking-tight">MindWeb</span>
        {nodeCount > 0 && (
          <span className="text-xs text-gray-500">
            {nodeCount} node{nodeCount !== 1 ? 's' : ''}
          </span>
        )}
      </div>

      <button
        onClick={signOut}
        className="text-xs text-gray-500 hover:text-gray-300 transition-colors"
      >
        Sign out
      </button>
    </header>
  )
}
