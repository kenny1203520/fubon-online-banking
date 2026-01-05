export interface LoanProduct {
  id: number
  product_name: string
  loan_type: 'personal' | 'mortgage' | 'auto' | 'business'
  min_amount: number
  max_amount: number
  interest_rate: number
  max_term_months: number
  features: string[]
  requirements: string[]
}

export interface Loan {
  id: number
  product_id: number
  product_name: string
  loan_type: 'personal' | 'mortgage' | 'auto' | 'business'
  loan_amount: number
  interest_rate: number
  term_months: number
  monthly_payment: number
  remaining_balance: number
  next_payment_date: string
  next_payment_amount: number
  status: 'pending' | 'approved' | 'active' | 'paid_off' | 'defaulted'
  application_date: string
  approval_date?: string
  start_date?: string
}

export interface LoanApplication {
  product_id: number
  loan_amount: number
  term_months: number
  purpose: string
  employment_status: 'employed' | 'self-employed' | 'unemployed' | 'retired'
  annual_income: number
  company_name?: string
  years_employed?: number
  has_collateral: boolean
  collateral_description?: string
}

export interface RepaymentSchedule {
  payment_number: number
  payment_date: string
  principal: number
  interest: number
  total_payment: number
  remaining_balance: number
  status: 'pending' | 'paid' | 'overdue'
}

export interface RepaymentHistory {
  id: number
  loan_id: number
  payment_date: string
  amount: number
  principal: number
  interest: number
  remaining_balance: number
}

export interface RepaymentRequest {
  loan_id: number
  amount: number
  payment_method: 'account' | 'atm' | 'online'
}

export interface LoanCalculation {
  loan_amount: number
  interest_rate: number
  term_months: number
  monthly_payment: number
  total_payment: number
  total_interest: number
}

export interface EarlyRepaymentRequest {
  loan_id: number
  amount: number
}

export interface LoanState {
  loanProducts: LoanProduct[]
  myLoans: Loan[]
  currentLoan: Loan | null
  repaymentSchedule: RepaymentSchedule[]
  repaymentHistory: RepaymentHistory[]
  isLoading: boolean
  error: string | null
}
