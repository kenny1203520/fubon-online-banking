<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useTransactionStore } from '../stores/transaction'
import type { ExchangeRequest } from '../types'

const transactionStore = useTransactionStore()

// Form data
const form = ref<ExchangeRequest>({
  from_currency: 'TWD',
  to_currency: 'USD',
  amount: 0,
  account_id: undefined
})

// UI state
const isSubmitting = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const showResult = ref(false)
const exchangeResult = ref({
  from_amount: 0,
  to_amount: 0,
  rate: 0,
  from_currency: '',
  to_currency: ''
})

// Currency options
const currencies = [
  { code: 'TWD', name: '新台幣', symbol: 'NT$' },
  { code: 'USD', name: '美元', symbol: '$' },
  { code: 'EUR', name: '歐元', symbol: '€' },
  { code: 'JPY', name: '日圓', symbol: '¥' },
  { code: 'GBP', name: '英鎊', symbol: '£' },
  { code: 'CNY', name: '人民幣', symbol: '¥' },
  { code: 'HKD', name: '港幣', symbol: 'HK$' },
  { code: 'AUD', name: '澳幣', symbol: 'A$' },
  { code: 'SGD', name: '新加坡幣', symbol: 'S$' },
  { code: 'KRW', name: '韓元', symbol: '₩' }
]

// Computed
const selectedFromCurrency = computed(() => 
  currencies.find(c => c.code === form.value.from_currency)
)

const selectedToCurrency = computed(() => 
  currencies.find(c => c.code === form.value.to_currency)
)

const currentRate = computed(() => {
  const rate = transactionStore.exchangeRates.find(
    r => r.from_currency === form.value.from_currency && 
         r.to_currency === form.value.to_currency
  )
  return rate?.rate || 0
})

const estimatedAmount = computed(() => {
  if (!form.value.amount || !currentRate.value) return 0
  return form.value.amount * currentRate.value
})

const isFormValid = computed(() => {
  return form.value.amount > 0 && 
         form.value.from_currency !== form.value.to_currency &&
         currentRate.value > 0
})

// Methods
const fetchRates = async () => {
  try {
    await transactionStore.fetchExchangeRates(form.value.from_currency)
  } catch (error) {
    console.error('Failed to fetch exchange rates:', error)
  }
}

const swapCurrencies = () => {
  const temp = form.value.from_currency
  form.value.from_currency = form.value.to_currency
  form.value.to_currency = temp
  fetchRates()
}

const handleSubmit = async () => {
  if (!isFormValid.value) return

  isSubmitting.value = true
  errorMessage.value = ''
  successMessage.value = ''
  showResult.value = false

  try {
    const result = await transactionStore.exchange(form.value)
    
    exchangeResult.value = {
      from_amount: result.from_amount,
      to_amount: result.to_amount,
      rate: result.rate,
      from_currency: result.from_currency,
      to_currency: result.to_currency
    }
    
    showResult.value = true
    successMessage.value = '換匯成功！'
    
    // Reset form
    form.value.amount = 0
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '換匯失敗'
  } finally {
    isSubmitting.value = false
  }
}

const formatCurrency = (amount: number, currencyCode: string) => {
  const currency = currencies.find(c => c.code === currencyCode)
  const formatted = new Intl.NumberFormat('zh-TW', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount)
  
  return currency ? `${currency.symbol} ${formatted}` : `${currencyCode} ${formatted}`
}

const validateAmount = () => {
  if (form.value.amount < 0) {
    form.value.amount = 0
  }
  if (form.value.amount > 10000000) {
    form.value.amount = 10000000
  }
}

onMounted(() => {
  fetchRates()
})
</script>

