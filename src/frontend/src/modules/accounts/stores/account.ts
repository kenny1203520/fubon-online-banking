import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { accountService } from '../services/account'
import type { Account, AccountCreate, Transaction, TransactionFilters } from '../types'

export const useAccountStore = defineStore('account', () => {
  // State
  const accounts = ref<Account[]>([])
  const currentAccount = ref<Account | null>(null)
  const transactions = ref<Transaction[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Pagination state
  const currentPage = ref(1)
  const perPage = ref(10)
  const totalAccounts = ref(0)
  const totalPages = ref(0)

  // Computed
  const hasAccounts = computed(() => accounts.value.length > 0)
  const activeAccounts = computed(() => accounts.value.filter((acc) => acc.status === 'active'))
  const totalBalance = computed(() =>
    activeAccounts.value.reduce((sum, acc) => sum + acc.balance, 0),
  )

  // Actions
  const fetchAccounts = async (page: number = 1, limit: number = 10) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await accountService.getAccounts(page, limit)
      accounts.value = response.data.items
      currentPage.value = response.data.page
      perPage.value = response.data.per_page
      totalAccounts.value = response.data.total
      totalPages.value = response.data.total_pages
    } catch (err: unknown) {
      const errorObj = err as { response?: { data?: { detail?: string } } }
      error.value = errorObj.response?.data?.detail || '取得帳戶列表失敗'
      throw new Error(error.value)
    } finally {
      isLoading.value = false
    }
  }

  const fetchAccountById = async (id: number) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await accountService.getAccountById(id)
      currentAccount.value = response.data
      return response.data
    } catch (err: unknown) {
      const errorObj = err as { response?: { data?: { detail?: string } } }
      error.value = errorObj.response?.data?.detail || '取得帳戶資訊失敗'
      throw new Error(error.value)
    } finally {
      isLoading.value = false
    }
  }

  const openAccount = async (data: AccountCreate) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await accountService.createAccount(data)
      // 開戶成功後重新取得帳戶列表
      await fetchAccounts(currentPage.value, perPage.value)
      return response.data
    } catch (err: unknown) {
      const errorObj = err as { response?: { data?: { detail?: string } } }
      error.value = errorObj.response?.data?.detail || '開戶申請失敗'
      throw new Error(error.value)
    } finally {
      isLoading.value = false
    }
  }

  const getBalance = async (accountId: number) => {
    try {
      const response = await accountService.getBalance(accountId)

      // 更新本地帳戶餘額
      const accountIndex = accounts.value.findIndex((acc) => acc.id === accountId)
      if (accountIndex !== -1 && accounts.value[accountIndex]) {
        accounts.value[accountIndex].balance = response.data.balance
        accounts.value[accountIndex].cashless_enabled = response.data.cashless_enabled
      }

      // 更新當前帳戶餘額
      if (currentAccount.value && currentAccount.value.id === accountId) {
        currentAccount.value.balance = response.data.balance
        currentAccount.value.cashless_enabled = response.data.cashless_enabled
      }

      return response.data
    } catch (err: unknown) {
      const errorObj = err as { response?: { data?: { detail?: string } } }
      error.value = errorObj.response?.data?.detail || '查詢餘額失敗'
      throw new Error(error.value)
    }
  }

  const setCashless = async (accountId: number, enabled: boolean) => {
    try {
      const response = await accountService.setCashless(accountId, enabled)

      // 更新本地帳戶狀態
      const accountIndex = accounts.value.findIndex((acc) => acc.id === accountId)
      if (accountIndex !== -1 && accounts.value[accountIndex]) {
        accounts.value[accountIndex].cashless_enabled = response.data.cashless_enabled
      }

      // 更新當前帳戶狀態
      if (currentAccount.value && currentAccount.value.id === accountId) {
        currentAccount.value.cashless_enabled = response.data.cashless_enabled
      }

      return response.data
    } catch (err: unknown) {
      const errorObj = err as { response?: { data?: { detail?: string } } }
      error.value = errorObj.response?.data?.detail || '設定無現金提款失敗'
      throw new Error(error.value)
    }
  }

  const fetchTransactions = async (accountId: number, filters?: TransactionFilters) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await accountService.getAccountTransactions(accountId, filters)
      transactions.value = response.data.items
      return response.data
    } catch (err: unknown) {
      const errorObj = err as { response?: { data?: { detail?: string } } }
      error.value = errorObj.response?.data?.detail || '取得交易紀錄失敗'
      throw new Error(error.value)
    } finally {
      isLoading.value = false
    }
  }

  const updateAccount = async (id: number, data: Partial<Account>) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await accountService.updateAccount(id, data)

      // 更新本地帳戶資料
      const accountIndex = accounts.value.findIndex((acc) => acc.id === id)
      if (accountIndex !== -1) {
        accounts.value[accountIndex] = { ...accounts.value[accountIndex], ...response.data }
      }

      // 更新當前帳戶資料
      if (currentAccount.value && currentAccount.value.id === id) {
        currentAccount.value = { ...currentAccount.value, ...response.data }
      }

      return response.data
    } catch (err: unknown) {
      const errorObj = err as { response?: { data?: { detail?: string } } }
      error.value = errorObj.response?.data?.detail || '更新帳戶失敗'
      throw new Error(error.value)
    } finally {
      isLoading.value = false
    }
  }

  const deleteAccount = async (id: number) => {
    isLoading.value = true
    error.value = null

    try {
      await accountService.deleteAccount(id)

      // 從列表中移除帳戶
      accounts.value = accounts.value.filter((acc) => acc.id !== id)

      // 清除當前帳戶（如果是被刪除的）
      if (currentAccount.value && currentAccount.value.id === id) {
        currentAccount.value = null
      }
    } catch (err: unknown) {
      const errorObj = err as { response?: { data?: { detail?: string } } }
      error.value = errorObj.response?.data?.detail || '刪除帳戶失敗'
      throw new Error(error.value)
    } finally {
      isLoading.value = false
    }
  }

  const clearError = () => {
    error.value = null
  }

  const clearCurrentAccount = () => {
    currentAccount.value = null
  }

  return {
    // State
    accounts,
    currentAccount,
    transactions,
    isLoading,
    error,
    currentPage,
    perPage,
    totalAccounts,
    totalPages,
    // Computed
    hasAccounts,
    activeAccounts,
    totalBalance,
    // Actions
    fetchAccounts,
    fetchAccountById,
    openAccount,
    getBalance,
    setCashless,
    fetchTransactions,
    updateAccount,
    deleteAccount,
    clearError,
    clearCurrentAccount,
  }
})
