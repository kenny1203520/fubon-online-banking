<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useLoanStore } from '@/modules/loans/stores/loan'
import { useAuthStore } from '@/modules/auth/stores/auth'
import type { Loan, LoanCalculation, RepaymentSchedule, RepaymentHistory } from '@/modules/loans/types'
import Alert from '@/shared/Alert.vue'

const loanStore = useLoanStore()
const authStore = useAuthStore()

// 當前視圖
const currentView = ref<'list' | 'calculator' | 'apply' | 'detail'>('list')
const selectedLoan = ref<Loan | null>(null)

// 切換到申請頁面時檢查登入狀態
const goToApplyPage = () => {
  if (!authStore.isAuthenticated) {
    alert('請先登入才能申請貸款！點擊右上角登入按鈕。')
    return
  }
  currentView.value = 'apply'
}

// 貸款試算表單
const calculatorForm = ref({
  amount: 500000,
  interestRate: 3.5,
  termMonths: 36
})

const calculationResult = ref<LoanCalculation | null>(null)
const isCalculating = ref(false)
const calculatorError = ref<string | null>(null)

// 申請貸款表單
const applicationForm = ref({
  loanAmount: 500000,
  termMonths: 36,
  purpose: '',
  employmentStatus: 'employed' as 'employed' | 'self-employed' | 'unemployed' | 'retired',
  annualIncome: 600000,
  companyName: '',
  yearsEmployed: 1,
  hasCollateral: false,
  collateralDescription: ''
})

const isApplying = ref(false)
const applicationError = ref<string | null>(null)
const applicationSuccess = ref<string | null>(null)

// 還款計劃和歷史
const repaymentSchedule = ref<RepaymentSchedule[]>([])
const repaymentHistory = ref<RepaymentHistory[]>([])
const isLoadingSchedule = ref(false)
const isLoadingHistory = ref(false)

// 就業狀態選項
const employmentOptions = [
  { value: 'employed', label: '受僱員工' },
  { value: 'self-employed', label: '自營商/自由業' },
  { value: 'unemployed', label: '待業中' },
  { value: 'retired', label: '退休' }
]

// 貸款期限選項
const termOptions = [
  { value: 12, label: '1年 (12期)' },
  { value: 24, label: '2年 (24期)' },
  { value: 36, label: '3年 (36期)' },
  { value: 48, label: '4年 (48期)' },
  { value: 60, label: '5年 (60期)' },
  { value: 84, label: '7年 (84期)' }
]

// 載入貸款列表
onMounted(async () => {
  try {
    await loanStore.fetchMyLoans()
  } catch (error) {
    console.error('載入貸款列表失敗:', error)
  }
})

// 進行貸款試算
const calculateLoan = async () => {
  calculatorError.value = null
  calculationResult.value = null

  if (calculatorForm.value.amount < 10000) {
    calculatorError.value = '貸款金額至少需要 10,000 元'
    return
  }

  if (calculatorForm.value.amount > 5000000) {
    calculatorError.value = '貸款金額不可超過 5,000,000 元'
    return
  }

  isCalculating.value = true
  console.log('開始計算貸款', {
    amount: calculatorForm.value.amount,
    rate: calculatorForm.value.interestRate,
    months: calculatorForm.value.termMonths
  })

  try {
    const result = await loanStore.calculateLoan(
      calculatorForm.value.amount,
      calculatorForm.value.interestRate,
      calculatorForm.value.termMonths
    )
    console.log('計算結果:', result)
    calculationResult.value = result
  } catch (error: any) {
    console.error('計算失敗:', error)
    calculatorError.value = error.message || '計算失敗'
  } finally {
    isCalculating.value = false
  }
}

