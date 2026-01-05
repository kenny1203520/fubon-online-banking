import apiClient from '../../../shared/services/api'
import type {
  UtilityService,
  UtilityBillListResponse,
  PayBillRequest,
  PayBillResponse,
  PaymentHistoryResponse,
  BillFilterOptions
} from '../types'

export const utilityService = {
  /**
   * 取得可用的繳費服務列表
   */
  getServices: () =>
    apiClient.get<UtilityService[]>('/api/v1/utilities/services'),

  /**
   * 取得使用者的繳費帳單列表
   */
  getBills: (options?: BillFilterOptions) => {
    const params = new URLSearchParams()
    if (options?.page) params.append('page', options.page.toString())
    if (options?.per_page) params.append('per_page', options.per_page.toString())
    if (options?.status) params.append('status', options.status)
    if (options?.bill_type) params.append('bill_type', options.bill_type)

    return apiClient.get<UtilityBillListResponse>(
      `/api/v1/utilities/bills${params.toString() ? '?' + params.toString() : ''}`
    )
  },

  /**
   * 支付帳單
   */
  payBill: (data: PayBillRequest) =>
    apiClient.post<PayBillResponse>('/api/v1/utilities/pay-bill', data),

  /**
   * 取得繳費記錄
   */
  getPaymentHistory: (options?: BillFilterOptions) => {
    const params = new URLSearchParams()
    if (options?.page) params.append('page', options.page.toString())
    if (options?.per_page) params.append('per_page', options.per_page.toString())
    if (options?.bill_id) params.append('bill_id', options.bill_id.toString())

    return apiClient.get<PaymentHistoryResponse>(
      `/api/v1/utilities/history${params.toString() ? '?' + params.toString() : ''}`
    )
  },
}
