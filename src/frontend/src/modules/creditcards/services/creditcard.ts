import apiClient from '@/shared/services/api'
import type {
  CreditCard,
  CreditCardTransaction,
  CreditCardBill,
  CardApplicationRequest,
  CardApplicationResponse,
  PaymentRequest,
  PaymentResponse
} from '../types'

export const creditCardService = {
  /**
   * 取得所有信用卡
   */
  getCards: () => 
    apiClient.get<CreditCard[]>('/creditcards'),
  
  /**
   * 取得單張信用卡詳情
   */
  getCardById: (cardId: number) => 
    apiClient.get<CreditCard>(`/creditcards/${cardId}`),
  
  /**
   * 申請信用卡
   */
  applyCard: (data: CardApplicationRequest) => 
    apiClient.post<CardApplicationResponse>('/creditcards/apply', data),
  
  /**
   * 取得信用卡消費記錄
   */
  getCardTransactions: (cardId: number, params?: { from?: string; to?: string }) => 
    apiClient.get<CreditCardTransaction[]>(`/creditcards/${cardId}/transactions`, { params }),
  
  /**
   * 取得信用卡帳單
   */
  getCardBills: (cardId: number) => 
    apiClient.get<CreditCardBill[]>(`/creditcards/${cardId}/bills`),
  
  /**
   * 繳費
   */
  payBill: (data: PaymentRequest) => 
    apiClient.post<PaymentResponse>('/creditcards/pay', data),
  
  /**
   * 鎖定/解鎖信用卡
   */
  toggleCardStatus: (cardId: number, action: 'lock' | 'unlock') => 
    apiClient.post(`/creditcards/${cardId}/${action}`),
}