// 提交貸款申請
const submitApplication = async () => {
  applicationError.value = null
  applicationSuccess.value = null

  // 檢查登入狀態
  if (!authStore.isAuthenticated) {
    applicationError.value = '請先登入才能申請貸款'
    return
  }

  if (!applicationForm.value.purpose) {
    applicationError.value = '請填寫貸款用途'
    return
  }

  if (applicationForm.value.employmentStatus === 'employed' && !applicationForm.value.companyName) {
    applicationError.value = '請填寫公司名稱'
    return
  }

  isApplying.value = true
  console.log('開始申請貸款', applicationForm.value)

  try {
    const result = await loanStore.applyLoan({
      product_id: undefined,
      loan_amount: applicationForm.value.loanAmount,
      term_months: applicationForm.value.termMonths,
      purpose: applicationForm.value.purpose,
      employment_status: applicationForm.value.employmentStatus,
      annual_income: applicationForm.value.annualIncome,
      company_name: applicationForm.value.companyName || undefined,
      years_employed: applicationForm.value.yearsEmployed || undefined,
      has_collateral: applicationForm.value.hasCollateral,
      collateral_description: applicationForm.value.collateralDescription || undefined
    })

    console.log('申請結果:', result)
    applicationSuccess.value = result.message
    
    // 重新載入貸款列表
    await loanStore.fetchMyLoans()
    
    // 3秒後返回列表
    setTimeout(() => {
      currentView.value = 'list'
      applicationSuccess.value = null
      resetApplicationForm()
    }, 3000)
  } catch (error: any) {
    console.error('申請失敗:', error)
    applicationError.value = error.message || '申請失敗'
  } finally {
    isApplying.value = false
  }
}

// 重置申請表單
const resetApplicationForm = () => {
  applicationForm.value = {
    loanAmount: 500000,
    termMonths: 36,
    purpose: '',
    employmentStatus: 'employed',
    annualIncome: 600000,
    companyName: '',
    yearsEmployed: 1,
    hasCollateral: false,
    collateralDescription: ''
  }
}

// 查看貸款詳情
const viewLoanDetail = async (loan: Loan) => {
  selectedLoan.value = loan
  currentView.value = 'detail'
  
  // 載入還款計劃和歷史
  if (loan.status === 'active' || loan.status === 'approved') {
    isLoadingSchedule.value = true
    try {
      repaymentSchedule.value = await loanStore.getRepaymentSchedule(loan.id)
    } catch (error) {
      console.error('載入還款計劃失敗:', error)
    } finally {
      isLoadingSchedule.value = false
    }
  }
  
  isLoadingHistory.value = true
  try {
    repaymentHistory.value = await loanStore.getRepaymentHistory(loan.id)
  } catch (error) {
    console.error('載入還款記錄失敗:', error)
  } finally {
    isLoadingHistory.value = false
  }
}

// 返回列表
const backToList = () => {
  currentView.value = 'list'
  selectedLoan.value = null
  calculationResult.value = null
  applicationSuccess.value = null
  applicationError.value = null
  calculatorError.value = null
}

// 格式化金額
const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('zh-TW', {
    style: 'currency',
    currency: 'TWD',
    minimumFractionDigits: 0
  }).format(amount)
}

// 格式化日期
const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

// 取得狀態標籤
const getStatusLabel = (status: string) => {
  const statusMap: Record<string, string> = {
    'pending': '審核中',
    'approved': '已核准',
    'active': '撥款中',
    'paid_off': '已清償',
    'rejected': '已拒絕'
  }
  return statusMap[status] || status
}

// 取得狀態類別
const getStatusClass = (status: string) => {
  const classMap: Record<string, string> = {
    'pending': 'status-pending',
    'approved': 'status-approved',
    'active': 'status-active',
    'paid_off': 'status-paid',
    'rejected': 'status-rejected'
  }
  return classMap[status] || ''
}
</script>

