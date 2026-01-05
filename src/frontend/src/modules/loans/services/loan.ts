import apiClient from '@/shared/services/api'
import type {
  LoanProduct,
  Loan,
  LoanApplication,
  RepaymentSchedule,
  RepaymentHistory,
  RepaymentRequest,
  LoanCalculation,
  EarlyRepaymentRequest
} from '../types'

export const loanService = {
  /**
   * 取得貸款產品列表
   */
  getLoanProducts: (params?: { type?: string }) => 
    apiClient.get<LoanProduct[]>('/loans/products', { params }),
  
  /**
   * 取得貸款產品詳情
   */
  getLoanProductById: (productId: number) => 
    apiClient.get<LoanProduct>(`/loans/products/${productId}`),
  
  /**
   * 貸款試算
   */
  calculateLoan: (amount: number, rate: number, months: number) => 
    apiClient.post<LoanCalculation>('/loans/calculate', {
      amount,
      interest_rate: rate,
      term_months: months
    }),
  
  /**
   * 申請貸款
   */
  applyLoan: (data: LoanApplication) => 
    apiClient.post<{ application_id: number; message: string }>('/loans/apply', data),
  
  /**
   * 取得我的貸款列表
   */
  getMyLoans: () => 
    apiClient.get<Loan[]>('/loans'),
  
  /**
   * 取得貸款詳情
   */
  getLoanById: (loanId: number) => 
    apiClient.get<Loan>(`/loans/${loanId}`),
  
  /**
   * 取得還款計劃
   */
  getRepaymentSchedule: (loanId: number) => 
    apiClient.get<RepaymentSchedule[]>(`/loans/${loanId}/schedule`),
  
  /**
   * 取得還款記錄
   */
  getRepaymentHistory: (loanId: number) => 
    apiClient.get<RepaymentHistory[]>(`/loans/${loanId}/history`),
  
  /**
   * 還款
   */
  makeRepayment: (data: RepaymentRequest) => 
    apiClient.post('/loans/repay', data),
  
  /**
   * 提前還款
   */
  earlyRepayment: (data: EarlyRepaymentRequest) => 
    apiClient.post('/loans/early-repay', data),
}
