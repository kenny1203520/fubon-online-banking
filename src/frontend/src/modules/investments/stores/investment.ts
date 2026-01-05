import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { investmentService } from '../services/investment'
import type {
  Fund,
  Stock,
  Insurance,
  Holding,
  FundTransaction,
  PurchaseRequest,
  RedeemRequest,
  StockOrderRequest,
  InsuranceApplicationRequest,
  InvestmentSummary
} from '../types'

export const useInvestmentStore = defineStore('investment', () => {
  // State
  const funds = ref<Fund[]>([])
  const stocks = ref<Stock[]>([])
  const insurances = ref<Insurance[]>([])
  const holdings = ref<Holding[]>([])
  const transactions = ref<FundTransaction[]>([])
  const summary = ref<InvestmentSummary | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const hasFunds = computed(() => funds.value.length > 0)
  const hasStocks = computed(() => stocks.value.length > 0)
  const hasHoldings = computed(() => holdings.value.length > 0)
  
  const totalInvestment = computed(() => summary.value?.total_investment || 0)
  const totalMarketValue = computed(() => summary.value?.total_market_value || 0)
  const totalGain = computed(() => summary.value?.total_gain || 0)
  const totalGainPercentage = computed(() => summary.value?.total_gain_percentage || 0)
  
  const fundHoldings = computed(() => 
    holdings.value.filter(h => h.investment_type === 'fund')
  )
  
  const stockHoldings = computed(() => 
    holdings.value.filter(h => h.investment_type === 'stock')
  )

  // Actions
  /**
   * 取得基金列表
   */
  const fetchFunds = async (params?: { type?: string; risk_level?: number }) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await investmentService.getFunds(params)
      funds.value = response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : '取得基金列表失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 取得基金詳情
   */
  const fetchFundById = async (fundId: number) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await investmentService.getFundById(fundId)
      return response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : '取得基金詳情失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 申購基金
   */
  const purchaseFund = async (data: PurchaseRequest) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await investmentService.purchaseFund(data)
      // 重新取得持有部位
      await fetchHoldings()
      return response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : '申購基金失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 贖回基金
   */
  const redeemFund = async (data: RedeemRequest) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await investmentService.redeemFund(data)
      // 重新取得持有部位
      await fetchHoldings()
      return response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : '贖回基金失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 取得基金交易記錄
   */
  const fetchFundTransactions = async (params?: { from?: string; to?: string }) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await investmentService.getFundTransactions(params)
      transactions.value = response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : '取得交易記錄失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 取得股票列表
   */
  const fetchStocks = async (params?: { exchange?: string; keyword?: string }) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await investmentService.getStocks(params)
      stocks.value = response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : '取得股票列表失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 股票下單
   */
  const placeStockOrder = async (data: StockOrderRequest) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await investmentService.placeStockOrder(data)
      // 重新取得持有部位
      await fetchHoldings()
      return response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : '股票下單失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 取得保險商品列表
   */
  const fetchInsurances = async (params?: { type?: string }) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await investmentService.getInsurances(params)
      insurances.value = response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : '取得保險列表失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 申請保險
   */
  const applyInsurance = async (data: InsuranceApplicationRequest) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await investmentService.applyInsurance(data)
      return response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : '申請保險失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 取得所有持有投資商品
   */
  const fetchHoldings = async () => {
    isLoading.value = true
    error.value = null

    try {
      const response = await investmentService.getHoldings()
      holdings.value = response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : '取得持有部位失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 取得投資摘要
   */
  const fetchInvestmentSummary = async () => {
    isLoading.value = true
    error.value = null

    try {
      const response = await investmentService.getInvestmentSummary()
      summary.value = response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : '取得投資摘要失敗'
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
    funds.value = []
    stocks.value = []
    insurances.value = []
    holdings.value = []
    transactions.value = []
    summary.value = null
    error.value = null
  }

  return {
    // State
    funds,
    stocks,
    insurances,
    holdings,
    transactions,
    summary,
    isLoading,
    error,
    
    // Computed
    hasFunds,
    hasStocks,
    hasHoldings,
    totalInvestment,
    totalMarketValue,
    totalGain,
    totalGainPercentage,
    fundHoldings,
    stockHoldings,
    
    // Actions
    fetchFunds,
    fetchFundById,
    purchaseFund,
    redeemFund,
    fetchFundTransactions,
    fetchStocks,
    placeStockOrder,
    fetchInsurances,
    applyInsurance,
    fetchHoldings,
    fetchInvestmentSummary,
    clearError,
    reset
  }
})
