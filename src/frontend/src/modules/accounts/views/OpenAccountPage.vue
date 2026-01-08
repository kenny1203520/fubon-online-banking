<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAccountStore } from '@/modules/accounts/stores/account'
import Alert from '@/shared/Alert.vue'

const router = useRouter()
const accountStore = useAccountStore()

// 帳戶類型選項
const accountTypes = [
  { value: 'savings', label: '儲蓄帳戶', description: '適合日常存款，享有利息收益' },
  { value: 'checking', label: '支票帳戶', description: '適合頻繁交易，可開立支票' },
  { value: 'fixed_deposit', label: '定期存款帳戶', description: '高利率，適合長期儲蓄' },
  { value: 'foreign_currency', label: '外幣帳戶', description: '支持多種外幣存款，便於國際交易' }
]

// 表單資料
const form = ref({
  full_name: '',
  id_number: '',
  email: '',
  phone: '',
  address: '',
  account_type: 'savings' as 'savings' | 'checking' | 'fixed_deposit' | 'foreign_currency',
  initial_deposit: 1000
})

const isLoading = ref(false)
const error = ref<string | null>(null)
const success = ref<string | null>(null)
const successDetails = ref<{ accountNumber: string; accountName: string } | null>(null)
const agreedToTerms = ref(false)
const currentStep = ref(1)

// 計算欄位錯誤狀態
const fieldErrors = ref<Record<string, string>>({})

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

// 驗證手機號碼格式（台灣手機號碼）
const validatePhone = (phone: string): boolean => {
  const pattern = /^09\d{8}$/
  return pattern.test(phone)
}

// 即時驗證單個欄位
const validateField = (fieldName: string) => {
  delete fieldErrors.value[fieldName]
  
  switch (fieldName) {
    case 'full_name':
      if (!form.value.full_name) {
        fieldErrors.value.full_name = '請輸入姓名'
      } else if (form.value.full_name.length < 2) {
        fieldErrors.value.full_name = '姓名至少需要 2 個字元'
      }
      break
    case 'id_number':
      if (!form.value.id_number) {
        fieldErrors.value.id_number = '請輸入身分證號'
      } else if (!validateIdNumber(form.value.id_number)) {
        fieldErrors.value.id_number = '身分證號格式不正確'
      }
      break
    case 'email':
      if (form.value.email && !validateEmail(form.value.email)) {
        fieldErrors.value.email = '電子郵件格式不正確'
      }
      break
    case 'phone':
      if (!form.value.phone) {
        fieldErrors.value.phone = '請輸入手機號碼'
      } else if (!validatePhone(form.value.phone)) {
        fieldErrors.value.phone = '手機號碼格式不正確（應為09開頭的10碼數字）'
      }
      break
    case 'address':
      if (!form.value.address) {
        fieldErrors.value.address = '請輸入地址'
      } else if (form.value.address.length < 5) {
        fieldErrors.value.address = '地址至少需要 5 個字元'
      }
      break
  }
}

// 表單驗證
const validateForm = (): boolean => {
  fieldErrors.value = {}
  
  validateField('full_name')
  validateField('id_number')
  validateField('email')
  validateField('phone')
  validateField('address')

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

  return Object.keys(fieldErrors.value).length === 0
}

// 檢查步驟1是否完成
const isStep1Valid = computed(() => {
  return form.value.full_name.length >= 2 &&
         validateIdNumber(form.value.id_number) &&
         (!form.value.email || validateEmail(form.value.email))
})

// 檢查步驟2是否完成
const isStep2Valid = computed(() => {
  return validatePhone(form.value.phone) &&
         form.value.address.length >= 5
})

// 前往下一步
const nextStep = () => {
  if (currentStep.value === 1 && !isStep1Valid.value) {
    error.value = '請確認基本資料填寫正確'
    return
  }
  if (currentStep.value === 2 && !isStep2Valid.value) {
    error.value = '請確認聯絡資料填寫正確'
    return
  }
  error.value = null
  currentStep.value++
}

