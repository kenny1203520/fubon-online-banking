export interface DashboardSummary {
  total_assets: number
  total_liabilities: number
  net_worth: number
  accounts_count: number
  cards_count: number
  last_updated: string
}

export interface AccountSummary {
  id: number
  account_name: string
  account_type: string
  balance: number
  currency: string
}

export interface RecentTransaction {
  id: number
  type: 'deposit' | 'withdrawal' | 'transfer'
  amount: number
  description: string
  date: string
  account_name: string
}

export interface CreditCardSummary {
  id: number
  card_name: string
  card_number: string
  current_balance: number
  available_credit: number
  due_date?: string
  minimum_payment?: number
}

export interface InvestmentSummary {
  total_value: number
  total_cost: number
  total_gain: number
  gain_percentage: number
  holdings_count: number
}

export interface Notification {
  id: number
  type: 'info' | 'warning' | 'error' | 'success'
  title: string
  message: string
  read: boolean
  created_at: string
}

export interface QuickLink {
  id: string
  name: string
  icon: string
  path: string
  description?: string
}

export interface DashboardData {
  summary: DashboardSummary
  accounts: AccountSummary[]
  recent_transactions: RecentTransaction[]
  cards: CreditCardSummary[]
  investment: InvestmentSummary
  notifications: Notification[]
}

export interface DashboardState {
  dashboardData: DashboardData | null
  isLoading: boolean
  error: string | null
  lastRefreshed: Date | null
}
