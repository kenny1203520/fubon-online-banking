<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useCreditCardStore } from '@/modules/creditcards/stores/creditcard'
import type { CardApplicationRequest } from '@/modules/creditcards/types'
import Alert from '@/shared/Alert.vue'

const router = useRouter()
const creditCardStore = useCreditCardStore()

// 信用卡類型選項
const cardTypes = [
  {
    value: 'visa_classic',
    name: 'Visa 經典卡',
    brand: 'visa',
    icon: '💳',
    color: '#1A1F71',
    benefits: [
      '國內消費現金回饋 0.5%',
      '海外消費現金回饋 1.0%',
      '免年費（首年）',
      '24小時客服服務'
    ],
    requirements: {
      minIncome: 200000,
      description: '年收入需達 20 萬元以上'
    }
  },
  {
    value: 'visa_gold',
    name: 'Visa 金卡',
    brand: 'visa',
    icon: '💎',
    color: '#FFD700',
    benefits: [
      '國內消費現金回饋 1.0%',
      '海外消費現金回饋 2.0%',
      '機場貴賓室免費使用（每年4次）',
      '旅遊不便險最高 100 萬',
      '購物保障險最高 30 萬'
    ],
    requirements: {
      minIncome: 500000,
      description: '年收入需達 50 萬元以上'
    }
  },
  {
    value: 'mastercard_titanium',
    name: 'Mastercard 鈦金卡',
    brand: 'mastercard',
    icon: '🌟',
    color: '#EB001B',
    benefits: [
      '國內消費現金回饋 1.2%',
      '海外消費現金回饋 2.5%',
      '無限次機場貴賓室',
      '旅遊不便險最高 300 萬',
      '購物保障險最高 100 萬',
      '道路救援服務'
    ],
    requirements: {
      minIncome: 800000,
      description: '年收入需達 80 萬元以上'
    }
  },
  {
    value: 'jcb_platinum',
    name: 'JCB 白金卡',
    brand: 'jcb',
    icon: '✨',
    color: '#006DB7',
    benefits: [
      '日本消費現金回饋 3.0%',
      '其他地區現金回饋 1.5%',
      '日本機場免稅店優惠',
      'JCB Plaza 禮賓服務',
      '免費旅遊保險'
    ],
    requirements: {
      minIncome: 600000,
      description: '年收入需達 60 萬元以上'
    }
  },
  {
    value: 'amex_gold',
    name: 'American Express 金卡',
    brand: 'amex',
    icon: '🏆',
    color: '#006FCF',
    benefits: [
      '精選餐廳消費回饋 3.0%',
      '旅遊消費回饋 2.0%',
      '其他消費回饋 1.0%',
      '全球機場貴賓室',
      '精選飯店升等優惠',
      '24小時旅遊支援服務'
    ],
    requirements: {
      minIncome: 700000,
      description: '年收入需達 70 萬元以上'
    }
  }
]

// 就業狀態選項
const employmentStatusOptions = [
  { value: 'employed', label: '受僱員工' },
  { value: 'self-employed', label: '自營商/自由業' },
  { value: 'unemployed', label: '待業中' },
  { value: 'retired', label: '退休' }
]

// 表單資料
const form = ref({
  full_name: '',
  id_number: '',
  annual_income: 300000,
  card_type: '',
  employment_status: 'employed' as 'employed' | 'self-employed' | 'unemployed' | 'retired',
  company_name: '',
  position: ''
})

const currentStep = ref(1)
const isLoading = ref(false)
const error = ref<string | null>(null)
const success = ref<string | null>(null)
const successDetails = ref<{ applicationId: number; cardName: string } | null>(null)

// 計算欄位錯誤
const fieldErrors = ref<Record<string, string>>({})