// 返回上一步
const prevStep = () => {
  error.value = null
  currentStep.value--
}

// 提交開戶申請
const handleSubmit = async () => {
  error.value = null
  success.value = null
  successDetails.value = null

  if (!validateForm()) {
    return
  }

  isLoading.value = true

  try {
    const result = await accountStore.openAccount({
      full_name: form.value.full_name,
      id_number: form.value.id_number,
      email: form.value.email || undefined,
      phone: form.value.phone,
      address: form.value.address,
      account_type: form.value.account_type,
      initial_deposit: form.value.initial_deposit
    })

    success.value = result.message
    successDetails.value = {
      accountNumber: result.account_number,
      accountName: result.account_name
    }
    
    // 清空表單
    form.value = {
      full_name: '',
      id_number: '',
      email: '',
      phone: '',
      address: '',
      account_type: 'savings',
      initial_deposit: 1000
    }
    agreedToTerms.value = false
    currentStep.value = 1

    // 3 秒後跳轉到帳戶列表
    setTimeout(() => {
      router.push('/accounts')
    }, 3000)
  } catch (err: any) {
    console.error('開戶錯誤詳情:', err)
    
    // 詳細錯誤處理
    if (err.response) {
      // 服務器返回錯誤
      const detail = err.response.data?.detail
      if (typeof detail === 'string') {
        error.value = detail
      } else if (Array.isArray(detail)) {
        // Pydantic 驗證錯誤
        error.value = detail.map((e: any) => `${e.loc.join('.')}: ${e.msg}`).join(', ')
      } else {
        error.value = `申請失敗 (${err.response.status}): ${JSON.stringify(err.response.data)}`
      }
    } else if (err.request) {
      // 請求發送但沒有收到響應
      error.value = '無法連接到服務器，請檢查網絡連接或確認後端服務是否已啟動'
    } else {
      // 其他錯誤
      error.value = err.message || '開戶申請失敗'
    }
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

// 格式化手機號碼輸入
const formatPhoneInput = () => {
  // 只保留數字
  form.value.phone = form.value.phone.replace(/\D/g, '')
}

// 獲取當前選擇的帳戶類型資訊
const selectedAccountType = computed(() => {
  return accountTypes.find(type => type.value === form.value.account_type)
})
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

    <!-- 步驟指示器 -->
    <div class="steps-indicator">
      <div class="step" :class="{ active: currentStep >= 1, completed: currentStep > 1 }">
        <div class="step-number">1</div>
        <div class="step-label">基本資料</div>
      </div>
      <div class="step-divider"></div>
      <div class="step" :class="{ active: currentStep >= 2, completed: currentStep > 2 }">
        <div class="step-number">2</div>
        <div class="step-label">聯絡資料</div>
      </div>
      <div class="step-divider"></div>
      <div class="step" :class="{ active: currentStep >= 3, completed: currentStep > 3 }">
        <div class="step-number">3</div>
        <div class="step-label">帳戶設定</div>
      </div>
      <div class="step-divider"></div>
      <div class="step" :class="{ active: currentStep >= 4 }">
        <div class="step-number">4</div>
        <div class="step-label">確認送出</div>
      </div>
    </div>

    <div class="page-content">
      <div class="form-container">
        <!-- 成功資訊 -->
        <Alert
          v-if="success"
          :message="success"
          type="success"
        />

        <!-- 成功詳情 -->
        <div v-if="successDetails" class="success-details">
          <h3>🎉 開戶申請已成功提交</h3>
          <div class="detail-item">
            <span class="detail-label">帳號：</span>
            <span class="detail-value">{{ successDetails.accountNumber }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">帳戶名稱：</span>
            <span class="detail-value">{{ successDetails.accountName }}</span>
          </div>
          <p class="detail-note">即將自動跳轉至帳戶列表...</p>
        </div>

        <!-- 錯誤資訊 -->
        <Alert
          v-if="error && !success"
          :message="error"
          type="error"
          @close="error = null"
        />

        <!-- 開戶說明 -->
        <div v-if="!success" class="info-section">
          <h3>📋 開戶須知</h3>
          <ul class="info-list">
            <li>請確保您提供的個人資料真實有效</li>
            <li>初始存款金額最低為 1,000 元</li>
            <li>申請提交後需等待審核，預計 1-3 個工作天完成審核</li>
            <li>您可以在帳戶列表中查看申請狀態</li>
          </ul>
        </div>

        <!-- 開戶表單 -->
        <form v-if="!success" class="account-form" @submit.prevent="handleSubmit">
          <!-- 步驟 1: 基本資料 -->
          <div v-show="currentStep === 1" class="form-step">
            <h2 class="step-title">基本資料</h2>
            
            <!-- 姓名 -->
            <div class="form-group" :class="{ error: fieldErrors.full_name }">
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
                @blur="validateField('full_name')"
              />
              <span v-if="fieldErrors.full_name" class="error-message">{{ fieldErrors.full_name }}</span>
              <span v-else class="form-hint">請輸入您的真實姓名</span>
            </div>

            <!-- 身分證號 -->
            <div class="form-group" :class="{ error: fieldErrors.id_number }">
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
                @blur="validateField('id_number')"
              />
              <span v-if="fieldErrors.id_number" class="error-message">{{ fieldErrors.id_number }}</span>
              <span v-else class="form-hint">格式：首位大寫英文字母 + 9 位數字</span>
            </div>

            <!-- 電子郵件 -->
            <div class="form-group" :class="{ error: fieldErrors.email }">
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
                @blur="validateField('email')"
              />
              <span v-if="fieldErrors.email" class="error-message">{{ fieldErrors.email }}</span>
              <span v-else class="form-hint">用於接收帳戶相關通知</span>
            </div>

            <div class="form-actions">
              <button type="button" class="btn-secondary" @click="goBack" :disabled="isLoading">
                取消
              </button>
              <button type="button" class="btn-primary" @click="nextStep" :disabled="!isStep1Valid || isLoading">
                下一步
              </button>
            </div>
          </div>

          <!-- 步驟 2: 聯絡資料 -->
          <div v-show="currentStep === 2" class="form-step">
            <h2 class="step-title">聯絡資料</h2>

            <!-- 手機號碼 -->
            <div class="form-group" :class="{ error: fieldErrors.phone }">
              <label for="phone" class="form-label">
                手機號碼 <span class="required">*</span>
              </label>
              <input
                id="phone"
                v-model="form.phone"
                type="tel"
                placeholder="0912345678"
                class="form-input"
                :disabled="isLoading"
                maxlength="10"
                @input="formatPhoneInput"
                @blur="validateField('phone')"
              />
              <span v-if="fieldErrors.phone" class="error-message">{{ fieldErrors.phone }}</span>
              <span v-else class="form-hint">請輸入09開頭的10碼手機號碼</span>
            </div>

            <!-- 地址 -->
            <div class="form-group" :class="{ error: fieldErrors.address }">
              <label for="address" class="form-label">
                聯絡地址 <span class="required">*</span>
              </label>
              <textarea
                id="address"
                v-model="form.address"
                placeholder="請輸入完整地址，例如：台北市信義區信義路五段7號"
                class="form-textarea"
                :disabled="isLoading"
                rows="3"
                maxlength="200"
                @blur="validateField('address')"
              ></textarea>
              <span v-if="fieldErrors.address" class="error-message">{{ fieldErrors.address }}</span>
              <span v-else class="form-hint">請輸入您的完整聯絡地址</span>
            </div>

            <div class="form-actions">
              <button type="button" class="btn-secondary" @click="prevStep" :disabled="isLoading">
                上一步
              </button>
              <button type="button" class="btn-primary" @click="nextStep" :disabled="!isStep2Valid || isLoading">
                下一步
              </button>
            </div>
          </div>

          <!-- 步驟 3: 帳戶設定 -->
          <div v-show="currentStep === 3" class="form-step">
            <h2 class="step-title">帳戶設定</h2>

            <!-- 帳戶類型 -->
            <div class="form-group">
              <label class="form-label">
                帳戶類型 <span class="required">*</span>
              </label>
              <div class="account-type-grid">
                <label
                  v-for="type in accountTypes"
                  :key="type.value"
                  class="account-type-card"
                  :class="{ selected: form.account_type === type.value }"
                >
                  <input
                    v-model="form.account_type"
                    type="radio"
                    :value="type.value"
                    :disabled="isLoading"
                    class="account-type-radio"
                  />
                  <div class="account-type-content">
                    <div class="account-type-label">{{ type.label }}</div>
                    <div class="account-type-description">{{ type.description }}</div>
                  </div>
                </label>
              </div>
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

            <div class="form-actions">
              <button type="button" class="btn-secondary" @click="prevStep" :disabled="isLoading">
                上一步
              </button>
              <button type="button" class="btn-primary" @click="nextStep" :disabled="isLoading">
                下一步
              </button>
            </div>
          </div>

          <!-- 步驟 4: 確認送出 -->
          <div v-show="currentStep === 4" class="form-step">
            <h2 class="step-title">確認資料</h2>

            <!-- 資料確認 -->
            <div class="confirmation-section">
              <div class="confirmation-group">
                <h3>基本資料</h3>
                <div class="confirmation-item">
                  <span class="confirmation-label">姓名：</span>
                  <span class="confirmation-value">{{ form.full_name }}</span>
                </div>
                <div class="confirmation-item">
                  <span class="confirmation-label">身分證號：</span>
                  <span class="confirmation-value">{{ form.id_number }}</span>
                </div>
                <div v-if="form.email" class="confirmation-item">
                  <span class="confirmation-label">電子郵件：</span>
                  <span class="confirmation-value">{{ form.email }}</span>
                </div>
              </div>

              <div class="confirmation-group">
                <h3>聯絡資料</h3>
                <div class="confirmation-item">
                  <span class="confirmation-label">手機號碼：</span>
                  <span class="confirmation-value">{{ form.phone }}</span>
                </div>
                <div class="confirmation-item">
                  <span class="confirmation-label">聯絡地址：</span>
                  <span class="confirmation-value">{{ form.address }}</span>
                </div>
              </div>

              <div class="confirmation-group">
                <h3>帳戶設定</h3>
                <div class="confirmation-item">
                  <span class="confirmation-label">帳戶類型：</span>
                  <span class="confirmation-value">{{ selectedAccountType?.label }}</span>
                </div>
                <div class="confirmation-item">
                  <span class="confirmation-label">初始存款：</span>
                  <span class="confirmation-value highlight">
                    {{ new Intl.NumberFormat('zh-TW', { style: 'currency', currency: 'TWD', minimumFractionDigits: 0 }).format(form.initial_deposit) }}
                  </span>
                </div>
              </div>
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

            <div class="form-actions">
              <button type="button" class="btn-secondary" @click="prevStep" :disabled="isLoading">
                上一步
              </button>
              <button
                type="submit"
                class="btn-primary"
                :disabled="isLoading || !agreedToTerms"
              >
                <span v-if="!isLoading">✓ 確認提交申請</span>
                <span v-else>處理中...</span>
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-wrapper {
  padding: 20px;
  max-width: 900px;
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

/* 步驟指示器 */
.steps-indicator {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 32px;
  padding: 0 20px;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  flex: 0 0 auto;
}

.step-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #e0e0e0;
  color: #999;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 16px;
  transition: all 0.3s;
}

.step.active .step-number {
  background: #0066cc;
  color: white;
}

.step.completed .step-number {
  background: #28a745;
  color: white;
}

.step-label {
  font-size: 12px;
  color: #999;
  font-weight: 500;
  white-space: nowrap;
}

.step.active .step-label {
  color: #0066cc;
  font-weight: 600;
}

.step.completed .step-label {
  color: #28a745;
}

.step-divider {
  flex: 1;
  height: 2px;
  background: #e0e0e0;
  margin: 0 12px;
  margin-bottom: 28px;
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

.success-details {
  background: #d4edda;
  border: 1px solid #c3e6cb;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
}

.success-details h3 {
  margin: 0 0 16px 0;
  color: #155724;
  font-size: 18px;
}

.detail-item {
  display: flex;
  margin-bottom: 12px;
  font-size: 14px;
}

.detail-label {
  color: #155724;
  font-weight: 600;
  min-width: 100px;
}

.detail-value {
  color: #155724;
  font-family: monospace;
  font-size: 15px;
}

.detail-note {
  margin: 16px 0 0 0;
  color: #155724;
  font-size: 13px;
  font-style: italic;
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
}

.form-step {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.step-title {
  font-size: 20px;
  color: #333;
  margin: 0 0 24px 0;
  padding-bottom: 12px;
  border-bottom: 2px solid #e0e0e0;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 24px;
}

.form-group.error .form-input,
.form-group.error .form-textarea {
  border-color: #dc3545;
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

.form-input,
.form-textarea {
  padding: 12px 14px;
  border: 1px solid #d0d0d0;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.3s ease;
  font-family: inherit;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #0066cc;
  box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1);
}

.form-input:disabled,
.form-textarea:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.form-hint {
  font-size: 12px;
  color: #999;
}

.error-message {
  font-size: 12px;
  color: #dc3545;
  font-weight: 500;
}

/* 帳戶類型選擇 */
.account-type-grid {
  display: grid;
  gap: 16px;
}

.account-type-card {
  display: flex;
  padding: 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  background: white;
}

.account-type-card:hover {
  border-color: #0066cc;
  background: #f8f9fa;
}

.account-type-card.selected {
  border-color: #0066cc;
  background: #e8f4ff;
}

.account-type-radio {
  margin-right: 12px;
  cursor: pointer;
  flex-shrink: 0;
  margin-top: 2px;
}

.account-type-content {
  flex: 1;
}

.account-type-label {
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
  font-size: 15px;
}

.account-type-description {
  font-size: 13px;
  color: #666;
  line-height: 1.4;
}

.amount-preview {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #e8f4ff;
  border-radius: 8px;
  border: 1px solid #b3d9ff;
  margin-bottom: 16px;
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

/* 確認資料區塊 */
.confirmation-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
  margin-bottom: 24px;
}

.confirmation-group {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.confirmation-group h3 {
  margin: 0 0 16px 0;
  color: #0066cc;
  font-size: 16px;
  font-weight: 600;
  padding-bottom: 8px;
  border-bottom: 1px solid #e0e0e0;
}

.confirmation-item {
  display: flex;
  margin-bottom: 12px;
  font-size: 14px;
}

.confirmation-item:last-child {
  margin-bottom: 0;
}

.confirmation-label {
  color: #666;
  font-weight: 500;
  min-width: 100px;
}

.confirmation-value {
  color: #333;
  flex: 1;
}

.confirmation-value.highlight {
  color: #0066cc;
  font-weight: 700;
  font-size: 16px;
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
  flex-shrink: 0;
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
  margin-top: 24px;
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
  .page-wrapper {
    padding: 16px;
  }

  .page-content {
    padding: 20px;
  }

  .steps-indicator {
    padding: 0;
  }

  .step-label {
    font-size: 10px;
  }

  .step-number {
    width: 32px;
    height: 32px;
    font-size: 14px;
  }

  .step-divider {
    margin: 0 6px;
    margin-bottom: 22px;
  }

  .form-actions {
    flex-direction: column;
  }

  .amount-preview {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .confirmation-item {
    flex-direction: column;
    gap: 4px;
  }

  .confirmation-label {
    min-width: auto;
  }
}
</style>
