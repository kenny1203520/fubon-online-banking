import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { utilityService } from '../services/utility'
import type {
  UtilityService,
  UtilityBill,
  PaymentRecord,
  BillFilterOptions,
  PayBillRequest
} from '../types'

export const useUtilityStore = defineStore('utility', () => {
  // State
  const services = ref<UtilityService[]>([])
  const bills = ref<UtilityBill[]>([])
  const paymentHistory = ref<PaymentRecord[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const currentPage = ref(1)
  const pageSize = ref(10)
  const totalPages = ref(0)
  const totalCount = ref(0)

  // Computed
  const billStats = computed(() => {
    const pending = bills.value.filter(b => b.status === 'pending').length
    const paid = bills.value.filter(b => b.status === 'paid').length
    const overdue = bills.value.filter(b => b.status === 'overdue').length
    const totalAmount = bills.value
      .filter(b => b.status === 'pending' || b.status === 'overdue')
      .reduce((sum, b) => sum + b.amount, 0)

    return { pending, paid, overdue, totalAmount }
  })

  // Actions
  /**
   * 取得繳費服務列表
   */
  const fetchServices = async () => {
    isLoading.value = true
    error.value = null
    try {
      const response = await utilityService.getServices()
      services.value = response.data
    } catch (err: unknown) {
      const error_msg = err instanceof Error ? err.message : '取得服務列表失敗'
      error.value = error_msg
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 取得帳單列表
   */
  const fetchBills = async (options?: BillFilterOptions) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await utilityService.getBills({
        page: options?.page || currentPage.value,
        per_page: options?.per_page || pageSize.value,
        ...options
      })

      bills.value = response.data.items
      currentPage.value = response.data.page
      pageSize.value = response.data.per_page
      totalCount.value = response.data.total
      totalPages.value = response.data.total_pages
    } catch (err: unknown) {
      const error_msg = err instanceof Error ? err.message : '取得帳單列表失敗'
      error.value = error_msg
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 支付帳單
   */
  const payBill = async (data: PayBillRequest) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await utilityService.payBill(data)

      // 更新本地帳單狀態
      const billIndex = bills.value.findIndex(b => b.id === data.bill_id)
      if (billIndex !== -1) {
        const bill = bills.value[billIndex]
        if (bill) {
          bill.status = 'paid'
          bill.paid_at = response.data.created_at
        }
      }

      return response.data
    } catch (err: unknown) {
      const error_msg = err instanceof Error ? err.message : '支付失敗'
      error.value = error_msg
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 取得支付歷史
   */
  const fetchPaymentHistory = async (options?: BillFilterOptions) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await utilityService.getPaymentHistory(options)
      paymentHistory.value = response.data.items
      currentPage.value = response.data.page
      totalCount.value = response.data.total
      totalPages.value = response.data.total_pages
    } catch (err: unknown) {
      const error_msg = err instanceof Error ? err.message : '取得支付歷史失敗'
      error.value = error_msg
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 清除錯誤資訊
   */
  const clearError = () => {
    error.value = null
  }

  /**
   * 重置狀態
   */
  const reset = () => {
    services.value = []
    bills.value = []
    paymentHistory.value = []
    error.value = null
    currentPage.value = 1
    pageSize.value = 10
  }

  return {
    // State
    services,
    bills,
    paymentHistory,
    isLoading,
    error,
    currentPage,
    pageSize,
    totalPages,
    totalCount,

    // Computed
    billStats,

    // Actions
    fetchServices,
    fetchBills,
    payBill,
    fetchPaymentHistory,
    clearError,
    reset
  }
})