// 驗證台灣身分證號格式與校驗碼
const validateIdNumber = (idNumber: string): boolean => {
  // 檢查基本格式：首位英文字母，第二位為1或2，後面8位數字，最後1位校驗碼
  const pattern = /^[A-Z][12]\d{8}$/
  if (!pattern.test(idNumber)) {
    return false
  }

  // 驗證校驗碼（台灣身分證號算法）
  // 英文字母對應編號：A=10, B=11, ..., Z=35
  const letterCode = idNumber.charCodeAt(0) - 64 + 9
  const digits = `${letterCode}${idNumber.substring(1)}`
  
  // 計算權重和
  let sum = Math.floor(letterCode / 10) + (letterCode % 10) * 9
  for (let i = 0; i < 9; i++) {
    sum += parseInt(digits[i + 1]) * (9 - i)
  }
  
  // 校驗碼應該是使總和 % 10 = 0
  const checksum = (10 - (sum % 10)) % 10
  const providedChecksum = parseInt(idNumber[9])
  
  return checksum === providedChecksum
}

// 驗證單個欄位
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
      } else if (!/^[A-Z][12]\d{8}$/.test(form.value.id_number)) {
        fieldErrors.value.id_number = '身分證號格式不正確（應為：一個大寫英文字母+1或2+8位數字）'
      } else if (!validateIdNumber(form.value.id_number)) {
        fieldErrors.value.id_number = '身分證號校驗失敗，請確認輸入無誤'
      }
      break
    case 'company_name':
      if (form.value.employment_status === 'employed' && !form.value.company_name) {
        fieldErrors.value.company_name = '請輸入公司名稱'
      }
      break
  }
}

// 獲取選中的卡片資訊
const selectedCard = computed(() => {
  return cardTypes.find(card => card.value === form.value.card_type)
})

// 檢查收入是否符合要求
const incomeRequirementMet = computed(() => {
  if (!selectedCard.value) return false
  return form.value.annual_income >= selectedCard.value.requirements.minIncome
})

// 檢查步驟1是否完成
const isStep1Valid = computed(() => {
  return !!form.value.card_type
})

// 檢查步驟2是否完成
const isStep2Valid = computed(() => {
  return form.value.full_name.length >= 2 &&
         validateIdNumber(form.value.id_number) &&
         form.value.annual_income >= 100000 &&
         incomeRequirementMet.value &&
         (form.value.employment_status !== 'employed' || form.value.company_name.length > 0)
})

