import apiClient from '@/shared/services/api'
import type {
  AccountCreate,
  AccountResponse,
  AccountList,
  BalanceResponse,
  CashlessResponse,
  AccountCreateResponse,
  TransactionList,
  TransactionFilters,
} from '../types'

export const accountService = {
  // 取得所有帳戶列表（分頁）
  getAccounts: (page: number = 1, perPage: number = 10) =>
    apiClient.get<AccountList>('/accounts', { params: { page, per_page: perPage } }),

  // 取得單一帳戶資訊
  getAccountById: (id: string) => apiClient.get<AccountResponse>(`/accounts/${id}`),

  // 開戶申請
  createAccount: (data: AccountCreate) => apiClient.post<AccountCreateResponse>('/accounts/open', data),

  // 查詢帳戶餘額
  getBalance: (accountId: string) =>
    apiClient.post<BalanceResponse>('/accounts/balance', { account_id: accountId }),

  // 設定無現金提款功能
  setCashless: (accountId: string, enabled: boolean) =>
    apiClient.post<CashlessResponse>('/accounts/cashless_withdraw', { account_id: accountId, enabled }),

  // 取得帳戶交易紀錄
  getAccountTransactions: (accountId: string, filters?: TransactionFilters) =>
    apiClient.post<TransactionList>('/accounts/transactions', {
      account_id: accountId,
      ...filters,
    }),

  // 更新帳戶資訊（如果後端有實作）
  updateAccount: (id: string, data: Partial<AccountResponse>) =>
    apiClient.put<AccountResponse>(`/accounts/${id}`, data),

  // 刪除/關閉帳戶（如果後端有實作）
  deleteAccount: (id: string) => apiClient.delete(`/accounts/${id}`),
}
