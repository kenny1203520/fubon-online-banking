import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { transactionService } from '../services/transaction'
import type {
  Transaction,
  TransactionQuery,
  TransferRequest,
  ExchangeRequest,
  ExchangeRate
} from '../types'

export const useTransactionStore = defineStore('transaction', () => {
  // State
  const transactions = ref<Transaction[]>([])
  const currentTransaction = ref<Transaction | null>(null)
  const exchangeRates = ref<ExchangeRate[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const pagination = ref({
    page: 1,
    per_page: 20,
    total: 0
  })

  // Computed
  const hasTransactions = computed(() => transactions.value.length > 0)
  
  const totalAmount = computed(() => {
    return transactions.value.reduce((sum, t) => {
      if (t.type === 'deposit') return sum + t.amount
      if (t.type === 'withdrawal') return sum - t.amount
      return sum
    }, 0)
  })

  const depositTotal = computed(() => {
    return transactions.value
      .filter(t => t.type === 'deposit')
      .reduce((sum, t) => sum + t.amount, 0)
  })

  const withdrawalTotal = computed(() => {
    return transactions.value
      .filter(t => t.type === 'withdrawal')
      .reduce((sum, t) => sum + t.amount, 0)
  })

  // Actions

  /**
   * 取得交易列表
   */
  const fetchTransactions = async (query?: TransactionQuery) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await transactionService.getTransactions(query)
      transactions.value = response.items
      
      if (response.total !== undefined) {
        pagination.value.total = response.total
      }
      if (response.page !== undefined) {
        pagination.value.page = response.page
      }
      if (response.per_page !== undefined) {
        pagination.value.per_page = response.per_page
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : '取得交易記錄失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 取得單一交易詳情
   */
  const fetchTransactionById = async (transactionId: number) => {
    isLoading.value = true
    error.value = null

    try {
      const transaction = await transactionService.getTransactionById(transactionId)
      currentTransaction.value = transaction
      return transaction
    } catch (err) {
      const message = err instanceof Error ? err.message : '取得交易詳情失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 轉帳
   */
  const transfer = async (data: TransferRequest) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await transactionService.transfer(data)
      
      // 刷新交易列表
      await fetchTransactions({
        account_id: data.from_account_id,
        page: pagination.value.page,
        per_page: pagination.value.per_page
      })
      
      return response
    } catch (err) {
      const message = err instanceof Error ? err.message : '轉帳失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 換匯
   */
  const exchange = async (data: ExchangeRequest) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await transactionService.exchange(data)
      
      // 如果有 account_id，刷新交易列表
      if (data.account_id) {
        await fetchTransactions({
          account_id: data.account_id,
          page: pagination.value.page,
          per_page: pagination.value.per_page
        })
      }
      
      return response
    } catch (err) {
      const message = err instanceof Error ? err.message : '換匯失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 取得匯率
   */
  const fetchExchangeRates = async (baseCurrency: string = 'TWD') => {
    isLoading.value = true
    error.value = null

    try {
      const response = await transactionService.getExchangeRates(baseCurrency)
      exchangeRates.value = response.rates
      return response
    } catch (err) {
      const message = err instanceof Error ? err.message : '取得匯率失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 取得特定帳戶的交易記錄
   */
  const fetchAccountTransactions = async (
    accountId: number,
    query?: Omit<TransactionQuery, 'account_id'>
  ) => {
    return fetchTransactions({ account_id: accountId, ...query })
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
    transactions.value = []
    currentTransaction.value = null
    exchangeRates.value = []
    error.value = null
    pagination.value = {
      page: 1,
      per_page: 20,
      total: 0
    }
  }

  return {
    // State
    transactions,
    currentTransaction,
    exchangeRates,
    isLoading,
    error,
    pagination,
    
    // Computed
    hasTransactions,
    totalAmount,
    depositTotal,
    withdrawalTotal,
    
    // Actions
    fetchTransactions,
    fetchTransactionById,
    transfer,
    exchange,
    fetchExchangeRates,
    fetchAccountTransactions,
    clearError,
    reset
  }
})
