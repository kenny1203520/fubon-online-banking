<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useTransactionStore } from '../stores/transaction'
import type { TransactionQuery } from '../types'

const transactionStore = useTransactionStore()

// Filters
const accountId = ref<number>()
const selectedType = ref<'all' | 'deposit' | 'withdrawal' | 'transfer'>('all')
const dateFrom = ref('')
const dateTo = ref('')

// Loading and error states
const errorMessage = ref('')
const successMessage = ref('')

// Computed
const filteredTransactions = computed(() => {
  let result = transactionStore.transactions

  if (selectedType.value !== 'all') {
    result = result.filter(t => t.type === selectedType.value)
  }

  return result
})

const stats = computed(() => ({
  total: transactionStore.transactions.length,
  deposits: transactionStore.depositTotal,
  withdrawals: transactionStore.withdrawalTotal,
  net: transactionStore.totalAmount
}))

// Methods
const fetchData = async () => {
  errorMessage.value = ''
  
  try {
    const query: TransactionQuery = {
      account_id: accountId.value!,
      page: transactionStore.pagination.page,
      per_page: transactionStore.pagination.per_page
    }

    if (selectedType.value !== 'all') {
      query.type = selectedType.value
    }

    if (dateFrom.value) {
      query.frm = dateFrom.value
    }

    if (dateTo.value) {
      query.to = dateTo.value
    }

    await transactionStore.fetchTransactions(query)
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '載入交易記錄失敗'
  }
}

const handleSearch = () => {
  transactionStore.pagination.page = 1
  fetchData()
}

const handleReset = () => {
  selectedType.value = 'all'
  dateFrom.value = ''
  dateTo.value = ''
  transactionStore.pagination.page = 1
  fetchData()
}

const changePage = (newPage: number) => {
  transactionStore.pagination.page = newPage
  fetchData()
}

const getTypeText = (type: string) => {
  const typeMap: Record<string, string> = {
    'deposit': '存款',
    'withdrawal': '提款',
    'transfer': '轉帳'
  }
  return typeMap[type] || type
}

const getTypeClass = (type: string) => {
  return `type-badge type-${type}`
}

const formatCurrency = (amount: number, currency: string = 'TWD') => {
  const formatted = new Intl.NumberFormat('zh-TW', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2
  }).format(Math.abs(amount))
  
  return currency === 'TWD' ? `NT$ ${formatted}` : `${currency} ${formatted}`
}

