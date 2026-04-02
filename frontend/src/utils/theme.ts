import { NODE_COLORS } from './constants'

export function nodeColor(type: string): string {
  return NODE_COLORS[type] ?? '#6b7280'
}

export function nodeTextColor(_type: string): string {
  return '#ffffff'
}

export function edgeColor(weight: number): string {
  // Stronger edges are brighter
  const alpha = Math.round(weight * 200 + 55)
  return `rgba(91, 106, 245, ${(alpha / 255).toFixed(2)})`
}