<template>
  <div class="page-wrapper">
    <!-- 列表視圖 -->
    <div v-if="currentView === 'list'" class="list-view">
      <div class="page-header">
        <div>
          <h1>貸款服務</h1>
          <p>管理您的貸款申請和還款</p>
        </div>
        <div class="header-actions">
          <button class="btn-secondary" @click="currentView = 'calculator'">
            🧮 貸款試算
          </button>
          <button class="btn-primary" @click="goToApplyPage()">
            + 申請貸款
          </button>
        </div>
      </div>

      <div class="page-content">
        <!-- 貸款列表 -->
        <div v-if="loanStore.myLoans.length > 0" class="loans-grid">
          <div
            v-for="loan in loanStore.myLoans"
            :key="loan.id"
            class="loan-card"
            @click="viewLoanDetail(loan)"
          >
            <div class="loan-card-header">
              <div>
                <h3>{{ loan.product_name || '個人信貸' }}</h3>
                <span :class="['status-badge', getStatusClass(loan.status)]">
                  {{ getStatusLabel(loan.status) }}
                </span>
              </div>
              <div class="loan-icon">💰</div>
            </div>

            <div class="loan-details">
              <div class="detail-row">
                <span class="label">貸款金額</span>
                <span class="value">{{ formatCurrency(loan.loan_amount) }}</span>
              </div>
              <div class="detail-row">
                <span class="label">年利率</span>
                <span class="value">{{ loan.interest_rate }}%</span>
              </div>
              <div class="detail-row">
                <span class="label">貸款期限</span>
                <span class="value">{{ loan.term_months }} 個月</span>
              </div>
              <div class="detail-row">
                <span class="label">月付金額</span>
                <span class="value highlight">{{ formatCurrency(loan.monthly_payment) }}</span>
              </div>
              <div class="detail-row">
                <span class="label">剩餘本金</span>
                <span class="value">{{ formatCurrency(loan.remaining_balance) }}</span>
              </div>
            </div>

            <div v-if="loan.next_payment_date" class="next-payment">
              <span class="next-label">下次還款日：</span>
              <span class="next-date">{{ formatDate(loan.next_payment_date) }}</span>
            </div>
          </div>
        </div>

        <!-- 空狀態 -->
        <div v-else class="empty-state">
          <div class="empty-icon">💰</div>
          <h3>尚無貸款記錄</h3>
          <p>您還沒有申請任何貸款</p>
          <div class="empty-actions">
            <button class="btn-secondary" @click="currentView = 'calculator'">
              先試算看看
            </button>
            <button class="btn-primary" @click="goToApplyPage()">
              立即申請貸款
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 貸款試算視圖 -->
    <div v-else-if="currentView === 'calculator'" class="calculator-view">
      <div class="page-header">
        <button class="btn-back" @click="backToList">
          ← 返回列表
        </button>
        <div>
          <h1>貸款試算</h1>
          <p>計算您的月付金額和總利息</p>
        </div>
      </div>

      <div class="page-content">
        <div class="calculator-container">
          <div class="calculator-form">
            <h3>試算參數</h3>

            <Alert v-if="calculatorError" :message="calculatorError" type="error" @close="calculatorError = null" />

            <div class="form-group">
              <label class="form-label">
                貸款金額（元）
                <span class="current-value">{{ formatCurrency(calculatorForm.amount) }}</span>
              </label>
              <input
                v-model.number="calculatorForm.amount"
                type="range"
                min="10000"
                max="5000000"
                step="10000"
                class="range-input"
              />
              <div class="range-labels">
                <span>1萬</span>
                <span>500萬</span>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">
                年利率（%）
                <span class="current-value">{{ calculatorForm.interestRate }}%</span>
              </label>
              <input
                v-model.number="calculatorForm.interestRate"
                type="range"
                min="0"
                max="15"
                step="0.1"
                class="range-input"
              />
              <div class="range-labels">
                <span>0%</span>
                <span>15%</span>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">貸款期限</label>
              <select v-model.number="calculatorForm.termMonths" class="form-select">
                <option v-for="option in termOptions" :key="option.value" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
            </div>

            <button class="btn-primary btn-full" @click="calculateLoan" :disabled="isCalculating">
              <span v-if="!isCalculating">💡 開始試算</span>
              <span v-else>計算中...</span>
            </button>
          </div>

          <div v-if="calculationResult" class="calculation-result">
            <h3>試算結果</h3>
            <div class="result-grid">
              <div class="result-item primary">
                <div class="result-label">每月應繳</div>
                <div class="result-value">{{ formatCurrency(calculationResult.monthly_payment) }}</div>
              </div>
              <div class="result-item">
                <div class="result-label">貸款總額</div>
                <div class="result-value">{{ formatCurrency(calculationResult.loan_amount) }}</div>
              </div>
              <div class="result-item">
                <div class="result-label">總支付金額</div>
                <div class="result-value">{{ formatCurrency(calculationResult.total_payment) }}</div>
              </div>
              <div class="result-item">
                <div class="result-label">總利息</div>
                <div class="result-value">{{ formatCurrency(calculationResult.total_interest) }}</div>
              </div>
            </div>

            <button class="btn-primary btn-full" @click="goToApplyPage()">
              確定金額，前往申請
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 申請貸款視圖 -->
    <div v-else-if="currentView === 'apply'" class="apply-view">
      <div class="page-header">
        <button class="btn-back" @click="backToList">
          ← 返回列表
        </button>
        <div>
          <h1>申請貸款</h1>
          <p>填寫申請資料</p>
        </div>
      </div>

      <div class="page-content">
        <div class="apply-container">
          <Alert v-if="!authStore.isAuthenticated" message="⚠️ 請先登入才能申請貸款！點擊右上角登入按鈕。" type="warning" />
          <Alert v-if="applicationSuccess" :message="applicationSuccess" type="success" />
          <Alert v-if="applicationError" :message="applicationError" type="error" @close="applicationError = null" />

          <form v-if="!applicationSuccess" @submit.prevent="submitApplication" class="apply-form">
            <h3>貸款資訊</h3>

            <div class="form-row">
              <div class="form-group">
                <label class="form-label">貸款金額（元） *</label>
                <input
                  v-model.number="applicationForm.loanAmount"
                  type="number"
                  class="form-input"
                  min="10000"
                  max="5000000"
                  step="10000"
                  required
                />
              </div>

              <div class="form-group">
                <label class="form-label">貸款期限 *</label>
                <select v-model.number="applicationForm.termMonths" class="form-select" required>
                  <option v-for="option in termOptions" :key="option.value" :value="option.value">
                    {{ option.label }}
                  </option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">貸款用途 *</label>
              <textarea
                v-model="applicationForm.purpose"
                class="form-textarea"
                rows="3"
                placeholder="例如：購買汽車、房屋裝修、子女教育等"
                required
              ></textarea>
            </div>

            <h3>財務資訊</h3>

            <div class="form-group">
              <label class="form-label">就業狀態 *</label>
              <div class="radio-group">
                <label
                  v-for="option in employmentOptions"
                  :key="option.value"
                  class="radio-label"
                >
                  <input
                    v-model="applicationForm.employmentStatus"
                    type="radio"
                    :value="option.value"
                  />
                  <span>{{ option.label }}</span>
                </label>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label class="form-label">年收入（元） *</label>
                <input
                  v-model.number="applicationForm.annualIncome"
                  type="number"
                  class="form-input"
                  min="0"
                  step="10000"
                  required
                />
              </div>

              <div v-if="applicationForm.employmentStatus === 'employed'" class="form-group">
                <label class="form-label">任職年資（年）</label>
                <input
                  v-model.number="applicationForm.yearsEmployed"
                  type="number"
                  class="form-input"
                  min="0"
                  max="50"
                />
              </div>
            </div>

            <div v-if="applicationForm.employmentStatus === 'employed'" class="form-group">
              <label class="form-label">公司名稱 *</label>
              <input
                v-model="applicationForm.companyName"
                type="text"
                class="form-input"
                required
              />
            </div>

            <h3>擔保品資訊（選填）</h3>

            <div class="form-group">
              <label class="checkbox-label">
                <input
                  v-model="applicationForm.hasCollateral"
                  type="checkbox"
                />
                <span>我有提供擔保品（可降低利率）</span>
              </label>
            </div>

            <div v-if="applicationForm.hasCollateral" class="form-group">
              <label class="form-label">擔保品說明</label>
              <textarea
                v-model="applicationForm.collateralDescription"
                class="form-textarea"
                rows="3"
                placeholder="請描述擔保品類型和價值"
              ></textarea>
            </div>

            <div class="info-box">
              <h4>📋 申請須知</h4>
              <ul>
                <li>審核期間約 3-5 個工作天</li>
                <li>利率將根據您的信用評分和財務狀況決定</li>
                <li>核准後將以簡訊和電子郵件通知您</li>
                <li>年收入越高，核准機率越大且利率越低</li>
              </ul>
            </div>

            <div class="form-actions">
              <button type="button" class="btn-secondary" @click="backToList" :disabled="isApplying">
                取消
              </button>
              <button type="submit" class="btn-primary" :disabled="isApplying">
                <span v-if="!isApplying">✓ 提交申請</span>
                <span v-else>處理中...</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 貸款詳情視圖 -->
    <div v-else-if="currentView === 'detail' && selectedLoan" class="detail-view">
      <div class="page-header">
        <button class="btn-back" @click="backToList">
          ← 返回列表
        </button>
        <div>
          <h1>貸款詳情</h1>
          <p>{{ selectedLoan.product_name || '個人信貸' }}</p>
        </div>
      </div>

      <div class="page-content">
        <div class="detail-container">
          <!-- 貸款基本資訊 -->
          <div class="detail-card">
            <h3>
              基本資訊
              <span :class="['status-badge', getStatusClass(selectedLoan.status)]">
                {{ getStatusLabel(selectedLoan.status) }}
              </span>
            </h3>
            <div class="detail-grid">
              <div class="detail-item">
                <span class="label">貸款編號</span>
                <span class="value">#{{ selectedLoan.id }}</span>
              </div>
              <div class="detail-item">
                <span class="label">貸款金額</span>
                <span class="value">{{ formatCurrency(selectedLoan.loan_amount) }}</span>
              </div>
              <div class="detail-item">
                <span class="label">年利率</span>
                <span class="value">{{ selectedLoan.interest_rate }}%</span>
              </div>
              <div class="detail-item">
                <span class="label">貸款期限</span>
                <span class="value">{{ selectedLoan.term_months }} 個月</span>
              </div>
              <div class="detail-item">
                <span class="label">月付金額</span>
                <span class="value highlight">{{ formatCurrency(selectedLoan.monthly_payment) }}</span>
              </div>
              <div class="detail-item">
                <span class="label">剩餘本金</span>
                <span class="value">{{ formatCurrency(selectedLoan.remaining_balance) }}</span>
              </div>
              <div class="detail-item">
                <span class="label">申請日期</span>
                <span class="value">{{ formatDate(selectedLoan.application_date) }}</span>
              </div>
              <div class="detail-item" v-if="selectedLoan.next_payment_date">
                <span class="label">下次還款日</span>
                <span class="value">{{ formatDate(selectedLoan.next_payment_date) }}</span>
              </div>
            </div>
          </div>

          <!-- 還款計劃 -->
          <div v-if="repaymentSchedule.length > 0" class="detail-card">
            <h3>還款計劃</h3>
            <div v-if="isLoadingSchedule" class="loading">載入中...</div>
            <div v-else class="table-container">
              <table class="schedule-table">
                <thead>
                  <tr>
                    <th>期數</th>
                    <th>還款日期</th>
                    <th>本金</th>
                    <th>利息</th>
                    <th>應繳金額</th>
                    <th>剩餘本金</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in repaymentSchedule.slice(0, 12)" :key="item.payment_number">
                    <td>{{ item.payment_number }}</td>
                    <td>{{ formatDate(item.payment_date) }}</td>
                    <td>{{ formatCurrency(item.principal) }}</td>
                    <td>{{ formatCurrency(item.interest) }}</td>
                    <td class="highlight">{{ formatCurrency(item.total_payment) }}</td>
                    <td>{{ formatCurrency(item.remaining_balance) }}</td>
                  </tr>
                </tbody>
              </table>
              <div v-if="repaymentSchedule.length > 12" class="table-note">
                僅顯示前 12 期，共 {{ repaymentSchedule.length }} 期
              </div>
            </div>
          </div>

          <!-- 還款記錄 -->
          <div class="detail-card">
            <h3>還款記錄</h3>
            <div v-if="isLoadingHistory" class="loading">載入中...</div>
            <div v-else-if="repaymentHistory.length > 0" class="table-container">
              <table class="history-table">
                <thead>
                  <tr>
                    <th>還款日期</th>
                    <th>繳款金額</th>
                    <th>本金</th>
                    <th>利息</th>
                    <th>剩餘本金</th>
                    <th>付款方式</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in repaymentHistory" :key="item.id">
                    <td>{{ formatDate(item.payment_date) }}</td>
                    <td class="highlight">{{ formatCurrency(item.amount) }}</td>
                    <td>{{ formatCurrency(item.principal) }}</td>
                    <td>{{ formatCurrency(item.interest) }}</td>
                    <td>{{ formatCurrency(item.remaining_balance) }}</td>
                    <td>{{ item.payment_method || '-' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-else class="empty-message">
              尚無還款記錄
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
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  flex-wrap: wrap;
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

.header-actions {
  display: flex;
  gap: 12px;
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

.btn-primary,
.btn-secondary {
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  font-size: 15px;
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

.btn-full {
  width: 100%;
  padding: 16px;
  font-size: 16px;
}

.page-content {
  background: white;
  padding: 32px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

/* 貸款卡片網格 */
.loans-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.loan-card {
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s;
  background: white;
}

.loan-card:hover {
  border-color: #0066cc;
  box-shadow: 0 4px 12px rgba(0, 102, 204, 0.1);
  transform: translateY(-2px);
}

.loan-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.loan-card-header h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  color: #333;
}

.loan-icon {
  font-size: 36px;
  opacity: 0.8;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.status-pending {
  background: #fff3cd;
  color: #856404;
}

.status-approved {
  background: #d1ecf1;
  color: #0c5460;
}

.status-active {
  background: #d4edda;
  color: #155724;
}

.status-paid {
  background: #e2e3e5;
  color: #383d41;
}

.status-rejected {
  background: #f8d7da;
  color: #721c24;
}

.loan-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
}

.detail-row .label {
  color: #666;
}

.detail-row .value {
  font-weight: 600;
  color: #333;
}

.detail-row .value.highlight {
  color: #0066cc;
  font-size: 16px;
}

.next-payment {
  padding-top: 16px;
  border-top: 1px solid #e0e0e0;
  font-size: 13px;
}

.next-label {
  color: #666;
}

.next-date {
  font-weight: 600;
  color: #ff6b6b;
  margin-left: 8px;
}

/* 空狀態 */
.empty-state {
  text-align: center;
  padding: 60px 40px;
}

.empty-icon {
  font-size: 80px;
  opacity: 0.5;
  margin-bottom: 20px;
}

.empty-state h3 {
  margin: 0 0 12px 0;
  color: #333;
  font-size: 20px;
}

.empty-state p {
  margin: 0 0 24px 0;
  color: #999;
  font-size: 14px;
}

.empty-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

/* 試算器 */
.calculator-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
}

.calculator-form,
.calculation-result {
  background: #f8f9fa;
  padding: 24px;
  border-radius: 8px;
}

.calculator-form h3,
.calculation-result h3 {
  margin: 0 0 24px 0;
  color: #333;
  font-size: 18px;
}

.form-group {
  margin-bottom: 24px;
}

.form-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.current-value {
  color: #0066cc;
  font-size: 16px;
}

.range-input {
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: #d0d0d0;
  outline: none;
  -webkit-appearance: none;
  appearance: none;
}

.range-input::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #0066cc;
  cursor: pointer;
}

.range-input::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #0066cc;
  cursor: pointer;
}

.range-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 12px;
  color: #999;
}

