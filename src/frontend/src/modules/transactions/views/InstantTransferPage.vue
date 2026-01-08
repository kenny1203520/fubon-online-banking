<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useTransactionStore } from '../stores/transaction'
import { useAccountStore } from '@/modules/accounts/stores/account'
import type { TransferRequest } from '../types'
import { TAIWAN_BANKS, validateAccountNumber, formatAccountNumber, isInternalBank, type BankInfo, getBankByCode } from '../constants/banks'

const router = useRouter()
const transactionStore = useTransactionStore()
const accountStore = useAccountStore()

// Form data
const form = ref<TransferRequest>({
  from_account_id: undefined,
  from_account_number: '',
  to_account_number: '',
  amount: 0,
  currency: 'TWD',
  description: '',
  transfer_type: 'internal'
})

// Bank selection
const selectedBank = ref<string>('012') // 預設富邦銀行
const accountNumber = ref<string>('') // 分行代碼+帳號 (不含銀行代碼)

// UI state
const isSubmitting = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const showConfirmDialog = ref(false)

// Computed
const selectedAccount = computed(() => 
  accountStore.accounts.find(a => a.id === form.value.from_account_id)
)

const selectedBankInfo = computed<BankInfo | undefined>(() => 
  TAIWAN_BANKS.find(b => b.code === selectedBank.value)
)

const transferFee = computed(() => {
  // 本行轉帳免手續費，跨行轉帳收15元
  return isInternalBank(selectedBank.value) ? 0 : 15
})

const totalAmount = computed(() => form.value.amount + transferFee.value)

const isAccountNumberValid = computed(() => {
  if (!accountNumber.value) return false
  return validateAccountNumber(selectedBank.value, accountNumber.value)
})

const isFormValid = computed(() => {
  return form.value.from_account_id 
    && selectedBank.value
    && isAccountNumberValid.value
    && form.value.amount > 0
    && selectedAccount.value
    && totalAmount.value <= selectedAccount.value.balance
})

const errorText = computed(() => {
  if (!form.value.from_account_id) return '請選擇轉出帳戶'
  if (!selectedBank.value) return '請選擇收款銀行'
  if (!accountNumber.value) return '請輸入收款帳號'
  if (!isAccountNumberValid.value) return '帳號格式不正確（應為分行代碼3碼+帳號6碼，共9碼數字）'
  if (form.value.amount <= 0) return '請輸入有效的轉帳金額'
  if (selectedAccount.value && totalAmount.value > selectedAccount.value.balance) {
    return '帳戶餘額不足'
  }
  return ''
})

const fullAccountNumber = computed(() => {
  if (!selectedBank.value || !accountNumber.value) return ''
  return formatAccountNumber(selectedBank.value, accountNumber.value)
})

// Methods
const loadAccounts = async () => {
  try {
    await accountStore.fetchAccounts()
    if (accountStore.accounts.length > 0) {
      form.value.from_account_id = accountStore.accounts[0]?.id
    }
  } catch (error) {
    console.error('Failed to load accounts:', error)
    errorMessage.value = '載入帳戶失敗'
  }
}

const handleSubmit = () => {
  if (!isFormValid.value) {
    errorMessage.value = errorText.value
    return
  }
  
  // 設定完整的收款帳號 (銀行代碼-分行代碼-帳號)
  form.value.to_account_number = fullAccountNumber.value
  
  // 設定轉帳類型 (本行或跨行)
  form.value.transfer_type = isInternalBank(selectedBank.value) ? 'internal' : 'other'
  
  showConfirmDialog.value = true
}

const confirmTransfer = async () => {
  if (!isFormValid.value) return

  isSubmitting.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    await transactionStore.createTransfer(form.value)
    successMessage.value = '轉帳成功！'
    showConfirmDialog.value = false
    
    // Reset form
    form.value = {
      from_account_id: accountStore.accounts[0]?.id,
      from_account_number: accountStore.accounts[0]?.account_number,
      to_account_number: '',
      amount: 0,
      currency: 'TWD',
      description: '',
      transfer_type: 'internal'
    }
    selectedBank.value = '012'
    accountNumber.value = ''

    // Reload accounts to update balance
    await loadAccounts()
  } catch (error) {
    const apiError = error as { response?: { data?: { message?: string } } }
    errorMessage.value = apiError.response?.data?.message || '轉帳失敗，請稍後再試'
  } finally {
    isSubmitting.value = false
  }
}

