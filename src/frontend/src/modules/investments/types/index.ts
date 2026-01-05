export interface Fund {
  id: number
  fund_code: string
  fund_name: string
  fund_type: 'equity' | 'bond' | 'balanced' | 'money_market'
  currency: string
  nav: number // 淨值
  nav_date: string
  return_1m: number
  return_3m: number
  return_6m: number
  return_1y: number
  risk_level: 1 | 2 | 3 | 4 | 5
  minimum_investment: number
  management_fee: number
}

export interface Stock {
  id: number
  symbol: string
  name: string
  exchange: 'TWSE' | 'OTC'
  current_price: number
  change: number
  change_percentage: number
  volume: number
  market_cap: number
  pe_ratio?: number
  dividend_yield?: number
}

export interface Insurance {
  id: number
  product_code: string
  product_name: string
  insurance_type: 'life' | 'health' | 'accident' | 'investment'
  premium: number
  payment_period: string
  coverage_amount: number
  features: string[]
}

export interface Holding {
  id: number
  investment_type: 'fund' | 'stock' | 'insurance'
  product_id: number
  product_name: string
  quantity: number
  purchase_price: number
  current_price: number
  market_value: number
  unrealized_gain: number
  unrealized_gain_percentage: number
  purchase_date: string
}

export interface FundTransaction {
  id: number
  fund_id: number
  fund_name: string
  transaction_type: 'purchase' | 'redeem' | 'switch'
  amount: number
  units: number
  nav: number
  fee: number
  transaction_date: string
  status: 'pending' | 'completed' | 'cancelled'
}

export interface PurchaseRequest {
  fund_id: number
  amount: number
  account_id: number
}

export interface RedeemRequest {
  holding_id: number
  units: number
  account_id: number
}

export interface StockOrderRequest {
  stock_id: number
  order_type: 'buy' | 'sell'
  quantity: number
  price?: number // 限價，不填為市價
  account_id: number
}

export interface InsuranceApplicationRequest {
  insurance_id: number
  insured_name: string
  insured_id_number: string
  insured_birthday: string
  beneficiary_name: string
  beneficiary_relationship: string
  payment_method: 'monthly' | 'quarterly' | 'annually' | 'single'
}

export interface InvestmentSummary {
  total_investment: number
  total_market_value: number
  total_gain: number
  total_gain_percentage: number
  holdings_by_type: {
    fund: number
    stock: number
    insurance: number
  }
}

export interface InvestmentState {
  funds: Fund[]
  stocks: Stock[]
  insurances: Insurance[]
  holdings: Holding[]
  transactions: FundTransaction[]
  summary: InvestmentSummary | null
  isLoading: boolean
  error: string | null
}
