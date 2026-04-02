import { useState } from 'react'
import { useGraph } from '../../hooks/useGraph'

interface Props {
  onSubmitted?: () => void
}

export default function KnowledgeInputBar({ onSubmitted }: Props) {
  const [text, setText] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [status, setStatus] = useState<'idle' | 'processing' | 'done' | 'error'>('idle')
  const { submitEntry } = useGraph()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!text.trim() || submitting) return

    setSubmitting(true)
    setStatus('processing')
    try {
      await submitEntry(text.trim())
      setStatus('done')
      setText('')
      onSubmitted?.()
      setTimeout(() => setStatus('idle'), 3000)
    } catch {
      setStatus('error')
      setTimeout(() => setStatus('idle'), 4000)
    } finally {
      setSubmitting(false)
    }
  }

  const charCount = text.length

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="relative">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="What did you learn today? Describe a concept, book, idea, or insight…"
          maxLength={1000}
          rows={3}
          disabled={submitting}
          className="w-full bg-gray-900 border border-gray-700 focus:border-brand-500 rounded-xl px-4 py-3 text-white placeholder-gray-500 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-brand-500/30 disabled:opacity-60 transition-colors"
        />
        <div className="flex items-center justify-between mt-2 px-1">
          <span className="text-xs text-gray-600">
            {charCount}/1000
          </span>
          <div className="flex items-center gap-3">
            {status === 'processing' && (
              <span className="text-xs text-brand-400 animate-pulse">Extracting knowledge…</span>
            )}
            {status === 'done' && (
              <span className="text-xs text-green-400">Added to your graph</span>
            )}
            {status === 'error' && (
              <span className="text-xs text-red-400">Something went wrong</span>
            )}
            <button
              type="submit"
              disabled={submitting || charCount < 3}
              className="bg-brand-600 hover:bg-brand-500 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-medium px-5 py-2 rounded-lg transition-colors"
            >
              {submitting ? 'Adding…' : 'Add to graph'}
            </button>
          </div>
        </div>
      </div>
    </form>
  )
}
