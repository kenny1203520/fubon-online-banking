<script setup lang="ts">
import { useUtilityStore } from '../stores/utility'
import { onMounted } from 'vue'
import type { BillFilterOptions } from '../types'

const utilityStore = useUtilityStore()

onMounted(async () => {
  await fetchHistory()
})

const fetchHistory = async () => {
  const options: BillFilterOptions = {
    page: utilityStore.currentPage,
    per_page: utilityStore.pageSize
  }
  await utilityStore.fetchPaymentHistory(options)
}

const changePage = (newPage: number) => {
  utilityStore.$patch({ currentPage: newPage })
  fetchHistory()
}
</script>

<template>
  <div class="history-page">
    <div class="page-header">
      <h1>繳費紀錄</h1>
      <p>查看您的繳費歷史記錄</p>
    </div>

    <!-- 加載狀態 -->
    <div v-if="utilityStore.isLoading" class="loading-spinner">
      加載中...
    </div>

    <!-- 錯誤提示 -->
    <div v-if="utilityStore.error" class="alert alert-error">
      {{ utilityStore.error }}
    </div>

    <!-- 繳費記錄列表 -->
    <div v-if="!utilityStore.isLoading && utilityStore.paymentHistory.length > 0" class="history-container">
      <table class="history-table">
        <thead>
          <tr>
            <th>帳單ID</th>
            <th>金額</th>
            <th>繳費方式</th>
            <th>參考號碼</th>
            <th>繳費日期</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="payment in utilityStore.paymentHistory" :key="payment.id">
            <td>#{{ payment.bill_id }}</td>
            <td class="amount">新台幣 {{ payment.amount.toLocaleString() }}</td>
            <td>
              <span class="method-badge">
                {{ getPaymentMethodText(payment.payment_method) }}
              </span>
            </td>
            <td class="reference">{{ payment.reference_number }}</td>
            <td>{{ new Date(payment.created_at).toLocaleDateString() }}</td>
          </tr>
        </tbody>
      </table>

      <!-- 分頁 -->
      <div v-if="utilityStore.totalPages > 1" class="pagination">
        <button
          :disabled="utilityStore.currentPage === 1"
          @click="changePage(utilityStore.currentPage - 1)"
        >
          上一頁
        </button>
        <span>
          第 {{ utilityStore.currentPage }} / {{ utilityStore.totalPages }} 頁
        </span>
        <button
          :disabled="utilityStore.currentPage === utilityStore.totalPages"
          @click="changePage(utilityStore.currentPage + 1)"
        >
          下一頁
        </button>
      </div>
    </div>

    <!-- 空狀態 -->
    <div v-else-if="!utilityStore.isLoading" class="empty-state">
      <p>還沒有繳費紀錄</p>
      <router-link to="/utilities/bills" class="btn btn-primary">
        前往繳費
      </router-link>
    </div>
  </div>
</template>

<script lang="ts">
function getPaymentMethodText(method: string): string {
  const methods: Record<string, string> = {
    bank_transfer: '銀行轉帳',
    credit_card: '信用卡'
  }
  return methods[method] || method
}
</script>

<style scoped>
.history-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 28px;
  color: #333;
  margin: 0 0 8px 0;
}

.page-header p {
  color: #666;
  margin: 0;
}

.loading-spinner {
  text-align: center;
  padding: 40px;
  color: #999;
}

.alert {
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.alert-error {
  background-color: #ffebee;
  color: #c62828;
  border-left: 4px solid #c62828;
}

.history-container {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.history-table {
  width: 100%;
  border-collapse: collapse;
}

.history-table thead {
  background-color: #f5f5f5;
  border-bottom: 2px solid #e0e0e0;
}

.history-table th {
  padding: 16px;
  text-align: left;
  font-weight: 600;
  color: #333;
}

.history-table td {
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.history-table tr:hover {
  background-color: #fafafa;
}

.amount {
  font-weight: 600;
  color: #2e7d32;
}

.method-badge {
  display: inline-block;
  padding: 6px 12px;
  background-color: #e3f2fd;
  color: #0066cc;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.reference {
  font-family: 'Courier New', monospace;
  color: #666;
  font-size: 12px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  padding: 20px;
}

.pagination button {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: white;
  cursor: pointer;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination button:not(:disabled):hover {
  border-color: #0066cc;
  color: #0066cc;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #999;
}

.btn {
  display: inline-block;
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.3s ease;
  margin-top: 16px;
}

.btn-primary {
  background-color: #0066cc;
  color: white;
}

.btn-primary:hover {
  background-color: #0052a3;
}
</style>
