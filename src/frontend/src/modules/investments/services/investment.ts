import apiClient from '@/shared/services/api'
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

export const investmentService = {
  // 基金相關
  /**
   * 取得基金列表
   */
  getFunds: (params?: { type?: string; risk_level?: number }) =>
    apiClient.get<Fund[]>('/investments/funds', { params }),

  /**
   * 取得基金詳情
   */
  getFundById: (fundId: number) =>
    apiClient.get<Fund>(`/investments/funds/${fundId}`),

  /**
   * 申購基金
   */
  purchaseFund: (data: PurchaseRequest) =>
    apiClient.post<FundTransaction>('/investments/funds/purchase', data),

  /**
   * 贖回基金
   */
  redeemFund: (data: RedeemRequest) =>
    apiClient.post<FundTransaction>('/investments/funds/redeem', data),

  /**
   * 取得基金交易記錄
   */
  getFundTransactions: (params?: { from?: string; to?: string }) =>
    apiClient.get<FundTransaction[]>('/investments/funds/transactions', { params }),

  // 股票相關
  /**
   * 取得股票列表
   */
  getStocks: (params?: { exchange?: string; keyword?: string }) =>
    apiClient.get<Stock[]>('/investments/stocks', { params }),

  /**
   * 取得股票詳情
   */
  getStockById: (stockId: number) =>
    apiClient.get<Stock>(`/investments/stocks/${stockId}`),

  /**
   * 股票下單
   */
  placeStockOrder: (data: StockOrderRequest) =>
    apiClient.post('/investments/stocks/order', data),

  // 保險相關
  /**
   * 取得保險商品列表
   */
  getInsurances: (params?: { type?: string }) =>
    apiClient.get<Insurance[]>('/investments/insurance', { params }),

  /**
   * 取得保險商品詳情
   */
  getInsuranceById: (insuranceId: number) =>
    apiClient.get<Insurance>(`/investments/insurance/${insuranceId}`),

  /**
   * 申請保險
   */
  applyInsurance: (data: InsuranceApplicationRequest) =>
    apiClient.post('/investments/insurance/apply', data),

  // 持有部位
  /**
   * 取得所有持有投資商品
   */
  getHoldings: () =>
    apiClient.get<Holding[]>('/investments/holdings'),

  /**
   * 取得投資摘要
   */
  getInvestmentSummary: () =>
    apiClient.get<InvestmentSummary>('/investments/summary'),

  // 通用產品與交易（後端新增）
  /**
   * 取得所有投資產品
   */
  getProducts: () => apiClient.get('/investments/products'),

  /**
   * 查詢投資紀錄
   */
  queryInvestments: (params?: { account_id?: number }) =>
    apiClient.post('/investments/query', params || {}),

  /**
   * 購買投資產品
   */
  purchaseProduct: (data: { account_id: number; product_id: number | string; amount: number }) =>
    apiClient.post('/investments/purchase', data),
}
