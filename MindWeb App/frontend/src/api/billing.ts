import { api } from './client'

export const billingApi = {
  subscribe: (priceId: string) =>
    api.post<{ checkout_url: string }>('/billing/subscribe', { price_id: priceId }),
}