.form-select,
.form-input,
.form-textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #d0d0d0;
  border-radius: 4px;
  font-size: 14px;
  font-family: inherit;
}

.form-select:focus,
.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #0066cc;
  box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1);
}

.result-grid {
  display: grid;
  gap: 16px;
  margin-bottom: 24px;
}

.result-item {
  background: white;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
}

.result-item.primary {
  background: linear-gradient(135deg, #0066cc 0%, #004499 100%);
  color: white;
}

.result-item.primary .result-label,
.result-item.primary .result-value {
  color: white;
}

.result-label {
  font-size: 13px;
  color: #666;
  margin-bottom: 8px;
}

.result-value {
  font-size: 24px;
  font-weight: 700;
  color: #333;
}

/* 申請表單 */
.apply-container {
  max-width: 800px;
  margin: 0 auto;
}

.apply-form h3 {
  margin: 32px 0 24px 0;
  padding-bottom: 12px;
  border-bottom: 2px solid #e0e0e0;
  color: #333;
  font-size: 18px;
}

.apply-form h3:first-child {
  margin-top: 0;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
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

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #333;
}

.checkbox-label input[type="checkbox"] {
  cursor: pointer;
  width: 18px;
  height: 18px;
}

.info-box {
  background: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 8px;
  padding: 20px;
  margin: 24px 0;
}

.info-box h4 {
  margin: 0 0 12px 0;
  color: #856404;
  font-size: 15px;
}

.info-box ul {
  margin: 0;
  padding-left: 20px;
  color: #856404;
  font-size: 13px;
  line-height: 1.8;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 32px;
}

.form-actions .btn-primary,
.form-actions .btn-secondary {
  flex: 1;
}

/* 詳情視圖 */
.detail-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.detail-card {
  background: #f8f9fa;
  padding: 24px;
  border-radius: 8px;
}

.detail-card h3 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 18px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-item .label {
  font-size: 13px;
  color: #666;
}

.detail-item .value {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.detail-item .value.highlight {
  font-size: 18px;
  color: #0066cc;
}

/* 表格 */
.table-container {
  overflow-x: auto;
}

.schedule-table,
.history-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.schedule-table th,
.history-table th {
  background: #e0e0e0;
  padding: 12px;
  text-align: left;
  font-weight: 600;
  color: #333;
}

.schedule-table td,
.history-table td {
  padding: 12px;
  border-bottom: 1px solid #e0e0e0;
  color: #666;
}

.schedule-table td.highlight,
.history-table td.highlight {
  font-weight: 600;
  color: #0066cc;
}

.table-note {
  margin-top: 12px;
  font-size: 13px;
  color: #999;
  text-align: center;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #999;
}

.empty-message {
  text-align: center;
  padding: 40px;
  color: #999;
  font-size: 14px;
}

@media (max-width: 1024px) {
  .calculator-container {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .page-wrapper {
    padding: 16px;
  }

  .page-content {
    padding: 20px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
    flex-direction: column;
  }

  .header-actions button {
    width: 100%;
  }

  .loans-grid {
    grid-template-columns: 1fr;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
