<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAccountStore } from '@/modules/accounts/stores/account'
import Alert from '@/shared/Alert.vue'
import LoadingSpinner from '@/shared/LoadingSpinner.vue'

const router = useRouter()
const accountStore = useAccountStore()

const error = ref<string | null>(null)

// 格式化金額
const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('zh-TW', {
    style: 'currency',
    currency: 'TWD',
    minimumFractionDigits: 0
  }).format(amount)
}

// 格式化日期
const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
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

// 載入帳戶列表
const loadAccounts = async () => {
  error.value = null
  try {
    await accountStore.fetchAccounts()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '載入帳戶列表失敗'
  }
}

// 切換頁面
const changePage = async (page: number) => {
  error.value = null
  try {
    await accountStore.fetchAccounts(page, accountStore.perPage)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '載入頁面失敗'
  }
}

// 查看帳戶詳情
const viewAccountDetail = (accountId: string) => {
  router.push(`/accounts/${accountId}`)
}

// 前往開戶頁面
const goToOpenAccount = () => {
  router.push('/accounts/open')
}

// 刷新餘額
const refreshBalance = async (accountId: string) => {
  try {
    await accountStore.getBalance(accountId)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '刷新餘額失敗'
  }
}

// 頁面掛載時載入資料
onMounted(() => {
  loadAccounts()
})
</script>

<template>
  <div class="page-wrapper">
    <div class="page-header">
      <div class="header-content">
        <div>
          <h1>帳戶管理</h1>
          <p>查看和管理您的所有帳戶</p>
        </div>
        <button class="btn-primary" @click="goToOpenAccount">
          <span class="icon">+</span>
          開戶申請
        </button>
      </div>
    </div>

    <div class="page-content">
      <!-- 錯誤資訊 -->
      <Alert
        v-if="error"
        :message="error"
        type="error"
        @close="error = null"
      />

      <!-- 載入中 -->
      <div v-if="accountStore.isLoading" class="loading-container">
        <LoadingSpinner />
        <p>載入中...</p>
      </div>

      <!-- 帳戶統計 -->
      <div v-else-if="accountStore.hasAccounts" class="account-summary">
        <div class="summary-card">
          <div class="summary-label">總帳戶數</div>
          <div class="summary-value">{{ accountStore.accounts.length }}</div>
        </div>
        <div class="summary-card">
          <div class="summary-label">有效帳戶</div>
          <div class="summary-value">{{ accountStore.activeAccounts.length }}</div>
        </div>
        <div class="summary-card total-balance">
          <div class="summary-label">總餘額</div>
          <div class="summary-value">{{ formatCurrency(accountStore.totalBalance) }}</div>
        </div>
      </div>

      <!-- 帳戶列表 -->
      <div v-if="!accountStore.isLoading && accountStore.hasAccounts" class="account-list">
        <div
          v-for="account in accountStore.accounts"
          :key="account.id"
          class="account-card"
          @click="viewAccountDetail(account.id)"
        >
          <div class="account-header">
            <div class="account-info">
              <h3 class="account-name">{{ account.full_name }}</h3>
              <span class="account-id">帳戶 {{ account.account_number }}</span>
            </div>
            <span :class="['account-status', getStatusClass(account.status)]">
              {{ getStatusText(account.status) }}
            </span>
          </div>

          <div class="account-body">
            <div class="account-detail">
              <span class="detail-label">身分證號</span>
              <span class="detail-value">{{ account.id_number }}</span>
            </div>
            <div class="account-detail">
              <span class="detail-label">電子郵件</span>
              <span class="detail-value">{{ account.email || '未提供' }}</span>
            </div>
            <div class="account-detail">
              <span class="detail-label">開戶日期</span>
              <span class="detail-value">{{ formatDate(account.created_at) }}</span>
            </div>
          </div>

          <div class="account-footer">
            <div class="balance-section">
              <span class="balance-label">帳戶餘額</span>
              <span class="balance-amount">{{ formatCurrency(account.balance) }}</span>
            </div>
            <div class="account-actions">
              <button
                class="btn-icon"
                @click.stop="refreshBalance(account.id)"
                title="刷新餘額"
              >
                ↻
              </button>
              <span v-if="account.cashless_enabled" class="cashless-badge" title="已啟用無現金提款">
                無現金
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 空狀態 -->
      <div v-if="!accountStore.isLoading && !accountStore.hasAccounts" class="empty-state">
        <div class="empty-icon">📋</div>
        <h3>尚無帳戶</h3>
        <p>您目前還沒有任何帳戶，立即申請開戶吧！</p>
        <button class="btn-primary" @click="goToOpenAccount">
          立即開戶
        </button>
      </div>

      <!-- 分頁 -->
      <div v-if="accountStore.hasAccounts && accountStore.totalPages > 1" class="pagination">
        <button
          class="btn-page"
          :disabled="accountStore.currentPage === 1"
          @click="changePage(accountStore.currentPage - 1)"
        >
          上一頁
        </button>
        <span class="page-info">
          第 {{ accountStore.currentPage }} / {{ accountStore.totalPages }} 頁
        </span>
        <button
          class="btn-page"
          :disabled="accountStore.currentPage === accountStore.totalPages"
          @click="changePage(accountStore.currentPage + 1)"
        >
          下一頁
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

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header h1 {
  margin: 0;
  font-size: 28px;
  color: #333;
}

