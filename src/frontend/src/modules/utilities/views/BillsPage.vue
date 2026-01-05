<script setup lang="ts">
import { useUtilityStore } from '../stores/utility'
import { ref, onMounted } from 'vue'
import type { BillFilterOptions } from '../types'

const utilityStore = useUtilityStore()
const filterStatus = ref<'all' | 'pending' | 'paid' | 'overdue'>('all')
const filterType = ref<string>('')
const selectedBill = ref<number | null>(null)
const showPaymentModal = ref(false)
const paymentAmount = ref<number>(0)
const selectedAccountId = ref<number>(0)

onMounted(async () => {
  await fetchBills()
})

const fetchBills = async () => {
  const options: BillFilterOptions = {
    page: utilityStore.currentPage,
    per_page: utilityStore.pageSize
  }

  if (filterStatus.value !== 'all') {
    options.status = filterStatus.value as 'pending' | 'paid' | 'overdue'
  }

  if (filterType.value) {
    options.bill_type = filterType.value
  }

  await utilityStore.fetchBills(options)
}

const openPaymentModal = (billId: number, amount: number) => {
  selectedBill.value = billId
  paymentAmount.value = amount
  showPaymentModal.value = true
}

const submitPayment = async () => {
  if (!selectedBill.value || !selectedAccountId.value) {
    alert('請選擇帳戶')
    return
  }

  try {
    await utilityStore.payBill({
      bill_id: selectedBill.value,
      account_id: selectedAccountId.value,
      amount: paymentAmount.value,
      payment_method: 'bank_transfer'
    })

    alert('繳費成功')
    showPaymentModal.value = false
    await fetchBills()
  } catch (error) {
    alert('繳費失敗：' + (error instanceof Error ? error.message : '未知錯誤'))
  }
}

const changePage = (newPage: number) => {
  utilityStore.$patch({ currentPage: newPage })
  fetchBills()
}

const getStatusBadgeClass = (status: string) => {
  switch (status) {
    case 'paid':
      return 'badge-success'
    case 'overdue':
      return 'badge-danger'
    default:
      return 'badge-warning'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'paid':
      return '已繳'
    case 'overdue':
      return '逾期'
    default:
      return '待繳'
  }
}
</script>

<template>
  <div class="bills-page">
    <div class="page-header">
      <h1>繳費帳單</h1>
      <p>管理和支付您的日常帳單</p>
    </div>

    <!-- 篩選工具 -->
    <div class="filters">
      <div class="filter-group">
        <label>帳單狀態</label>
        <select v-model="filterStatus" @change="fetchBills">
          <option value="all">全部</option>
          <option value="pending">待繳</option>
          <option value="paid">已繳</option>
          <option value="overdue">逾期</option>
        </select>
      </div>

      <div class="filter-group">
        <label>帳單類型</label>
        <select v-model="filterType" @change="fetchBills">
          <option value="">全部</option>
          <option value="water">水費</option>
          <option value="electricity">電費</option>
          <option value="gas">瓦斯費</option>
          <option value="phone">電話費</option>
          <option value="internet">網路費</option>
          <option value="insurance">保險費</option>
        </select>
      </div>
    </div>

    <!-- 加載狀態 -->
    <div v-if="utilityStore.isLoading" class="loading-spinner">
      加載中...
    </div>

    <!-- 錯誤提示 -->
    <div v-if="utilityStore.error" class="alert alert-error">
      {{ utilityStore.error }}
    </div>

    <!-- 帳單列表 -->
    <div v-if="!utilityStore.isLoading && utilityStore.bills.length > 0" class="bills-container">
      <table class="bills-table">
        <thead>
          <tr>
            <th>帳單類型</th>
            <th>供應商</th>
            <th>金額</th>
            <th>截止日期</th>
            <th>狀態</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="bill in utilityStore.bills" :key="bill.id" :class="{ 'row-paid': bill.status === 'paid' }">
            <td>{{ bill.bill_type }}</td>
            <td>{{ bill.provider }}</td>
            <td class="amount">{{ bill.amount.toLocaleString() }}</td>
            <td>{{ new Date(bill.due_date).toLocaleDateString() }}</td>
            <td>
              <span :class="['badge', getStatusBadgeClass(bill.status)]">
                {{ getStatusText(bill.status) }}
              </span>
            </td>
            <td class="actions">
              <button
                v-if="bill.status !== 'paid'"
                class="btn btn-pay"
                @click="openPaymentModal(bill.id, bill.amount)"
              >
                繳費
              </button>
              <span v-else class="text-muted">已繳</span>
            </td>
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
      <p>沒有找到符合條件的帳單</p>
    </div>

    <!-- 支付模態框 -->
    <div v-if="showPaymentModal" class="modal-overlay" @click.self="showPaymentModal = false">
      <div class="modal">
        <div class="modal-header">
          <h2>確認繳費</h2>
          <button class="close-btn" @click="showPaymentModal = false">✕</button>
        </div>

        <div class="modal-body">
          <div class="payment-info">
            <div class="info-row">
              <span>金額：</span>
              <strong>新台幣 {{ paymentAmount.toLocaleString() }}</strong>
            </div>

            <div class="form-group">
              <label>選擇繳費帳戶</label>
              <select v-model.number="selectedAccountId">
                <option value="">-- 請選擇帳戶 --</option>
                <option value="1">帳戶 1 (餘額: 10,000)</option>
                <option value="2">帳戶 2 (餘額: 25,000)</option>
                <option value="3">帳戶 3 (餘額: 50,000)</option>
              </select>
            </div>

            <div class="form-group">
              <label>繳費方式</label>
              <select>
                <option>銀行轉帳</option>
                <option>信用卡</option>
              </select>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showPaymentModal = false">
            取消
          </button>
          <button class="btn btn-primary" @click="submitPayment">
            確認繳費
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.bills-page {
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

.filters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 30px;
}

.filter-group {
  display: flex;
  flex-direction: column;
}

.filter-group label {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.filter-group select {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
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

.bills-container {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.bills-table {
  width: 100%;
  border-collapse: collapse;
}

.bills-table thead {
  background-color: #f5f5f5;
  border-bottom: 2px solid #e0e0e0;
}

.bills-table th {
  padding: 16px;
  text-align: left;
  font-weight: 600;
  color: #333;
}

.bills-table td {
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.bills-table tr:hover {
  background-color: #fafafa;
}

.bills-table tr.row-paid {
  opacity: 0.6;
}

.amount {
  font-weight: 600;
  color: #0066cc;
}

.badge {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.badge-success {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.badge-warning {
  background-color: #fff3e0;
  color: #f57c00;
}

.badge-danger {
  background-color: #ffebee;
  color: #c62828;
}

.actions {
  text-align: right;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-pay {
  background-color: #0066cc;
  color: white;
}

.btn-pay:hover {
  background-color: #0052a3;
}

.text-muted {
  color: #999;
  font-size: 14px;
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

/* 模態框樣式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 12px;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.modal-header h2 {
  margin: 0;
  font-size: 20px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
}

.modal-body {
  padding: 20px;
}

.payment-info {
  margin-bottom: 20px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  color: #333;
}

.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px;
  border-top: 1px solid #f0f0f0;
}

.btn-primary {
  background-color: #0066cc;
  color: white;
}

.btn-primary:hover {
  background-color: #0052a3;
}

.btn-secondary {
  background-color: #f0f0f0;
  color: #333;
}

.btn-secondary:hover {
  background-color: #e0e0e0;
}
</style>
