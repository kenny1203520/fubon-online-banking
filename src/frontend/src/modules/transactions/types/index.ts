// Transaction Types

export interface Transaction {
  id: number
  account_id: number
  type: 'deposit' | 'withdrawal' | 'transfer'
  amount: number
  currency: string
  related_account?: number
  description?: string
  created_at: string
}

export interface TransactionResponse {
  id: number
  account_id: number
  type: 'deposit' | 'withdrawal' | 'transfer'
  amount: number
  currency: string
  related_account?: number
  description?: string
  created_at: string
}

export interface TransactionList {
  items: TransactionResponse[]
  total?: number
  page?: number
  per_page?: number
}

export interface TransactionQuery {
  account_id: number
  frm?: string  // from date (ISO 8601)
  to?: string   // to date (ISO 8601)
  type?: 'deposit' | 'withdrawal' | 'transfer'
  page?: number
  per_page?: number
}

// Transfer Types

export interface TransferRequest {
  from_account_id?: number
  to_account_number: string
  amount: number
  description?: string
  transfer_type: 'internal' | 'other' | 'scheduled'
}

export interface TransferResponse {
  transaction_id: number
  from_account_id: number
  to_account_id: number
  amount: number
  currency: string
  created_at: string
  message: string
}

// Exchange Types

export interface ExchangeRate {
  from_currency: string
  to_currency: string
  rate: number
  timestamp: string
}

export interface ExchangeRequest {
  from_currency: string
  to_currency: string
  amount: number
  account_id?: number
}

export interface ExchangeResponse {
  transaction_id: number
  from_currency: string
  to_currency: string
  from_amount: number
  to_amount: number
  rate: number
  account_id?: number
  created_at: string
  message: string
}

export interface ExchangeRateResponse {
  rates: ExchangeRate[]
  base_currency: string
  timestamp: string
}

// State Types

export interface TransactionState {
  transactions: Transaction[]
  currentTransaction: Transaction | null
  exchangeRates: ExchangeRate[]
  isLoading: boolean
  error: string | null
  pagination: {
    page: number
    per_page: number
    total: number
  }
}

// Filter Types

export interface TransactionFilters {
  account_id?: number
  type?: 'deposit' | 'withdrawal' | 'transfer'
  from_date?: string
  to_date?: string
  min_amount?: number
  max_amount?: number
  currency?: string
}