<template>
  <div class="page-wrapper">
    <div class="page-header">
      <h1>換匯</h1>
      <p>進行貨幣兌換</p>
    </div>

    <!-- Alert Messages -->
    <div v-if="errorMessage" class="alert alert-error">
      {{ errorMessage }}
      <button @click="errorMessage = ''" class="alert-close">&times;</button>
    </div>

    <div v-if="successMessage" class="alert alert-success">
      {{ successMessage }}
      <button @click="successMessage = ''" class="alert-close">&times;</button>
    </div>

    <div class="page-content">
      <div class="exchange-container">
        <!-- Exchange Form -->
        <div class="exchange-form">
          <h2>貨幣兌換</h2>

          <form @submit.prevent="handleSubmit">
            <!-- From Currency -->
            <div class="currency-section">
              <div class="form-group">
                <label>兌換貨幣</label>
                <select 
                  v-model="form.from_currency" 
                  @change="fetchRates"
                  class="form-control"
                  :disabled="isSubmitting"
                >
                  <option v-for="currency in currencies" :key="currency.code" :value="currency.code">
                    {{ currency.code }} - {{ currency.name }}
                  </option>
                </select>
              </div>

              <div class="form-group">
                <label>金額</label>
                <div class="input-with-symbol">
                  <span class="currency-symbol">{{ selectedFromCurrency?.symbol }}</span>
                  <input 
                    v-model.number="form.amount"
                    @input="validateAmount"
                    type="number"
                    step="0.01"
                    min="0"
                    max="10000000"
                    class="form-control"
                    placeholder="請輸入金額"
                    :disabled="isSubmitting"
                    required
                  />
                </div>
              </div>
            </div>

            <!-- Swap Button -->
            <div class="swap-section">
              <button 
                type="button"
                @click="swapCurrencies"
                class="btn-swap"
                :disabled="isSubmitting"
                title="交換貨幣"
              >
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M7 16V4M7 4L3 8M7 4L11 8M17 8V20M17 20L21 16M17 20L13 16"/>
                </svg>
              </button>
            </div>

            <!-- To Currency -->
            <div class="currency-section">
              <div class="form-group">
                <label>兌換為</label>
                <select 
                  v-model="form.to_currency" 
                  @change="fetchRates"
                  class="form-control"
                  :disabled="isSubmitting"
                >
                  <option v-for="currency in currencies" :key="currency.code" :value="currency.code">
                    {{ currency.code }} - {{ currency.name }}
                  </option>
                </select>
              </div>

              <div class="form-group">
                <label>預估金額</label>
                <div class="estimated-amount">
                  <span class="currency-symbol">{{ selectedToCurrency?.symbol }}</span>
                  <span class="amount">{{ estimatedAmount.toFixed(2) }}</span>
                </div>
              </div>
            </div>

            <!-- Exchange Rate Info -->
            <div v-if="currentRate > 0" class="rate-info">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <path d="M12 16v-4M12 8h.01"/>
              </svg>
              <span>
                當前匯率：1 {{ form.from_currency }} = {{ currentRate.toFixed(4) }} {{ form.to_currency }}
              </span>
            </div>

            <!-- Submit Button -->
            <button 
              type="submit" 
              class="btn btn-primary btn-block"
              :disabled="!isFormValid || isSubmitting"
            >
              <span v-if="isSubmitting">處理中...</span>
              <span v-else>確認換匯</span>
            </button>
          </form>
        </div>

        <!-- Exchange Result -->
        <div v-if="showResult" class="exchange-result">
          <h3>換匯結果</h3>
          <div class="result-card">
            <div class="result-row">
              <span class="result-label">兌換金額</span>
              <span class="result-value">
                {{ formatCurrency(exchangeResult.from_amount, exchangeResult.from_currency) }}
              </span>
            </div>
            <div class="result-arrow">→</div>
            <div class="result-row">
              <span class="result-label">獲得金額</span>
              <span class="result-value result-highlight">
                {{ formatCurrency(exchangeResult.to_amount, exchangeResult.to_currency) }}
              </span>
            </div>
            <div class="result-divider"></div>
            <div class="result-row">
              <span class="result-label">使用匯率</span>
              <span class="result-value">{{ exchangeResult.rate.toFixed(4) }}</span>
            </div>
          </div>
        </div>

        <!-- Exchange Rates Table -->
        <div v-if="transactionStore.exchangeRates.length > 0" class="rates-table">
          <h3>即時匯率</h3>
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>貨幣對</th>
                  <th>匯率</th>
                  <th>更新時間</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="rate in transactionStore.exchangeRates" :key="`${rate.from_currency}-${rate.to_currency}`">
                  <td>{{ rate.from_currency }} / {{ rate.to_currency }}</td>
                  <td class="rate-value">{{ rate.rate.toFixed(4) }}</td>
                  <td class="rate-time">{{ new Date(rate.timestamp).toLocaleString('zh-TW') }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-wrapper {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  margin: 0;
  font-size: 28px;
  color: #333;
  font-weight: 600;
}

.page-header p {
  margin: 8px 0 0 0;
  color: #666;
  font-size: 14px;
}

/* Alert */
.alert {
  padding: 12px 16px;
  border-radius: 6px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.alert-error {
  background-color: #fee;
  color: #c33;
  border: 1px solid #fcc;
}

.alert-success {
  background-color: #efe;
  color: #3c3;
  border: 1px solid #cfc;
}

.alert-close {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: inherit;
  padding: 0;
  width: 24px;
  height: 24px;
}

.page-content {
  background: white;
  padding: 24px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.exchange-container {
  display: grid;
  gap: 30px;
}

/* Exchange Form */
.exchange-form {
  background: #f8f9fa;
  padding: 24px;
  border-radius: 8px;
}

.exchange-form h2 {
  margin: 0 0 24px 0;
  font-size: 20px;
  color: #333;
  font-weight: 600;
}

.currency-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 16px;
  border: 1px solid #e0e0e0;
}

.form-group {
  margin-bottom: 16px;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-group label {
  display: block;
  font-size: 14px;
  color: #555;
  margin-bottom: 8px;
  font-weight: 500;
}

.form-control {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-control:focus {
  outline: none;
  border-color: #0066cc;
}

.form-control:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.input-with-symbol {
  display: flex;
  align-items: center;
  gap: 8px;
}

.currency-symbol {
  font-size: 16px;
  font-weight: 600;
  color: #666;
  min-width: 40px;
}

.estimated-amount {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #e3f2fd;
  border-radius: 6px;
  font-size: 18px;
  font-weight: 600;
  color: #1565c0;
}

.estimated-amount .amount {
  flex: 1;
}

/* Swap Button */
.swap-section {
  display: flex;
  justify-content: center;
  margin: 16px 0;
}

.btn-swap {
  width: 48px;
  height: 48px;
  border: 2px solid #0066cc;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  color: #0066cc;
}

.btn-swap:hover:not(:disabled) {
  background: #0066cc;
  color: white;
  transform: rotate(180deg);
}

.btn-swap:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Rate Info */
.rate-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #fff3cd;
  border-radius: 6px;
  font-size: 14px;
  color: #856404;
  margin-bottom: 20px;
}

/* Buttons */
.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background-color: #0066cc;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #0052a3;
}

.btn-block {
  width: 100%;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Exchange Result */
.exchange-result {
  background: #f8f9fa;
  padding: 24px;
  border-radius: 8px;
}

.exchange-result h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  color: #333;
  font-weight: 600;
}

.result-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.result-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
}

.result-label {
  font-size: 14px;
  color: #666;
}

.result-value {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.result-highlight {
  color: #4caf50;
  font-size: 18px;
}

.result-arrow {
  text-align: center;
  font-size: 24px;
  color: #0066cc;
  margin: 8px 0;
}

.result-divider {
  height: 1px;
  background: #e0e0e0;
  margin: 12px 0;
}

/* Rates Table */
.rates-table {
  background: #f8f9fa;
  padding: 24px;
  border-radius: 8px;
}

.rates-table h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  color: #333;
  font-weight: 600;
}

.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

thead {
  background-color: #e3f2fd;
}

th {
  padding: 12px;
  text-align: left;
  font-weight: 600;
  font-size: 14px;
  color: #1565c0;
}

td {
  padding: 12px;
  border-bottom: 1px solid #e9ecef;
  font-size: 14px;
  color: #333;
}

tr:last-child td {
  border-bottom: none;
}

tr:hover {
  background-color: #f8f9fa;
}

.rate-value {
  font-weight: 600;
  color: #0066cc;
}

.rate-time {
  color: #666;
  font-size: 12px;
}

/* Responsive */
@media (max-width: 768px) {
  .page-wrapper {
    padding: 16px;
  }

  .page-content {
    padding: 16px;
  }

  .exchange-form,
  .exchange-result,
  .rates-table {
    padding: 16px;
  }

  .currency-section {
    padding: 16px;
  }

  table {
    font-size: 12px;
  }

  th, td {
    padding: 8px;
  }
}
</style>
