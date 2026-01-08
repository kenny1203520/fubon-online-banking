<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { creditCardService } from '../services/creditcard'
import type { CreditCardApplication } from '../types'

const router = useRouter()
const applications = ref<CreditCardApplication[]>([])
const isLoading = ref(false)
const error = ref<string | null>(null)

const goToApply = () => {
  router.push('/cards/apply')
}

const loadApplications = async () => {
  isLoading.value = true
  error.value = null
  try {
    applications.value = await creditCardService.getCards()
  } catch (err: any) {
    error.value = err.response?.data?.detail || '載入失敗'
    console.error('載入信用卡申請失敗:', err)
  } finally {
    isLoading.value = false
  }
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: '審核中',
    approved: '已核准',
    rejected: '已拒絕'
  }
  return statusMap[status] || status
}

const getStatusClass = (status: string) => {
  const classMap: Record<string, string> = {
    pending: 'status-pending',
    approved: 'status-approved',
    rejected: 'status-rejected'
  }
  return classMap[status] || ''
}

onMounted(() => {
  loadApplications()
})
</script>

<template>
  <div class="page-wrapper">
    <div class="page-header">
      <h1>信用卡</h1>
      <p>管理您的信用卡</p>
      <button class="btn-apply" @click="goToApply">
        + 申請信用卡
      </button>
    </div>
    <div class="page-content">
      <div v-if="isLoading" class="loading">載入中...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else-if="applications.length === 0" class="placeholder">
        <div class="empty-icon">💳</div>
        <h3>尚無信用卡申請</h3>
        <p>您還沒有申請任何信用卡</p>
        <button class="btn-primary" @click="goToApply">
          立即申請信用卡
        </button>
      </div>
      <div v-else class="applications-list">
        <div v-for="app in applications" :key="app.id" class="application-card">
          <div class="card-header">
            <h3>{{ app.card_type }}</h3>
            <span class="status" :class="getStatusClass(app.status)">{{ getStatusText(app.status) }}</span>
          </div>
          <div class="card-body">
            <div class="info-row">
              <span class="label">申請日期：</span>
              <span class="value">{{ new Date(app.created_at).toLocaleDateString('zh-TW') }}</span>
            </div>
            <div class="info-row">
              <span class="label">年收入：</span>
              <span class="value">NT$ {{ app.annual_income.toLocaleString() }}</span>
            </div>
            <div class="info-row">
              <span class="label">就業狀態：</span>
              <span class="value">{{ app.employment_status }}</span>
            </div>
            <div class="info-row" v-if="app.company_name">
              <span class="label">公司名稱：</span>
              <span class="value">{{ app.company_name }}</span>
            </div>
            <div class="info-row" v-if="app.position">
              <span class="label">職位：</span>
              <span class="value">{{ app.position }}</span>
            </div>
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
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

.btn-apply {
  padding: 12px 24px;
  background: linear-gradient(135deg, #0066cc 0%, #004499 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-apply:hover {
  box-shadow: 0 4px 12px rgba(0, 102, 204, 0.3);
  transform: translateY(-1px);
}

.page-content { 
  background: white; 
  padding: 60px 24px; 
  border-radius: 8px; 
  border: 1px solid #e0e0e0; 
}

.placeholder { 
  color: #999; 
  text-align: center; 
  padding: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.empty-icon {
  font-size: 64px;
  opacity: 0.5;
}

.placeholder h3 {
  margin: 0;
  color: #333;
  font-size: 20px;
}

.placeholder p {
  margin: 0;
  color: #999;
  font-size: 14px;
}

.btn-primary {
  margin-top: 8px;
  padding: 12px 32px;
  background: linear-gradient(135deg, #0066cc 0%, #004499 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  box-shadow: 0 4px 12px rgba(0, 102, 204, 0.3);
  transform: translateY(-1px);
}

.loading, .error {
  text-align: center;
  padding: 40px;
  color: #666;
  font-size: 16px;
}

.error {
  color: #d32f2f;
}

.applications-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.application-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  transition: all 0.3s ease;
}

.application-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.status {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
}

.status-pending {
  background: #fff3e0;
  color: #f57c00;
}

.status-approved {
  background: #e8f5e9;
  color: #388e3c;
}

.status-rejected {
  background: #ffebee;
  color: #d32f2f;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
}

.info-row .label {
  color: #666;
  font-weight: 500;
}

.info-row .value {
  color: #333;
  font-weight: 600;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .btn-apply {
    width: 100%;
  }
}
</style>
