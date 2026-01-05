import apiClient from '../../../shared/services/api'
import type {
  TransactionList,
  TransactionQuery,
  TransactionResponse,
  TransferRequest,
  TransferResponse,
  ExchangeRequest,
  ExchangeResponse,
  ExchangeRateResponse
} from '../types'

export const transactionService = {
  // 取得交易列表
  getTransactions: async (query?: TransactionQuery): Promise<TransactionList> => {
    const response = await apiClient.get<TransactionList>('/transactions', { params: query })
    return response.data
  },

  // 取得單一交易詳情
  getTransactionById: async (transactionId: number): Promise<TransactionResponse> => {
    const response = await apiClient.get<TransactionResponse>(`/transactions/${transactionId}`)
    return response.data
  },

  // 轉帳
  transfer: async (data: TransferRequest): Promise<TransferResponse> => {
    const response = await apiClient.post<TransferResponse>('/transactions/transfer', data)
    return response.data
  },

  // 換匯
  exchange: async (data: ExchangeRequest): Promise<ExchangeResponse> => {
    const response = await apiClient.post<ExchangeResponse>('/transactions/exchange', data)
    return response.data
  },

  // 取得匯率
  getExchangeRates: async (baseCurrency: string = 'TWD'): Promise<ExchangeRateResponse> => {
    const response = await apiClient.get<ExchangeRateResponse>('/transactions/exchange/rates', {
      params: { base: baseCurrency }
    })
    return response.data
  },

  // 查詢帳戶交易記錄
  getAccountTransactions: async (
    accountId: number,
    query?: Omit<TransactionQuery, 'account_id'>
  ): Promise<TransactionList> => {
    const response = await apiClient.get<TransactionList>('/transactions', {
      params: { account_id: accountId, ...query }
    })
    return response.data
  },
}
