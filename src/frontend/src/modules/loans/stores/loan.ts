import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { loanService } from '../services/loan'
import type {
  LoanProduct,
  Loan,
  LoanApplication,
  RepaymentSchedule,
  RepaymentHistory,
  RepaymentRequest,
  EarlyRepaymentRequest
} from '../types'

export const useLoanStore = defineStore('loan', () => {
  // State
  const loanProducts = ref<LoanProduct[]>([])
  const myLoans = ref<Loan[]>([])
  const currentLoan = ref<Loan | null>(null)
  const repaymentSchedule = ref<RepaymentSchedule[]>([])
  const repaymentHistory = ref<RepaymentHistory[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const hasLoans = computed(() => myLoans.value.length > 0)
  
  const activeLoans = computed(() => 
    myLoans.value.filter(loan => loan.status === 'active')
  )
  
  const totalRemainingBalance = computed(() => 
    activeLoans.value.reduce((sum, loan) => sum + loan.remaining_balance, 0)
  )
  
  const nextPaymentDue = computed(() => {
    const upcoming = activeLoans.value
      .filter(loan => loan.next_payment_date)
      .sort((a, b) => 
        new Date(a.next_payment_date).getTime() - new Date(b.next_payment_date).getTime()
      )
    return upcoming[0] || null
  })
  
  const overduePayments = computed(() => 
    repaymentSchedule.value.filter(payment => payment.status === 'overdue')
  )

  // Actions
  /**
   * 取得貸款產品列表
   */
  const fetchLoanProducts = async (params?: { type?: string }) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await loanService.getLoanProducts(params)
      loanProducts.value = response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : '取得貸款產品失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 貸款試算
   */
  const calculateLoan = async (amount: number, rate: number, months: number) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await loanService.calculateLoan(amount, rate, months)
      return response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : '貸款試算失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 申請貸款
   */
  const applyLoan = async (data: LoanApplication) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await loanService.applyLoan(data)
      // 重新取得我的貸款列表
      await fetchMyLoans()
      return response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : '申請貸款失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 取得我的貸款列表
   */
  const fetchMyLoans = async () => {
    isLoading.value = true
    error.value = null

    try {
      const response = await loanService.getMyLoans()
      myLoans.value = response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : '取得貸款列表失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 取得貸款詳情
   */
  const fetchLoanById = async (loanId: number) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await loanService.getLoanById(loanId)
      currentLoan.value = response.data
      return response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : '取得貸款詳情失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 取得還款計劃
   */
  const fetchRepaymentSchedule = async (loanId: number) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await loanService.getRepaymentSchedule(loanId)
      repaymentSchedule.value = response.data
      return response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : '取得還款計劃失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 取得還款記錄
   */
  const fetchRepaymentHistory = async (loanId: number) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await loanService.getRepaymentHistory(loanId)
      repaymentHistory.value = response.data
      return response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : '取得還款記錄失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 還款
   */
  const makeRepayment = async (data: RepaymentRequest) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await loanService.makeRepayment(data)
      // 重新取得貸款資訊
      await fetchMyLoans()
      await fetchRepaymentSchedule(data.loan_id)
      return response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : '還款失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 提前還款
   */
  const earlyRepayment = async (data: EarlyRepaymentRequest) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await loanService.earlyRepayment(data)
      // 重新取得貸款資訊
      await fetchMyLoans()
      return response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : '提前還款失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 清空錯誤訊息
   */
  const clearError = () => {
    error.value = null
  }

  /**
   * 重置狀態
   */
  const reset = () => {
    loanProducts.value = []
    myLoans.value = []
    currentLoan.value = null
    repaymentSchedule.value = []
    repaymentHistory.value = []
    error.value = null
  }

  return {
    // State
    loanProducts,
    myLoans,
    currentLoan,
    repaymentSchedule,
    repaymentHistory,
    isLoading,
    error,
    
    // Computed
    hasLoans,
    activeLoans,
    totalRemainingBalance,
    nextPaymentDue,
    overduePayments,
    
    // Actions
    fetchLoanProducts,
    calculateLoan,
    applyLoan,
    fetchMyLoans,
    fetchLoanById,
    fetchRepaymentSchedule,
    fetchRepaymentHistory,
    makeRepayment,
    earlyRepayment,
    clearError,
    reset
  }
})