const formatDateTime = (dateStr: string) => {
  const date = new Date(dateStr)
  return new Intl.DateTimeFormat('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).format(date)
}

const getAmountClass = (type: string) => {
  if (type === 'deposit') return 'amount-positive'
  if (type === 'withdrawal') return 'amount-negative'
  return ''
}

const getAmountPrefix = (type: string) => {
  if (type === 'deposit') return '+'
  if (type === 'withdrawal') return '-'
  return ''
}

onMounted(() => {
  // 從路由或其他方式取得 accountId
  // accountId.value = ... 
  // fetchData()
})
</script>

<template>
  <div class="page-wrapper">
    <div class="page-header">
      <h1>交易記錄</h1>
      <p>查看您的交易歷史</p>
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

    <!-- Statistics Cards -->
    <div v-if="transactionStore.hasTransactions" class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">交易總數</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card stat-positive">
        <div class="stat-label">總存款</div>
        <div class="stat-value">{{ formatCurrency(stats.deposits) }}</div>
      </div>
      <div class="stat-card stat-negative">
        <div class="stat-label">總提款</div>
        <div class="stat-value">{{ formatCurrency(stats.withdrawals) }}</div>
      </div>
      <div class="stat-card" :class="stats.net >= 0 ? 'stat-positive' : 'stat-negative'">
        <div class="stat-label">淨額</div>
        <div class="stat-value">{{ formatCurrency(stats.net) }}</div>
      </div>
    </div>

    <div class="page-content">
      <!-- Filters -->
      <div class="filters-section">
        <h3>篩選條件</h3>
        <div class="filters-grid">
          <div class="form-group">
            <label>交易類型</label>
            <select v-model="selectedType" class="form-control">
              <option value="all">全部</option>
              <option value="deposit">存款</option>
              <option value="withdrawal">提款</option>
              <option value="transfer">轉帳</option>
            </select>
          </div>

          <div class="form-group">
            <label>起始日期</label>
            <input 
              v-model="dateFrom" 
              type="date" 
              class="form-control"
            />
          </div>

          <div class="form-group">
            <label>結束日期</label>
            <input 
              v-model="dateTo" 
              type="date" 
              class="form-control"
            />
          </div>

          <div class="form-group filter-actions">
            <button @click="handleSearch" class="btn btn-primary">
              搜尋
            </button>
            <button @click="handleReset" class="btn btn-secondary">
              重置
            </button>
          </div>
        </div>
      </div>

      <!-- Transactions List -->
      <div v-if="transactionStore.isLoading" class="loading-container">
        <div class="spinner"></div>
        <p>載入中...</p>
      </div>

      <div v-else-if="!transactionStore.hasTransactions" class="empty-state">
        <p>尚無交易記錄</p>
      </div>

      <div v-else class="transactions-section">
        <h3>交易明細</h3>
        <div class="transactions-table">
          <table>
            <thead>
              <tr>
                <th>交易時間</th>
                <th>類型</th>
                <th>金額</th>
                <th>幣別</th>
                <th>說明</th>
                <th>相關帳戶</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="transaction in filteredTransactions" :key="transaction.id">
                <td>{{ formatDateTime(transaction.created_at) }}</td>
                <td>
                  <span :class="getTypeClass(transaction.type)">
                    {{ getTypeText(transaction.type) }}
                  </span>
                </td>
                <td :class="getAmountClass(transaction.type)">
                  {{ getAmountPrefix(transaction.type) }}{{ formatCurrency(transaction.amount, transaction.currency) }}
                </td>
                <td>{{ transaction.currency }}</td>
                <td>{{ transaction.description || '-' }}</td>
                <td>{{ transaction.related_account || '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div v-if="transactionStore.pagination.total > transactionStore.pagination.per_page" class="pagination">
          <button 
            @click="changePage(transactionStore.pagination.page - 1)"
            :disabled="transactionStore.pagination.page === 1"
            class="btn btn-sm"
          >
            上一頁
          </button>
          
          <span class="pagination-info">
            第 {{ transactionStore.pagination.page }} 頁，
            共 {{ Math.ceil(transactionStore.pagination.total / transactionStore.pagination.per_page) }} 頁
          </span>
          
          <button 
            @click="changePage(transactionStore.pagination.page + 1)"
            :disabled="transactionStore.pagination.page >= Math.ceil(transactionStore.pagination.total / transactionStore.pagination.per_page)"
            class="btn btn-sm"
          >
            下一頁
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-wrapper {
  padding: 20px;
  max-width: 1400px;
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

/* Statistics */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.stat-card.stat-positive {
  border-left: 4px solid #4caf50;
}

.stat-card.stat-negative {
  border-left: 4px solid #f44336;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #333;
}

.stat-positive .stat-value {
  color: #4caf50;
}

.stat-negative .stat-value {
  color: #f44336;
}

/* Page Content */
.page-content {
  background: white;
  padding: 24px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

/* Filters */
.filters-section {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.filters-section h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  color: #333;
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  align-items: end;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-size: 14px;
  color: #555;
  margin-bottom: 6px;
  font-weight: 500;
}

.form-control {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-control:focus {
  outline: none;
  border-color: #0066cc;
}

.filter-actions {
  display: flex;
  gap: 8px;
}

/* Buttons */
.btn {
  padding: 10px 20px;
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

.btn-primary:hover {
  background-color: #0052a3;
}

.btn-secondary {
  background-color: #f5f5f5;
  color: #333;
}

.btn-secondary:hover {
  background-color: #e0e0e0;
}

.btn-sm {
  padding: 8px 16px;
  font-size: 13px;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Loading */
.loading-container {
  text-align: center;
  padding: 60px 40px;
  color: #666;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #0066cc;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 60px 40px;
  color: #999;
}

/* Transactions */
.transactions-section h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  color: #333;
}

.transactions-table {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background-color: #f8f9fa;
}

th {
  padding: 12px;
  text-align: left;
  font-weight: 600;
  font-size: 14px;
  color: #555;
  border-bottom: 2px solid #dee2e6;
}

td {
  padding: 12px;
  border-bottom: 1px solid #e9ecef;
  font-size: 14px;
  color: #333;
}

tr:hover {
  background-color: #f8f9fa;
}

.type-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.type-deposit {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.type-withdrawal {
  background-color: #ffebee;
  color: #c62828;
}

.type-transfer {
  background-color: #e3f2fd;
  color: #1565c0;
}

.amount-positive {
  color: #4caf50;
  font-weight: 600;
}

.amount-negative {
  color: #f44336;
  font-weight: 600;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #e0e0e0;
}

.pagination-info {
  font-size: 14px;
  color: #666;
}

/* Responsive */
@media (max-width: 768px) {
  .page-wrapper {
    padding: 16px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .filters-grid {
    grid-template-columns: 1fr;
  }

  .filter-actions {
    flex-direction: column;
  }

  .filter-actions .btn {
    width: 100%;
  }

  .transactions-table {
    font-size: 12px;
  }

  th, td {
    padding: 8px;
  }
}
</style>
