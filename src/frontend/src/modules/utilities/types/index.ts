/**
 * 繳費服務類型定義
 */

// 服務類型
export interface UtilityService {
  service_type: string
  providers: string[]
  description: string
}

// 繳費帳單
export interface UtilityBill {
  id: number
  bill_type: string
  provider: string
  amount: number
  due_date: string
  status: 'pending' | 'paid' | 'overdue'
  description?: string
  created_at: string
  paid_at?: string
}

// 繳費帳單列表響應
export interface UtilityBillListResponse {
  items: UtilityBill[]
  page: number
  per_page: number
  total: number
  total_pages: number
}

// 支付請求
export interface PayBillRequest {
  bill_id: number
  account_id: number
  amount: number
  payment_method?: 'bank_transfer' | 'credit_card'
}

// 支付響應
export interface PayBillResponse {
  transaction_id: number
  bill_id: number
  amount: number
  reference_number: string
  status: string
  created_at: string
}

// 繳費記錄
export interface PaymentRecord {
  id: number
  bill_id: number
  amount: number
  payment_method: string
  reference_number: string
  created_at: string
}

// 繳費記錄列表響應
export interface PaymentHistoryResponse {
  items: PaymentRecord[]
  page: number
  per_page: number
  total: number
  total_pages: number
}

// 繳費狀態
export interface UtilityState {
  services: UtilityService[]
  bills: UtilityBill[]
  paymentHistory: PaymentRecord[]
  isLoading: boolean
  error: string | null
  currentPage: number
  pageSize: number
  totalPages: number
  totalCount: number
}

// 過濾選項
export interface BillFilterOptions {
  bill_id?: number
  status?: 'pending' | 'paid' | 'overdue'
  bill_type?: string
  page?: number
  per_page?: number
}
