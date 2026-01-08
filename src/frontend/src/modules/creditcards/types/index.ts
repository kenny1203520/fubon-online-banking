export interface CreditCard {
  id: number
  card_number: string
  card_type: 'visa' | 'mastercard' | 'jcb' | 'amex'
  card_name: string
  credit_limit: number
  available_credit: number
  status: 'active' | 'inactive' | 'blocked' | 'pending'
  expiry_date: string
  created_at: string
}

export interface CreditCardTransaction {
  id: number
  card_id: number
  merchant_name: string
  amount: number
  currency: string
  transaction_date: string
  transaction_type: 'purchase' | 'refund' | 'fee'
  status: 'pending' | 'completed' | 'cancelled'
  description?: string
}

export interface CreditCardBill {
  id: number
  card_id: number
  billing_date: string
  due_date: string
  total_amount: number
  minimum_payment: number
  paid_amount: number
  status: 'unpaid' | 'partial' | 'paid' | 'overdue'
  created_at: string
}

export interface CardApplicationRequest {
  card_type: string
  annual_income: number
  employment_status: 'employed' | 'self-employed' | 'unemployed' | 'retired'
  company_name?: string
  position?: string
}

export interface CardApplicationResponse {
  application_id: number
  status: 'pending' | 'approved' | 'rejected'
  message: string
  estimated_processing_days?: number
}

export interface PaymentRequest {
  card_id: number
  bill_id: number
  amount: number
  payment_method: 'account' | 'atm' | 'online'
}

export interface PaymentResponse {
  transaction_id: number
  message: string
  remaining_balance: number
}

export interface CreditCardApplication {
  id: number
  user_id: string
  card_type: string
  annual_income: number
  employment_status: string
  company_name: string
  position: string
  status: string
  created_at: string
}

export interface CreditCardApplicationListResponse {
  items: CreditCardApplication[]
  page: number
  per_page: number
  total: number
  total_pages: number
}

export interface CreditCardState {
  cards: CreditCard[]
  currentCard: CreditCard | null
  transactions: CreditCardTransaction[]
  bills: CreditCardBill[]
  isLoading: boolean
  error: string | null
}
