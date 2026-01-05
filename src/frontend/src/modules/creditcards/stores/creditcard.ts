import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { creditCardService } from '../services/creditcard'
import type {
  CreditCard,
  CreditCardTransaction,
  CreditCardBill,
  CardApplicationRequest,
  PaymentRequest
} from '../types'

export const useCreditCardStore = defineStore('creditcard', () => {
  // State
  const cards = ref<CreditCard[]>([])
  const currentCard = ref<CreditCard | null>(null)
  const transactions = ref<CreditCardTransaction[]>([])
  const bills = ref<CreditCardBill[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const hasCards = computed(() => cards.value.length > 0)
  
  const activeCards = computed(() => 
    cards.value.filter(card => card.status === 'active')
  )
  
  const totalCreditLimit = computed(() => 
    cards.value.reduce((sum, card) => sum + card.credit_limit, 0)
  )
  
  const totalAvailableCredit = computed(() => 
    cards.value.reduce((sum, card) => sum + card.available_credit, 0)
  )
  
  const unpaidBills = computed(() => 
    bills.value.filter(bill => bill.status === 'unpaid' || bill.status === 'partial')
  )

  // Actions
  /**
   * 取得所有信用卡
   */
  const fetchCards = async () => {
    isLoading.value = true
    error.value = null

    try {
      const response = await creditCardService.getCards()
      cards.value = response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : '取得信用卡列表失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 取得單張信用卡詳情
   */
  const fetchCardById = async (cardId: number) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await creditCardService.getCardById(cardId)
      currentCard.value = response.data
      return response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : '取得信用卡詳情失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 申請信用卡
   */
  const applyCard = async (data: CardApplicationRequest) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await creditCardService.applyCard(data)
      return response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : '申請信用卡失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 取得信用卡消費記錄
   */
  const fetchCardTransactions = async (cardId: number, params?: { from?: string; to?: string }) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await creditCardService.getCardTransactions(cardId, params)
      transactions.value = response.data
      return response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : '取得消費記錄失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 取得信用卡帳單
   */
  const fetchCardBills = async (cardId: number) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await creditCardService.getCardBills(cardId)
      bills.value = response.data
      return response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : '取得帳單失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 繳費
   */
  const payBill = async (data: PaymentRequest) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await creditCardService.payBill(data)
      // 繳費後重新取得帳單列表
      await fetchCardBills(data.card_id)
      return response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : '繳費失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 鎖定/解鎖信用卡
   */
  const toggleCardStatus = async (cardId: number, action: 'lock' | 'unlock') => {
    isLoading.value = true
    error.value = null

    try {
      await creditCardService.toggleCardStatus(cardId, action)
      // 更新卡片狀態
      await fetchCards()
    } catch (err) {
      const message = err instanceof Error ? err.message : '操作失敗'
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
    cards.value = []
    currentCard.value = null
    transactions.value = []
    bills.value = []
    error.value = null
  }

  return {
    // State
    cards,
    currentCard,
    transactions,
    bills,
    isLoading,
    error,
    
    // Computed
    hasCards,
    activeCards,
    totalCreditLimit,
    totalAvailableCredit,
    unpaidBills,
    
    // Actions
    fetchCards,
    fetchCardById,
    applyCard,
    fetchCardTransactions,
    fetchCardBills,
    payBill,
    toggleCardStatus,
    clearError,
    reset
  }
})