.page-header p {
  margin: 8px 0 0 0;
  color: #999;
  font-size: 14px;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 8px;
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

.btn-primary .icon {
  font-size: 18px;
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

.account-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.summary-card {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.summary-card.total-balance {
  background: linear-gradient(135deg, #0066cc 0%, #004499 100%);
  color: white;
}

.summary-label {
  font-size: 13px;
  color: #666;
  margin-bottom: 8px;
}

.total-balance .summary-label {
  color: rgba(255, 255, 255, 0.8);
}

.summary-value {
  font-size: 24px;
  font-weight: 700;
  color: #333;
}

.total-balance .summary-value {
  color: white;
}

.account-list {
  display: grid;
  gap: 16px;
}

.account-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.account-card:hover {
  border-color: #0066cc;
  box-shadow: 0 2px 8px rgba(0, 102, 204, 0.1);
  transform: translateY(-2px);
}

.account-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.account-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.account-name {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.account-id {
  font-size: 13px;
  color: #999;
}

.account-status {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.status-pending {
  background: #fff3cd;
  color: #856404;
}

.status-active {
  background: #d4edda;
  color: #155724;
}

.status-inactive {
  background: #f8d7da;
  color: #721c24;
}

.status-closed {
  background: #e2e3e5;
  color: #383d41;
}

.account-body {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.account-detail {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-label {
  font-size: 12px;
  color: #999;
}

.detail-value {
  font-size: 14px;
  color: #333;
}

.account-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.balance-section {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.balance-label {
  font-size: 12px;
  color: #999;
}

.balance-amount {
  font-size: 20px;
  font-weight: 700;
  color: #0066cc;
}

.account-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-icon {
  width: 32px;
  height: 32px;
  border: 1px solid #e0e0e0;
  border-radius: 50%;
  background: white;
  cursor: pointer;
  font-size: 16px;
  color: #666;
  transition: all 0.2s;
}

.btn-icon:hover {
  border-color: #0066cc;
  color: #0066cc;
  background: #f0f7ff;
}

.cashless-badge {
  padding: 4px 8px;
  background: #d4edda;
  color: #155724;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
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

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #e0e0e0;
}

.btn-page {
  padding: 8px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  background: white;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-page:hover:not(:disabled) {
  border-color: #0066cc;
  color: #0066cc;
  background: #f0f7ff;
}

.btn-page:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #666;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .account-summary {
    grid-template-columns: 1fr;
  }

  .account-body {
    grid-template-columns: 1fr;
  }

  .account-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
