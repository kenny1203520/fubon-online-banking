<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAccountStore } from '@/modules/accounts/stores/account'
import Alert from '@/shared/Alert.vue'
import LoadingSpinner from '@/shared/LoadingSpinner.vue'

const router = useRouter()
const route = useRoute()
const accountStore = useAccountStore()

const error = ref<string | null>(null)
const success = ref<string | null>(null)
const accountId = computed(() => route.params.id as string)

// Tab 狀態
const activeTab = ref<'info' | 'transactions'>('info')

// 交易篩選
const transactionFilters = ref({
  page: 1,
  per_page: 10,
  frm: '',
  to: ''
})

// 格式化金額
const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('zh-TW', {
    style: 'currency',
    currency: 'TWD',
    minimumFractionDigits: 0
  }).format(amount)
}

// 格式化日期時間
const formatDateTime = (dateString: string): string => {
  return new Date(dateString).toLocaleString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 取得狀態顯示文字
const getStatusText = (status: string): string => {
  const statusMap: Record<string, string> = {
    'pending': '待審核',
    'active': '正常',
    'inactive': '停用',
    'closed': '已關閉'
  }
  return statusMap[status] || status
}

// 取得狀態樣式類別
const getStatusClass = (status: string): string => {
  const classMap: Record<string, string> = {
    'pending': 'status-pending',
    'active': 'status-active',
    'inactive': 'status-inactive',
    'closed': 'status-closed'
  }
  return classMap[status] || ''
}

// 取得交易類型文字
const getTransactionTypeText = (type: string): string => {
  const typeMap: Record<string, string> = {
    'deposit': '存款',
    'withdrawal': '提款',
    'transfer': '轉帳'
  }
  return typeMap[type] || type
}

// 取得交易類型樣式
const getTransactionTypeClass = (type: string): string => {
  const classMap: Record<string, string> = {
    'deposit': 'type-deposit',
    'withdrawal': 'type-withdrawal',
    'transfer': 'type-transfer'
  }
  return classMap[type] || ''
}

// 載入帳戶資訊
const loadAccountDetail = async () => {
  error.value = null
  try {
    await accountStore.fetchAccountById(accountId.value)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '載入帳戶資訊失敗'
  }
}

// 載入交易紀錄
const loadTransactions = async () => {
  error.value = null
  try {
    await accountStore.fetchTransactions(accountId.value, transactionFilters.value)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '載入交易紀錄失敗'
  }
}

// 刷新餘額
const refreshBalance = async () => {
  error.value = null
  success.value = null
  try {
    await accountStore.getBalance(accountId.value)
    success.value = '餘額已更新'
  } catch (err) {
    error.value = err instanceof Error ? err.message : '刷新餘額失敗'
  }
}

// 切換無現金提款
const toggleCashless = async () => {
  error.value = null
  success.value = null
  if (!accountStore.currentAccount) return

  try {
    const newState = !accountStore.currentAccount.cashless_enabled
    await accountStore.setCashless(accountId.value, newState)
    success.value = `無現金提款功能已${newState ? '啟用' : '停用'}`
  } catch (err) {
    error.value = err instanceof Error ? err.message : '設定失敗'
  }
}

// 返回列表
const goBack = () => {
  router.push('/accounts')
}

// 切換 Tab
const switchTab = (tab: 'info' | 'transactions') => {
  activeTab.value = tab
  if (tab === 'transactions' && accountStore.transactions.length === 0) {
    loadTransactions()
  }
}

// 頁面掛載時載入資料
onMounted(() => {
  loadAccountDetail()
})
</script>

<template>
  <div class="page-wrapper">
    <div class="page-header">
      <button class="btn-back" @click="goBack">
        ← 返回列表
      </button>
      <h1>帳戶詳情</h1>
    </div>

    <div class="page-content">
      <!-- 錯誤資訊 -->
      <Alert
        v-if="error"
        :message="error"
        type="error"
        @close="error = null"
      />

      <!-- 成功資訊 -->
      <Alert
        v-if="success"
        :message="success"
        type="success"
        @close="success = null"
      />

      <!-- 載入中 -->
      <div v-if="accountStore.isLoading && !accountStore.currentAccount" class="loading-container">
        <LoadingSpinner />
        <p>載入中...</p>
      </div>

      <!-- 帳戶資訊 -->
      <div v-else-if="accountStore.currentAccount" class="account-detail">
        <!-- 帳戶卡片 -->
        <div class="account-card">
          <div class="card-header">
            <div>
              <h2 class="account-name">{{ accountStore.currentAccount.full_name }}</h2>
              <span class="account-id">帳戶 {{ accountStore.currentAccount.account_number }}</span>
            </div>
            <span :class="['account-status', getStatusClass(accountStore.currentAccount.status)]">
              {{ getStatusText(accountStore.currentAccount.status) }}
            </span>
          </div>

          <div class="card-body">
            <div class="balance-display">
              <span class="balance-label">帳戶餘額</span>
              <span class="balance-amount">
                {{ formatCurrency(accountStore.currentAccount.balance) }}
              </span>
            </div>

            <button class="btn-refresh" @click="refreshBalance" :disabled="accountStore.isLoading">
              ↻ 刷新餘額
            </button>
          </div>
        </div>

        <!-- Tab 切換 -->
        <div class="tabs">
          <button
            :class="['tab-button', { active: activeTab === 'info' }]"
            @click="switchTab('info')"
          >
            基本資訊
          </button>
          <button
            :class="['tab-button', { active: activeTab === 'transactions' }]"
            @click="switchTab('transactions')"
          >
            交易紀錄
          </button>
        </div>

        <!-- Tab 內容 -->
        <div class="tab-content">
          <!-- 基本資訊 Tab -->
          <div v-if="activeTab === 'info'" class="info-section">
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">帳戶持有人</span>
                <span class="info-value">{{ accountStore.currentAccount.full_name }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">身分證號</span>
                <span class="info-value">{{ accountStore.currentAccount.id_number }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">電子郵件</span>
                <span class="info-value">{{ accountStore.currentAccount.email || '未提供' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">開戶日期</span>
                <span class="info-value">{{ formatDateTime(accountStore.currentAccount.created_at) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">帳戶狀態</span>
                <span class="info-value">{{ getStatusText(accountStore.currentAccount.status) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">無現金提款</span>
                <div class="cashless-control">
                  <span class="info-value">
                    {{ accountStore.currentAccount.cashless_enabled ? '已啟用' : '未啟用' }}
                  </span>
                  <button
                    class="btn-toggle"
                    @click="toggleCashless"
                    :disabled="accountStore.isLoading"
                  >
                    {{ accountStore.currentAccount.cashless_enabled ? '停用' : '啟用' }}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- 交易紀錄 Tab -->
          <div v-else-if="activeTab === 'transactions'" class="transactions-section">
            <div v-if="accountStore.isLoading" class="loading-container">
              <LoadingSpinner />
              <p>載入交易紀錄中...</p>
            </div>

            <div v-else-if="accountStore.transactions.length > 0" class="transactions-list">
              <div
                v-for="transaction in accountStore.transactions"
                :key="transaction.id"
                class="transaction-item"
              >
                <div class="transaction-info">
                  <span :class="['transaction-type', getTransactionTypeClass(transaction.type)]">
                    {{ getTransactionTypeText(transaction.type) }}
                  </span>
                  <span class="transaction-desc">{{ transaction.description || '無說明' }}</span>
                  <span class="transaction-date">{{ formatDateTime(transaction.created_at) }}</span>
                </div>
                <div class="transaction-amount">
                  <span :class="['amount', transaction.type === 'deposit' ? 'positive' : 'negative']">
                    {{ transaction.type === 'deposit' ? '+' : '-' }}{{ formatCurrency(Math.abs(transaction.amount)) }}
                  </span>
                </div>
              </div>
            </div>

            <div v-else class="empty-state">
              <div class="empty-icon">📝</div>
              <p>暫無交易紀錄</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 未找到帳戶 -->
      <div v-else class="empty-state">
        <div class="empty-icon">❌</div>
        <h3>找不到帳戶</h3>
        <p>此帳戶不存在或已被刪除</p>
        <button class="btn-primary" @click="goBack">
          返回列表
        </button>
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

.btn-back {
  background: none;
  border: none;
  color: #0066cc;
  cursor: pointer;
  font-size: 14px;
  padding: 8px 0;
  margin-bottom: 12px;
  transition: color 0.2s;
}

.btn-back:hover {
  color: #004499;
  text-decoration: underline;
}

.page-header h1 {
  margin: 0;
  font-size: 28px;
  color: #333;
}

.page-content {
  background: white;
  padding: 24px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #999;
}

.loading-container p {
  margin-top: 16px;
}

.account-detail {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.account-card {
  background: linear-gradient(135deg, #0066cc 0%, #004499 100%);
  color: white;
  padding: 30px;
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.account-name {
  margin: 0 0 8px 0;
  font-size: 24px;
}

.account-id {
  font-size: 13px;
  opacity: 0.8;
}

.account-status {
  padding: 6px 14px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.card-body {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.balance-display {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.balance-label {
  font-size: 14px;
  opacity: 0.8;
}

.balance-amount {
  font-size: 36px;
  font-weight: 700;
}

.btn-refresh {
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn-refresh:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
}

.btn-refresh:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.tabs {
  display: flex;
  gap: 4px;
  border-bottom: 2px solid #e0e0e0;
}

.tab-button {
  padding: 12px 24px;
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s;
  position: relative;
}

.tab-button:hover {
  color: #0066cc;
}

.tab-button.active {
  color: #0066cc;
}

.tab-button.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 2px;
  background: #0066cc;
}

.tab-content {
  min-height: 400px;
}

.info-section {
  padding: 24px 0;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-label {
  font-size: 13px;
  color: #999;
  font-weight: 600;
}

.info-value {
  font-size: 15px;
  color: #333;
}

.cashless-control {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-toggle {
  padding: 6px 12px;
  border: 1px solid #0066cc;
  background: white;
  color: #0066cc;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.btn-toggle:hover:not(:disabled) {
  background: #0066cc;
  color: white;
}

.btn-toggle:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.transactions-section {
  padding: 24px 0;
}

.transactions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.transaction-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  transition: all 0.2s;
}

.transaction-item:hover {
  border-color: #0066cc;
  background: #f8f9fa;
}

.transaction-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.transaction-type {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  width: fit-content;
}

.type-deposit {
  background: #d4edda;
  color: #155724;
}

.type-withdrawal {
  background: #f8d7da;
  color: #721c24;
}

.type-transfer {
  background: #d1ecf1;
  color: #0c5460;
}

.transaction-desc {
  font-size: 14px;
  color: #666;
}

.transaction-date {
  font-size: 12px;
  color: #999;
}

.transaction-amount {
  font-size: 18px;
  font-weight: 700;
}

.amount.positive {
  color: #28a745;
}

.amount.negative {
  color: #dc3545;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-state h3 {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 20px;
}

.empty-state p {
  margin: 0 0 24px 0;
  color: #999;
  font-size: 14px;
}

.btn-primary {
  padding: 12px 24px;
  background: linear-gradient(135deg, #0066cc 0%, #004499 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  box-shadow: 0 4px 12px rgba(0, 102, 204, 0.3);
  transform: translateY(-1px);
}

@media (max-width: 768px) {
  .card-body {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .transaction-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
