// Account Types
export interface Account {
  id: string
  account_number: string
  account_name: string
  full_name: string
  id_number: string
  email?: string
  phone: string
  address: string
  account_type: 'savings' | 'checking' | 'fixed_deposit' | 'foreign_currency' | 'investment'
  balance: number
  status: 'pending' | 'active' | 'inactive' | 'closed'
  cashless_enabled: boolean
  created_at: string
}

export interface AccountCreate {
  full_name: string
  id_number: string
  email?: string
  phone: string
  address: string
  account_type: 'savings' | 'checking' | 'fixed_deposit' | 'foreign_currency' | 'investment'
  initial_deposit: number
}

export interface AccountResponse {
  id: string
  account_number: string
  account_name: string
  full_name: string
  id_number: string
  email?: string
  phone: string
  address: string
  account_type: string
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
  account_id: string
}

export interface BalanceResponse {
  account_id: string
  balance: number
  cashless_enabled: boolean
}

export interface CashlessRequest {
  account_id: string
  enabled: boolean
}

export interface CashlessResponse {
  account_id: string
  cashless_enabled: boolean
}

export interface AccountCreateResponse {
  account_id: string
  account_number: string
  account_name: string
  status: string
  message: string
}

// Transaction Types (related to accounts)
export interface Transaction {
  id: number
  account_id: string
  type: 'deposit' | 'withdrawal' | 'transfer'
  amount: number
  description?: string
  created_at: string
}

export interface TransactionResponse {
  id: number
  account_id: string
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
  frm?: string
  to?: string
}

// Store State
export interface AccountState {
  accounts: Account[]
  currentAccount: Account | null
  transactions: Transaction[]
  isLoading: boolean
  error: string | null
}