const cancelTransfer = () => {
  showConfirmDialog.value = false
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('zh-TW', {
    style: 'currency',
    currency: 'TWD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount)
}

// 監聽帳號輸入，自動識別銀行代碼
watch(accountNumber, (newValue) => {
  // 移除所有非數字字符和分隔符號
  const cleaned = newValue.replace(/[^0-9]/g, '')
  
  // 如果輸入超過14碼（可能包含銀行代碼），嘗試解析
  if (cleaned.length > 14) {
    const possibleBankCode = cleaned.substring(0, 3)
    const bank = getBankByCode(possibleBankCode)
    
    if (bank) {
      // 找到有效的銀行代碼
      selectedBank.value = possibleBankCode
    }
  }
  // 如果以 3 碼數字開頭且後面有連字號，也嘗試解析
  else if (/^\d{3}[-]/.test(newValue)) {
    const possibleBankCode = cleaned.substring(0, 3)
    const bank = getBankByCode(possibleBankCode)
    
    if (bank) {
      // 找到有效的銀行代碼
      selectedBank.value = possibleBankCode
    }
  }
})

onMounted(() => {
  loadAccounts()
})
</script>

<template>
  <div class="transfer-page">
    <!-- Header -->
    <div class="page-header">
      <h1 class="page-title">即時轉帳</h1>
      <p class="page-subtitle">快速、安全的即時轉帳服務</p>
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions">
      <button class="action-btn" @click="router.push('/transactions/scheduled')">
        <span class="icon">⏰</span>
        <span>預約轉帳</span>
      </button>
      <button class="action-btn" @click="router.push('/transactions/history')">
        <span class="icon">📋</span>
        <span>交易紀錄</span>
      </button>
    </div>

    <!-- Alert Messages -->
    <div v-if="errorMessage" class="alert alert-error">
      <span class="alert-icon">❌</span>
      <span>{{ errorMessage }}</span>
    </div>

    <div v-if="successMessage" class="alert alert-success">
      <span class="alert-icon">✅</span>
      <span>{{ successMessage }}</span>
    </div>

    <!-- Transfer Form -->
    <div class="transfer-form-container">
      <div class="form-card">
        <h2 class="form-title">轉帳資訊</h2>

        <form @submit.prevent="handleSubmit">
          <!-- From Account -->
          <div class="form-group">
            <label class="form-label" for="from-account">轉出帳戶</label>
            <select 
              id="from-account"
              v-model="form.from_account_id" 
              class="form-select"
              required
            >
              <option :value="undefined" disabled>請選擇轉出帳戶</option>
              <option 
                v-for="account in accountStore.accounts" 
                :key="account.id"
                :value="account.id"
              >
                {{ account.account_name }} ({{ account.account_number }}) - 
                餘額: {{ formatCurrency(account.balance) }}
              </option>
            </select>
            <div v-if="selectedAccount" class="account-info">
              <span>可用餘額：{{ formatCurrency(selectedAccount.balance) }}</span>
            </div>
          </div>

          <!-- Bank Selection -->
          <div class="form-group">
            <label class="form-label" for="bank-select">收款銀行</label>
            <select 
              id="bank-select"
              v-model="selectedBank" 
              class="form-select"
              required
            >
              <option 
                v-for="bank in TAIWAN_BANKS" 
                :key="bank.code"
                :value="bank.code"
              >
                {{ bank.code }} - {{ bank.name }}
              </option>
            </select>
            <div v-if="selectedBankInfo" class="bank-info">
              <span v-if="isInternalBank(selectedBank)" class="badge badge-success">本行轉帳 · 免手續費</span>
              <span v-else class="badge badge-warning">跨行轉帳 · 手續費 {{ formatCurrency(transferFee) }}</span>
            </div>
          </div>

          <!-- Account Number -->
          <div class="form-group">
            <label class="form-label" for="account-number">收款帳號</label>
            <input 
              id="account-number"
              v-model="accountNumber"
              type="text"
              class="form-input"
              placeholder="請輸入分行代碼及帳號 (例: 12345678901)"
              maxlength="9"
              required
            >
            <div class="input-hint">
              <span v-if="!accountNumber">格式：分行代碼(3碼) + 帳號(6碼)，例: 525-947586</span>
              <span v-else-if="!isAccountNumberValid" class="text-error">❌ 帳號格式不正確</span>
              <span v-else class="text-success">✓ 完整帳號：{{ fullAccountNumber }}</span>
            </div>
          </div>

          <!-- Amount -->
          <div class="form-group">
            <label class="form-label" for="amount">轉帳金額</label>
            <div class="amount-input-wrapper">
              <span class="currency-symbol">NT$</span>
              <input 
                id="amount"
                v-model.number="form.amount"
                type="number"
                class="form-input amount-input"
                placeholder="0"
                min="1"
                step="1"
                required
              >
            </div>
          </div>

          <!-- Description -->
          <div class="form-group">
            <label class="form-label" for="description">備註說明（選填）</label>
            <textarea 
              id="description"
              v-model="form.description"
              class="form-textarea"
              placeholder="請輸入備註說明"
              rows="3"
              maxlength="100"
            ></textarea>
          </div>

          <!-- Summary -->
          <div class="transfer-summary">
            <div class="summary-row">
              <span class="summary-label">轉帳金額</span>
              <span class="summary-value">{{ formatCurrency(form.amount) }}</span>
            </div>
            <div class="summary-row">
              <span class="summary-label">手續費</span>
              <span class="summary-value">{{ formatCurrency(transferFee) }}</span>
            </div>
            <div class="summary-row total">
              <span class="summary-label">總計金額</span>
              <span class="summary-value">{{ formatCurrency(totalAmount) }}</span>
            </div>
          </div>

          <!-- Submit Button -->
          <button 
            type="submit" 
            class="btn btn-primary btn-block"
            :disabled="!isFormValid || isSubmitting"
          >
            {{ isSubmitting ? '處理中...' : '確認轉帳' }}
          </button>
        </form>
      </div>
    </div>

    <!-- Confirmation Dialog -->
    <div v-if="showConfirmDialog" class="modal-overlay" @click.self="cancelTransfer">
      <div class="modal-content">
        <h3 class="modal-title">確認轉帳資訊</h3>
        
        <div class="confirm-details">
          <div class="detail-row">
            <span class="detail-label">轉出帳戶</span>
            <span class="detail-value">{{ selectedAccount?.account_number }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">收款銀行</span>
            <span class="detail-value">{{ selectedBankInfo?.name }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">收款帳號</span>
            <span class="detail-value">{{ fullAccountNumber }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">轉帳金額</span>
            <span class="detail-value">{{ formatCurrency(form.amount) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">手續費</span>
            <span class="detail-value">{{ formatCurrency(transferFee) }}</span>
          </div>
          <div class="detail-row total">
            <span class="detail-label">總計金額</span>
            <span class="detail-value">{{ formatCurrency(totalAmount) }}</span>
          </div>
          <div v-if="form.description" class="detail-row">
            <span class="detail-label">備註</span>
            <span class="detail-value">{{ form.description }}</span>
          </div>
        </div>

        <div class="modal-actions">
          <button 
            class="btn btn-secondary" 
            @click="cancelTransfer"
            :disabled="isSubmitting"
          >
            取消
          </button>
          <button 
            class="btn btn-primary" 
            @click="confirmTransfer"
            :disabled="isSubmitting"
          >
            {{ isSubmitting ? '處理中...' : '確認' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.transfer-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 8px;
}

.page-subtitle {
  font-size: 16px;
  color: #666;
}

/* Quick Actions */
.quick-actions {
  display: flex;
  gap: 16px;
  margin-bottom: 30px;
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-btn:hover {
  border-color: #0066cc;
  background: #f0f7ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 102, 204, 0.1);
}

.action-btn .icon {
  font-size: 24px;
}

/* Alerts */
.alert {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.alert-error {
  background: #fff5f5;
  color: #c53030;
  border: 1px solid #feb2b2;
}

.alert-success {
  background: #f0fff4;
  color: #22543d;
  border: 1px solid #9ae6b4;
}

.alert-icon {
  font-size: 20px;
}

/* Form */
.transfer-form-container {
  margin-bottom: 30px;
}

.form-card {
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.form-title {
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 24px;
}

.form-group {
  margin-bottom: 24px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 12px 16px;
  font-size: 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #0066cc;
  box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1);
}

.form-textarea {
  resize: vertical;
  font-family: inherit;
}

.account-info, .bank-info {
  margin-top: 8px;
  font-size: 14px;
  color: #666;
}

.input-hint {
  margin-top: 8px;
  font-size: 13px;
  color: #666;
}

.text-error {
  color: #c53030;
}

.text-success {
  color: #22543d;
}

/* Badge */
.badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 500;
}

.badge-success {
  background: #f0fff4;
  color: #22543d;
}

.badge-warning {
  background: #fffaf0;
  color: #c05621;
}

/* Amount Input */
.amount-input-wrapper {
  position: relative;
}

.currency-symbol {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 16px;
  font-weight: 500;
  color: #666;
}

.amount-input {
  padding-left: 48px;
  font-size: 18px;
  font-weight: 600;
}

/* Summary */
.transfer-summary {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 24px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.summary-row.total {
  border-top: 2px solid #e0e0e0;
  margin-top: 8px;
  padding-top: 16px;
  font-weight: 600;
  font-size: 18px;
}

.summary-label {
  color: #666;
}

.summary-value {
  color: #1a1a1a;
  font-weight: 500;
}

/* Buttons */
.btn {
  padding: 14px 24px;
  font-size: 16px;
  font-weight: 500;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #0066cc 0%, #004499 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 102, 204, 0.3);
}

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-secondary {
  background: white;
  color: #333;
  border: 1px solid #e0e0e0;
}

.btn-secondary:hover {
  background: #f8f9fa;
}

.btn-block {
  width: 100%;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 16px;
  padding: 32px;
  max-width: 500px;
  width: 100%;
}

.modal-title {
  font-size: 22px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 24px;
}

.confirm-details {
  margin-bottom: 24px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.detail-row.total {
  border-bottom: none;
  border-top: 2px solid #e0e0e0;
  margin-top: 8px;
  padding-top: 16px;
  font-weight: 600;
  font-size: 18px;
}

.detail-label {
  color: #666;
  font-size: 14px;
}

.detail-value {
  color: #1a1a1a;
  font-weight: 500;
}

.modal-actions {
  display: flex;
  gap: 12px;
}

.modal-actions .btn {
  flex: 1;
}

/* Responsive */
@media (max-width: 768px) {
  .transfer-page {
    padding: 16px;
  }

  .form-card {
    padding: 20px;
  }

  .quick-actions {
    flex-direction: column;
  }
}
</style>
