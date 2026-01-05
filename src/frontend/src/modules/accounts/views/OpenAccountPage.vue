<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAccountStore } from '@/modules/accounts/store/account'
import Alert from '@/shared/Alert.vue'

const router = useRouter()
const accountStore = useAccountStore()

// 表單資料
const form = ref({
  full_name: '',
  id_number: '',
  email: '',
  initial_deposit: 0
})

const isLoading = ref(false)
const error = ref<string | null>(null)
const success = ref<string | null>(null)
const agreedToTerms = ref(false)

// 驗證身分證號格式（台灣身分證號）
const validateIdNumber = (idNumber: string): boolean => {
  const pattern = /^[A-Z][12]\d{8}$/
  return pattern.test(idNumber)
}

// 驗證電子郵件格式
const validateEmail = (email: string): boolean => {
  if (!email) return true // 電子郵件為選填
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

// 表單驗證
const validateForm = (): boolean => {
  if (!form.value.full_name) {
    error.value = '請輸入姓名'
    return false
  }
  
  if (form.value.full_name.length < 2) {
    error.value = '姓名至少需要 2 個字元'
    return false
  }

  if (!form.value.id_number) {
    error.value = '請輸入身分證號'
    return false
  }

  if (!validateIdNumber(form.value.id_number)) {
    error.value = '身分證號格式不正確'
    return false
  }

  if (form.value.email && !validateEmail(form.value.email)) {
    error.value = '電子郵件格式不正確'
    return false
  }

  if (form.value.initial_deposit < 1000) {
    error.value = '初始存款金額至少需要 1,000 元'
    return false
  }

  if (form.value.initial_deposit > 10000000) {
    error.value = '初始存款金額不可超過 10,000,000 元'
    return false
  }

  if (!agreedToTerms.value) {
    error.value = '請同意服務條款及隱私權政策'
    return false
  }

  return true
}

// 提交開戶申請
const handleSubmit = async () => {
  error.value = null
  success.value = null

  if (!validateForm()) {
    return
  }

  isLoading.value = true

  try {
    const result = await accountStore.openAccount({
      full_name: form.value.full_name,
      id_number: form.value.id_number,
      email: form.value.email || undefined,
      initial_deposit: form.value.initial_deposit
    })

    success.value = `申請成功！您的申請編號為 ${result.account_id}，狀態為：${result.message}`
    
    // 清空表單
    form.value = {
      full_name: '',
      id_number: '',
      email: '',
      initial_deposit: 0
    }
    agreedToTerms.value = false

    // 2 秒後跳轉到帳戶列表
    setTimeout(() => {
      router.push('/accounts')
    }, 2000)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '開戶申請失敗'
  } finally {
    isLoading.value = false
  }
}

// 返回列表
const goBack = () => {
  router.push('/accounts')
}

// 格式化金額輸入
const formatDepositInput = () => {
  const value = form.value.initial_deposit
  if (value < 0) {
    form.value.initial_deposit = 0
  }
}
</script>

<template>
  <div class="page-wrapper">
    <div class="page-header">
      <button class="btn-back" @click="goBack">
        ← 返回列表
      </button>
      <div>
        <h1>開戶申請</h1>
        <p>填寫以下資料申請新帳戶</p>
      </div>
    </div>

    <div class="page-content">
      <div class="form-container">
        <!-- 成功訊息 -->
        <Alert
          v-if="success"
          :message="success"
          type="success"
        />

        <!-- 錯誤訊息 -->
        <Alert
          v-if="error"
          :message="error"
          type="error"
          @close="error = null"
        />

        <!-- 開戶說明 -->
        <div class="info-section">
          <h3>📋 開戶須知</h3>
          <ul class="info-list">
            <li>請確保您提供的個人資料真實有效</li>
            <li>初始存款金額最低為 1,000 元</li>
            <li>申請提交後需等待審核，審核通過後帳戶將自動啟用</li>
            <li>您可以在帳戶列表中查看申請狀態</li>
          </ul>
        </div>

        <!-- 開戶表單 -->
        <form class="account-form" @submit.prevent="handleSubmit">
          <!-- 姓名 -->
          <div class="form-group">
            <label for="full_name" class="form-label">
              姓名 <span class="required">*</span>
            </label>
            <input
              id="full_name"
              v-model="form.full_name"
              type="text"
              placeholder="請輸入真實姓名"
              class="form-input"
              :disabled="isLoading"
              maxlength="50"
            />
            <span class="form-hint">請輸入您的真實姓名</span>
          </div>

          <!-- 身分證號 -->
          <div class="form-group">
            <label for="id_number" class="form-label">
              身分證號 <span class="required">*</span>
            </label>
            <input
              id="id_number"
              v-model="form.id_number"
              type="text"
              placeholder="例如：A123456789"
              class="form-input"
              :disabled="isLoading"
              maxlength="10"
              @input="form.id_number = form.id_number.toUpperCase()"
            />
            <span class="form-hint">格式：首位大寫英文字母 + 9 位數字</span>
          </div>

          <!-- 電子郵件 -->
          <div class="form-group">
            <label for="email" class="form-label">
              電子郵件 <span class="optional">(選填)</span>
            </label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              placeholder="example@email.com"
              class="form-input"
              :disabled="isLoading"
            />
            <span class="form-hint">用於接收帳戶相關通知</span>
          </div>

          <!-- 初始存款 -->
          <div class="form-group">
            <label for="initial_deposit" class="form-label">
              初始存款金額（元） <span class="required">*</span>
            </label>
            <input
              id="initial_deposit"
              v-model.number="form.initial_deposit"
              type="number"
              placeholder="請輸入初始存款金額"
              class="form-input"
              :disabled="isLoading"
              min="1000"
              max="10000000"
              step="100"
              @input="formatDepositInput"
            />
            <span class="form-hint">最低金額：1,000 元，最高金額：10,000,000 元</span>
          </div>

          <!-- 金額預覽 -->
          <div v-if="form.initial_deposit >= 1000" class="amount-preview">
            <span class="preview-label">初始存款金額：</span>
            <span class="preview-amount">
              {{ new Intl.NumberFormat('zh-TW', { style: 'currency', currency: 'TWD', minimumFractionDigits: 0 }).format(form.initial_deposit) }}
            </span>
          </div>

          <!-- 服務條款 -->
          <div class="form-group checkbox-group">
            <label class="checkbox-label">
              <input
                v-model="agreedToTerms"
                type="checkbox"
                :disabled="isLoading"
              />
              <span>
                我已閱讀並同意
                <a href="#" class="link" @click.prevent>服務條款</a>
                及
                <a href="#" class="link" @click.prevent>隱私權政策</a>
              </span>
            </label>
          </div>

          <!-- 提交按鈕 -->
          <div class="form-actions">
            <button
              type="button"
              class="btn-secondary"
              @click="goBack"
              :disabled="isLoading"
            >
              取消
            </button>
            <button
              type="submit"
              class="btn-primary"
              :disabled="isLoading || !agreedToTerms"
            >
              <span v-if="!isLoading">提交申請</span>
              <span v-else>處理中...</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-wrapper {
  padding: 20px;
  max-width: 800px;
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
  margin: 0 0 8px 0;
  font-size: 28px;
  color: #333;
}

.page-header p {
  margin: 0;
  color: #999;
  font-size: 14px;
}

.page-content {
  background: white;
  padding: 32px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.form-container {
  max-width: 600px;
  margin: 0 auto;
}

.info-section {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  border-left: 4px solid #0066cc;
  margin-bottom: 32px;
}

.info-section h3 {
  margin: 0 0 12px 0;
  color: #333;
  font-size: 16px;
}

.info-list {
  margin: 0;
  padding-left: 20px;
  color: #666;
  font-size: 14px;
  line-height: 1.8;
}

.info-list li {
  margin-bottom: 8px;
}

.account-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.required {
  color: #ff4444;
}

.optional {
  color: #999;
  font-weight: 400;
}

.form-input {
  padding: 12px 14px;
  border: 1px solid #d0d0d0;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.3s ease;
}

.form-input:focus {
  outline: none;
  border-color: #0066cc;
  box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1);
}

.form-input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.form-hint {
  font-size: 12px;
  color: #999;
}

.amount-preview {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #e8f4ff;
  border-radius: 8px;
  border: 1px solid #b3d9ff;
}

.preview-label {
  font-size: 14px;
  color: #666;
}

.preview-amount {
  font-size: 20px;
  font-weight: 700;
  color: #0066cc;
}

.checkbox-group {
  margin-top: 8px;
}

.checkbox-label {
  display: flex;
  align-items: flex-start;
  font-size: 13px;
  color: #666;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  margin-right: 8px;
  margin-top: 2px;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"]:disabled {
  cursor: not-allowed;
}

.link {
  color: #0066cc;
  text-decoration: none;
  transition: color 0.2s;
}

.link:hover {
  color: #004499;
  text-decoration: underline;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.btn-primary,
.btn-secondary {
  flex: 1;
  padding: 14px 24px;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #0066cc 0%, #004499 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  box-shadow: 0 4px 12px rgba(0, 102, 204, 0.3);
  transform: translateY(-1px);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: white;
  color: #666;
  border: 1px solid #d0d0d0;
}

.btn-secondary:hover:not(:disabled) {
  border-color: #999;
  background: #f8f9fa;
}

.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .page-content {
    padding: 20px;
  }

  .form-actions {
    flex-direction: column;
  }

  .amount-preview {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>
