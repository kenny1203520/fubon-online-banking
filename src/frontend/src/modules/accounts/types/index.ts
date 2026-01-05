// Account Types
export interface Account {
  id: number
  full_name: string
  id_number: string
  email?: string
  balance: number
  status: 'pending' | 'active' | 'inactive' | 'closed'
  cashless_enabled: boolean
  created_at: string
}

export interface AccountCreate {
  full_name: string
  id_number: string
  email?: string
  initial_deposit: number
}

export interface AccountResponse {
  id: number
  full_name: string
  id_number: string
  email?: string
  balance: number
  status: 'pending' | 'active' | 'inactive' | 'closed'
  cashless_enabled: boolean
  created_at: string
}

export interface AccountList {
  items: AccountResponse[]
  page: number
  per_page: number
  total: number
  total_pages: number
}

export interface BalanceRequest {
  account_id: number
}

export interface BalanceResponse {
  account_id: number
  balance: number
  cashless_enabled: boolean
}

export interface CashlessRequest {
  account_id: number
  enabled: boolean
}

export interface CashlessResponse {
  account_id: number
  cashless_enabled: boolean
}

export interface OpenAccountResponse {
  account_id: number
  status: string
  message: string
}

// Transaction Types (related to accounts)
export interface Transaction {
  id: number
  account_id: number
  type: 'deposit' | 'withdrawal' | 'transfer'
  amount: number
  description?: string
  created_at: string
}

export interface TransactionResponse {
  id: number
  account_id: number
  type: 'deposit' | 'withdrawal' | 'transfer'
  amount: number
  description?: string
  created_at: string
}

export interface TransactionList {
  items: TransactionResponse[]
  page: number
  per_page: number
  total: number
  total_pages: number
}

export interface TransactionFilters {
  page?: number
  per_page?: number
  type?: string
  start_date?: string
  end_date?: string
}

// Store State
export interface AccountState {
  accounts: Account[]
  currentAccount: Account | null
  transactions: Transaction[]
  isLoading: boolean
  error: string | null
}