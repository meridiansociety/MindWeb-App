import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { billingApi } from '../api/billing'
import { useAuthStore } from '../store/authStore'
import { useGraphStore } from '../store/graphStore'
import { FREE_NODE_LIMIT } from '../utils/constants'
import { useAuth } from '../hooks/useAuth'

export default function Settings() {
  const [searchParams] = useSearchParams()
  const checkoutStatus = searchParams.get('checkout')
  const { signOut } = useAuth()
  const nodeCount = useGraphStore((s) => s.nodes.length)
  const [upgrading, setUpgrading] = useState(false)
  const [upgradeError, setUpgradeError] = useState<string | null>(null)

  // In production, tier would come from the API; stored in auth state for simplicity here
  const priceId = import.meta.env.VITE_STRIPE_PREMIUM_PRICE_ID ?? ''

  const handleUpgrade = async () => {
    setUpgrading(true)
    setUpgradeError(null)
    try {
      const { data } = await billingApi.subscribe(priceId)
      window.location.href = data.checkout_url
    } catch (err: any) {
      setUpgradeError(err.response?.data?.detail ?? 'Failed to start checkout')
    } finally {
      setUpgrading(false)
    }
  }

  return (
    <div className="h-full overflow-y-auto px-8 py-6 max-w-xl mx-auto w-full">
      <h1 className="text-xl font-semibold text-white mb-6">Settings</h1>

      {checkoutStatus === 'success' && (
        <div className="mb-6 bg-green-950/50 border border-green-800 rounded-xl px-4 py-3 text-sm text-green-300">
          Subscription activated — welcome to Premium!
        </div>
      )}
      {checkoutStatus === 'cancelled' && (
        <div className="mb-6 bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-sm text-gray-400">
          Checkout cancelled. Your account remains on the free tier.
        </div>
      )}

      {/* Usage */}
      <section className="bg-gray-900 border border-gray-800 rounded-xl p-5 mb-4">
        <h2 className="text-sm font-semibold text-gray-200 mb-4">Usage</h2>
        <div className="space-y-3">
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-400">Nodes</span>
              <span className="text-gray-300">
                {nodeCount} / {FREE_NODE_LIMIT}
              </span>
            </div>
            <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-brand-600 rounded-full transition-all"
                style={{ width: `${Math.min(100, (nodeCount / FREE_NODE_LIMIT) * 100)}%` }}
              />
            </div>
          </div>
        </div>
      </section>

      {/* Plan */}
      <section className="bg-gray-900 border border-gray-800 rounded-xl p-5 mb-4">
        <h2 className="text-sm font-semibold text-gray-200 mb-1">Plan</h2>
        <p className="text-gray-500 text-xs mb-4">Free tier — 50 nodes, 3 suggestions/day</p>

        {upgradeError && (
          <p className="text-xs text-red-400 mb-3">{upgradeError}</p>
        )}

        <button
          onClick={handleUpgrade}
          disabled={upgrading || !priceId}
          className="w-full bg-brand-600 hover:bg-brand-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium py-2.5 rounded-lg text-sm transition-colors"
        >
          {upgrading ? 'Redirecting to Stripe…' : 'Upgrade to Premium — Unlimited'}
        </button>
        {!priceId && (
          <p className="text-xs text-gray-600 mt-2 text-center">
            Set VITE_STRIPE_PREMIUM_PRICE_ID in your .env to enable billing.
          </p>
        )}
      </section>

      {/* Account */}
      <section className="bg-gray-900 border border-gray-800 rounded-xl p-5">
        <h2 className="text-sm font-semibold text-gray-200 mb-4">Account</h2>
        <button
          onClick={signOut}
          className="text-sm text-red-500 hover:text-red-400 transition-colors"
        >
          Sign out
        </button>
      </section>
    </div>
  )
}
