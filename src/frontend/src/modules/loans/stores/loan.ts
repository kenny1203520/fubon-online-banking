import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { loanService } from '../services/loanService'
import type {
  LoanProduct,
  Loan,
  LoanApplication,
  LoanApplyRequest,
  LoanApplyResponse,
  RepaymentSchedule,
  RepaymentHistory,
  RepaymentRequest,
  RepaymentResponse,
  EarlyRepaymentRequest,
  LoanCalculation
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
        new Date(a.next_payment_date!).getTime() - new Date(b.next_payment_date!).getTime()
      )
    return upcoming[0] || null
  })

  const overduePayments = computed(() =>
    repaymentSchedule.value.filter(payment => payment.status === 'overdue')
  )

  // Actions
  /**
   * 貸款試算
   */
  const calculateLoan = async (amount: number, rate: number, months: number): Promise<LoanCalculation> => {
    isLoading.value = true
    error.value = null

    try {
      const result = await loanService.calculateLoan({
        amount: amount,
        interest_rate: rate,
        term_months: months
      })
      return result
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
  const applyLoan = async (data: LoanApplyRequest): Promise<LoanApplyResponse> => {
    isLoading.value = true
    error.value = null

    try {
      const result = await loanService.applyLoan(data)
      // 嘗試重新取得我的貸款列表，但不影響申請結果
      try {
        await fetchMyLoans()
      } catch (fetchError) {
        console.warn('無法刷新貸款列表:', fetchError)
        // 忽略此錯誤，因為申請已經成功
      }
      return result
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
      myLoans.value = await loanService.getMyLoans()
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
      currentLoan.value = await loanService.getLoanDetail(loanId)
      return currentLoan.value
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
  const fetchRepaymentSchedule = async (loanId: number): Promise<RepaymentSchedule[]> => {
    isLoading.value = true
    error.value = null

    try {
      repaymentSchedule.value = await loanService.getRepaymentSchedule(loanId)
      return repaymentSchedule.value
    } catch (err) {
      const message = err instanceof Error ? err.message : '取得還款計劃失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 取得還款記錄（簡化版本，不使用 isLoading）
   */
  const getRepaymentSchedule = async (loanId: number): Promise<RepaymentSchedule[]> => {
    try {
      return await loanService.getRepaymentSchedule(loanId)
    } catch (err) {
      const message = err instanceof Error ? err.message : '取得還款計劃失敗'
      error.value = message
      throw new Error(message)
    }
  }

  /**
   * 取得還款記錄
   */
  const fetchRepaymentHistory = async (loanId: number): Promise<RepaymentHistory[]> => {
    isLoading.value = true
    error.value = null

    try {
      repaymentHistory.value = await loanService.getRepaymentHistory(loanId)
      return repaymentHistory.value
    } catch (err) {
      const message = err instanceof Error ? err.message : '取得還款記錄失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 取得還款記錄（簡化版本，不使用 isLoading）
   */
  const getRepaymentHistory = async (loanId: number): Promise<RepaymentHistory[]> => {
    try {
      return await loanService.getRepaymentHistory(loanId)
    } catch (err) {
      const message = err instanceof Error ? err.message : '取得還款記錄失敗'
      error.value = message
      throw new Error(message)
    }
  }

  /**
   * 還款
   */
  const makeRepayment = async (data: RepaymentRequest) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await loanService.makeRepayment(data.loan_id, data)
      // 重新取得貸款資訊
      await fetchMyLoans()
      await fetchRepaymentSchedule(data.loan_id)
      return response
    } catch (err) {
      const message = err instanceof Error ? err.message : '還款失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 清空錯誤資訊
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
    getRepaymentSchedule,
    getRepaymentHistory,
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
    calculateLoan,
    applyLoan,
    fetchMyLoans,
    fetchLoanById,
    fetchRepaymentSchedule,
    fetchRepaymentHistory,
    makeRepayment,
    clearError,
    reset
  }
})