// 前往下一步
const nextStep = () => {
  if (currentStep.value === 1 && !isStep1Valid.value) {
    error.value = '請選擇一張信用卡'
    return
  }
  if (currentStep.value === 2 && !isStep2Valid.value) {
    error.value = '請確認所有資料填寫正確'
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

// 選擇卡片
const selectCard = (cardValue: string) => {
  form.value.card_type = cardValue
  error.value = null
}

// 提交申請
const handleSubmit = async () => {
  error.value = null
  success.value = null
  successDetails.value = null

  if (!isStep2Valid.value) {
    error.value = '請確認所有資料填寫正確'
    return
  }

  isLoading.value = true

  try {
    const applicationData: CardApplicationRequest = {
      card_type: form.value.card_type,
      annual_income: form.value.annual_income,
      employment_status: form.value.employment_status,
      company_name: form.value.company_name || undefined,
      position: form.value.position || undefined
    }
    
    const result = await creditCardStore.applyCard(applicationData)

    success.value = result.message
    successDetails.value = {
      applicationId: result.application_id,
      cardName: selectedCard.value?.name || '信用卡'
    }

    // 清空表單
    form.value = {
      full_name: '',
      id_number: '',
      annual_income: 300000,
      card_type: '',
      employment_status: 'employed',
      company_name: '',
      position: ''
    }
    currentStep.value = 1

    // 3秒後跳轉
    setTimeout(() => {
      router.push('/cards')
    }, 3000)
  } catch (err: any) {
    console.error('申請錯誤:', err)
    error.value = err.message || '信用卡申請失敗'
  } finally {
    isLoading.value = false
  }
}

// 返回列表
const goBack = () => {
  router.push('/cards')
}

// 格式化收入輸入
const formatIncomeInput = () => {
  if (form.value.annual_income < 0) {
    form.value.annual_income = 0
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
        <h1>申請信用卡</h1>
        <p>選擇適合您的信用卡並完成申請</p>
      </div>
    </div>

    <!-- 步驟指示器 -->
    <div class="steps-indicator">
      <div class="step" :class="{ active: currentStep >= 1, completed: currentStep > 1 }">
        <div class="step-number">1</div>
        <div class="step-label">選擇卡片</div>
      </div>
      <div class="step-divider"></div>
      <div class="step" :class="{ active: currentStep >= 2, completed: currentStep > 2 }">
        <div class="step-number">2</div>
        <div class="step-label">填寫資料</div>
      </div>
      <div class="step-divider"></div>
      <div class="step" :class="{ active: currentStep >= 3 }">
        <div class="step-number">3</div>
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
          <h3>🎉 信用卡申請已成功提交</h3>
          <div class="detail-item">
            <span class="detail-label">申請編號：</span>
            <span class="detail-value">{{ successDetails.applicationId }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">卡片類型：</span>
            <span class="detail-value">{{ successDetails.cardName }}</span>
          </div>
          <p class="detail-note">我們將在 3-5 個工作天內完成審核，結果將以簡訊通知您。</p>
        </div>

        <!-- 錯誤資訊 -->
        <Alert
          v-if="error && !success"
          :message="error"
          type="error"
          @close="error = null"
        />

        <!-- 申請表單 -->
        <form v-if="!success" class="card-form" @submit.prevent="handleSubmit">
          <!-- 步驟 1: 選擇卡片 -->
          <div v-show="currentStep === 1" class="form-step">
            <h2 class="step-title">選擇信用卡類型</h2>
            
            <div class="info-banner">
              <span class="info-icon">ℹ️</span>
              <div>
                <strong>選擇最適合您的信用卡</strong>
                <p>每張卡片都有不同的權益和年收入要求，請仔細比較後選擇。</p>
              </div>
            </div>

            <div class="card-grid">
              <div
                v-for="card in cardTypes"
                :key="card.value"
                class="card-option"
                :class="{ selected: form.card_type === card.value }"
                @click="selectCard(card.value)"
              >
                <div class="card-icon" :style="{ color: card.color }">{{ card.icon }}</div>
                <h3 class="card-name">{{ card.name }}</h3>
                <div class="card-brand">{{ card.brand.toUpperCase() }}</div>
                
                <div class="card-benefits">
                  <div class="benefit-label">權益特色</div>
                  <ul>
                    <li v-for="(benefit, index) in card.benefits" :key="index">
                      {{ benefit }}
                    </li>
                  </ul>
                </div>

                <div class="card-requirement">
                  <span class="requirement-icon">💰</span>
                  {{ card.requirements.description }}
                </div>

                <div class="card-check" v-if="form.card_type === card.value">
                  <span class="check-icon">✓</span>
                </div>
              </div>
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

          <!-- 步驟 2: 填寫資料 -->
          <div v-show="currentStep === 2" class="form-step">
            <h2 class="step-title">填寫申請資料</h2>

            <div v-if="selectedCard" class="selected-card-preview">
              <div class="preview-icon" :style="{ color: selectedCard.color }">{{ selectedCard.icon }}</div>
              <div class="preview-info">
                <div class="preview-name">{{ selectedCard.name }}</div>
                <div class="preview-requirement">{{ selectedCard.requirements.description }}</div>
              </div>
            </div>

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
              <span v-else class="form-hint">請輸入與身分證相同的姓名</span>
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

            <!-- 年收入 -->
            <div class="form-group" :class="{ error: !incomeRequirementMet }">
              <label for="annual_income" class="form-label">
                年收入（元） <span class="required">*</span>
              </label>
              <input
                id="annual_income"
                v-model.number="form.annual_income"
                type="number"
                placeholder="請輸入年收入"
                class="form-input"
                :disabled="isLoading"
                min="0"
                step="10000"
                @input="formatIncomeInput"
              />
              <span v-if="!incomeRequirementMet && form.annual_income > 0" class="error-message">
                年收入需達 {{ new Intl.NumberFormat('zh-TW').format(selectedCard?.requirements.minIncome || 0) }} 元以上
              </span>
              <span v-else-if="incomeRequirementMet" class="success-message">
                ✓ 符合申請條件
              </span>
              <span v-else class="form-hint">此卡片要求最低年收入：{{ new Intl.NumberFormat('zh-TW').format(selectedCard?.requirements.minIncome || 0) }} 元</span>
            </div>

            <!-- 就業狀態 -->
            <div class="form-group">
              <label class="form-label">
                就業狀態 <span class="required">*</span>
              </label>
              <div class="radio-group">
                <label
                  v-for="option in employmentStatusOptions"
                  :key="option.value"
                  class="radio-label"
                >
                  <input
                    v-model="form.employment_status"
                    type="radio"
                    :value="option.value"
                    :disabled="isLoading"
                  />
                  <span>{{ option.label }}</span>
                </label>
              </div>
            </div>

            <!-- 公司名稱 -->
            <div v-if="form.employment_status === 'employed'" class="form-group" :class="{ error: fieldErrors.company_name }">
              <label for="company_name" class="form-label">
                公司名稱 <span class="required">*</span>
              </label>
              <input
                id="company_name"
                v-model="form.company_name"
                type="text"
                placeholder="請輸入公司名稱"
                class="form-input"
                :disabled="isLoading"
                @blur="validateField('company_name')"
              />
              <span v-if="fieldErrors.company_name" class="error-message">{{ fieldErrors.company_name }}</span>
            </div>

            <!-- 職位 -->
            <div v-if="form.employment_status === 'employed'" class="form-group">
              <label for="position" class="form-label">
                職位 <span class="optional">(選填)</span>
              </label>
              <input
                id="position"
                v-model="form.position"
                type="text"
                placeholder="請輸入職位"
                class="form-input"
                :disabled="isLoading"
              />
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

          <!-- 步驟 3: 確認送出 -->
          <div v-show="currentStep === 3" class="form-step">
            <h2 class="step-title">確認申請資料</h2>

            <!-- 卡片資訊 -->
            <div v-if="selectedCard" class="confirmation-section">
              <div class="confirmation-card">
                <div class="card-preview" :style="{ borderColor: selectedCard.color }">
                  <div class="card-preview-icon" :style="{ color: selectedCard.color }">
                    {{ selectedCard.icon }}
                  </div>
                  <div class="card-preview-name">{{ selectedCard.name }}</div>
                  <div class="card-preview-brand">{{ selectedCard.brand.toUpperCase() }}</div>
                </div>
              </div>

              <div class="confirmation-group">
                <h3>申請人資料</h3>
                <div class="confirmation-item">
                  <span class="confirmation-label">姓名：</span>
                  <span class="confirmation-value">{{ form.full_name }}</span>
                </div>
                <div class="confirmation-item">
                  <span class="confirmation-label">身分證號：</span>
                  <span class="confirmation-value">{{ form.id_number }}</span>
                </div>
                <div class="confirmation-item">
                  <span class="confirmation-label">年收入：</span>
                  <span class="confirmation-value highlight">
                    {{ new Intl.NumberFormat('zh-TW', { style: 'currency', currency: 'TWD', minimumFractionDigits: 0 }).format(form.annual_income) }}
                  </span>
                </div>
              </div>

              <div class="confirmation-group">
                <h3>就業資訊</h3>
                <div class="confirmation-item">
                  <span class="confirmation-label">就業狀態：</span>
                  <span class="confirmation-value">
                    {{ employmentStatusOptions.find(opt => opt.value === form.employment_status)?.label }}
                  </span>
                </div>
                <div v-if="form.company_name" class="confirmation-item">
                  <span class="confirmation-label">公司名稱：</span>
                  <span class="confirmation-value">{{ form.company_name }}</span>
                </div>
                <div v-if="form.position" class="confirmation-item">
                  <span class="confirmation-label">職位：</span>
                  <span class="confirmation-value">{{ form.position }}</span>
                </div>
              </div>
            </div>

            <div class="notice-section">
              <h4>📋 申請須知</h4>
              <ul>
                <li>請確保提供的資料真實有效</li>
                <li>審核期間約 3-5 個工作天</li>
                <li>審核結果將以簡訊通知</li>
                <li>核卡後將以掛號方式寄送卡片</li>
              </ul>
            </div>

            <div class="form-actions">
              <button type="button" class="btn-secondary" @click="prevStep" :disabled="isLoading">
                上一步
              </button>
              <button
                type="submit"
                class="btn-primary"
                :disabled="isLoading"
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
  justify-content: center;
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
  flex: 0 0 60px;
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
  max-width: 900px;
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

.card-form {
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

.info-banner {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  background: #e8f4ff;
  border: 1px solid #b3d9ff;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
}

.info-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.info-banner strong {
  color: #0066cc;
  display: block;
  margin-bottom: 4px;
}

.info-banner p {
  margin: 0;
  color: #666;
  font-size: 13px;
  line-height: 1.5;
}

/* 卡片選擇網格 */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.card-option {
  position: relative;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s;
  background: white;
}

.card-option:hover {
  border-color: #0066cc;
  box-shadow: 0 4px 12px rgba(0, 102, 204, 0.1);
  transform: translateY(-2px);
}

.card-option.selected {
  border-color: #0066cc;
  background: #f8fbff;
  box-shadow: 0 4px 16px rgba(0, 102, 204, 0.2);
}

.card-icon {
  font-size: 48px;
  text-align: center;
  margin-bottom: 12px;
}

.card-name {
  font-size: 18px;
  font-weight: 700;
  color: #333;
  margin: 0 0 4px 0;
  text-align: center;
}

.card-brand {
  text-align: center;
  font-size: 11px;
  font-weight: 600;
  color: #999;
  letter-spacing: 1px;
  margin-bottom: 16px;
}

.card-benefits {
  margin-bottom: 16px;
}

.benefit-label {
  font-size: 12px;
  font-weight: 600;
  color: #666;
  margin-bottom: 8px;
}

.card-benefits ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.card-benefits li {
  font-size: 12px;
  color: #666;
  padding: 4px 0;
  padding-left: 16px;
  position: relative;
  line-height: 1.4;
}

.card-benefits li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: #28a745;
  font-weight: bold;
}

.card-requirement {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px;
  background: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 6px;
  font-size: 12px;
  color: #856404;
  font-weight: 500;
}

.requirement-icon {
  font-size: 16px;
}

.card-check {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #0066cc;
  display: flex;
  align-items: center;
  justify-content: center;
}

.check-icon {
  color: white;
  font-size: 18px;
  font-weight: bold;
}

/* 選中卡片預覽 */
.selected-card-preview {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #f8fbff;
  border: 2px solid #0066cc;
  border-radius: 8px;
  margin-bottom: 24px;
}

.preview-icon {
  font-size: 40px;
}

.preview-info {
  flex: 1;
}

.preview-name {
  font-size: 18px;
  font-weight: 700;
  color: #333;
  margin-bottom: 4px;
}

.preview-requirement {
  font-size: 13px;
  color: #666;
}

/* 表單樣式 */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 24px;
}

.form-group.error .form-input {
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

.form-input {
  padding: 12px 14px;
  border: 1px solid #d0d0d0;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.3s ease;
  font-family: inherit;
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

.error-message {
  font-size: 12px;
  color: #dc3545;
  font-weight: 500;
}

.success-message {
  font-size: 12px;
  color: #28a745;
  font-weight: 500;
}

.radio-group {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #333;
}

.radio-label input[type="radio"] {
  cursor: pointer;
}

/* 確認資料區塊 */
.confirmation-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
  margin-bottom: 24px;
}

.confirmation-card {
  display: flex;
  justify-content: center;
  margin-bottom: 8px;
}

.card-preview {
  width: 320px;
  height: 200px;
  border-radius: 16px;
  border: 3px solid;
  background: linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.card-preview-icon {
  font-size: 64px;
}

.card-preview-name {
  font-size: 20px;
  font-weight: 700;
  color: #333;
}

.card-preview-brand {
  font-size: 12px;
  font-weight: 600;
  color: #666;
  letter-spacing: 2px;
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

.notice-section {
  background: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 24px;
}

.notice-section h4 {
  margin: 0 0 12px 0;
  color: #856404;
  font-size: 15px;
}

.notice-section ul {
  margin: 0;
  padding-left: 20px;
  color: #856404;
  font-size: 13px;
  line-height: 1.8;
}

.notice-section li {
  margin-bottom: 6px;
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

  .card-grid {
    grid-template-columns: 1fr;
  }

  .card-preview {
    width: 100%;
    max-width: 320px;
  }

  .form-actions {
    flex-direction: column;
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
