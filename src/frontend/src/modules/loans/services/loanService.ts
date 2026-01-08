import apiClient from '@/shared/services/api'
import type {
    Loan,
    LoanCalculateRequest,
    LoanCalculation,
    LoanApplyRequest,
    LoanApplyResponse,
    RepaymentSchedule,
    RepaymentHistory,
    RepaymentRequest,
    RepaymentResponse
} from '../types'

export const loanService = {
    // 貸款試算
    async calculateLoan(data: LoanCalculateRequest): Promise<LoanCalculation> {
        const response = await apiClient.post<LoanCalculation>('/loans/calculate', data)
        return response.data
    },

    // 申請貸款
    async applyLoan(data: LoanApplyRequest): Promise<LoanApplyResponse> {
        const response = await apiClient.post<LoanApplyResponse>('/loans/apply', data)
        return response.data
    },

    // 獲取我的貸款列表
    async getMyLoans(): Promise<Loan[]> {
        const response = await apiClient.get<{ items: Loan[], total: number }>('/loans/')
        return response.data.items
    },

    // 獲取貸款詳情
    async getLoanDetail(loanId: number): Promise<Loan> {
        const response = await apiClient.get<Loan>(`/loans/${loanId}`)
        return response.data
    },

    // 獲取還款計劃
    async getRepaymentSchedule(loanId: number): Promise<RepaymentSchedule[]> {
        const response = await apiClient.get<RepaymentSchedule[]>(`/loans/${loanId}/schedule`)
        return response.data
    },

    // 獲取還款記錄
    async getRepaymentHistory(loanId: number): Promise<RepaymentHistory[]> {
        const response = await apiClient.get<RepaymentHistory[]>(`/loans/${loanId}/history`)
        return response.data
    },

    // 進行還款
    async makeRepayment(loanId: number, data: RepaymentRequest): Promise<RepaymentResponse> {
        const response = await apiClient.post<RepaymentResponse>('/loans/repay', {
            ...data,
            loan_id: loanId
        })
        return response.data
    }
}
