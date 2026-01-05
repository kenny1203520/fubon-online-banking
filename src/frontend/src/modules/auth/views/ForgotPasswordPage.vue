<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/modules/auth/stores/auth'
import Alert from '@/shared/Alert.vue'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const isLoading = ref(false)
const error = ref<string | null>(null)
const success = ref<string | null>(null)
const isSubmitted = ref(false)

const validateEmail = (email: string): boolean => {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

const handleResetPassword = async () => {
  error.value = null
  success.value = null

  if (!email.value) {
    error.value = '請輸入電子郵件地址'
    return
  }

  if (!validateEmail(email.value)) {
    error.value = '請輸入有效的電子郵件地址'
    return
  }

  isLoading.value = true

  try {
    await authStore.resetPassword(email.value)
    success.value = '重設密碼連結已發送至您的電子郵件，請查收'
    isSubmitted.value = true
  } catch (err) {
    error.value = err instanceof Error ? err.message : '發送失敗，請重試'
  } finally {
    isLoading.value = false
  }
}

const handleBackToLogin = () => {
  router.push('/login')
}

const handleResend = () => {
  isSubmitted.value = false
  success.value = null
  error.value = null
}
</script>

<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <h1 class="bank-title">富邦網路銀行</h1>
        <p class="subtitle">重設密碼</p>
      </div>

      <!-- 未提交狀態 -->
      <form v-if="!isSubmitted" class="auth-form" @submit.prevent="handleResetPassword">
        <!-- 錯誤訊息 -->
        <Alert
          v-if="error"
          :message="error"
          type="error"
          @close="error = null"
        />

        <p class="instruction">
          請輸入您註冊時使用的電子郵件地址，我們將發送重設密碼連結到您的信箱。
        </p>

        <!-- 電子郵件輸入 -->
        <div class="form-group">
          <label for="email" class="form-label">電子郵件</label>
          <input
            id="email"
            v-model="email"
            type="email"
            placeholder="請輸入電子郵件地址"
            class="form-input"
            :disabled="isLoading"
          />
        </div>

        <!-- 提交按鈕 -->
        <button
          type="submit"
          class="btn-reset"
          :disabled="isLoading || !email"
        >
          <span v-if="!isLoading">發送重設連結</span>
          <span v-else>發送中...</span>
        </button>
      </form>

      <!-- 已提交狀態 -->
      <div v-else class="success-message">
        <Alert
          :message="success || ''"
          type="success"
        />

        <div class="success-actions">
          <p class="instruction">
            如果您在幾分鐘內未收到郵件，請檢查您的垃圾郵件資料夾。
          </p>
          
          <button
            type="button"
            class="btn-resend"
            @click="handleResend"
            :disabled="isLoading"
          >
            重新發送
          </button>
        </div>
      </div>

      <!-- 返回登入 -->
      <div class="auth-links">
        <button type="button" class="link-button" @click="handleBackToLogin" :disabled="isLoading">
          ← 返回登入
        </button>
      </div>
    </div>

    <!-- 背景裝飾 -->
    <div class="background-decoration"></div>
  </div>
</template>

<style scoped>
.auth-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0066cc 0%, #004499 100%);
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.background-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  opacity: 0.1;
  background-image: radial-gradient(circle at 20% 50%, #fff 0%, transparent 50%),
                    radial-gradient(circle at 80% 80%, #fff 0%, transparent 50%);
  pointer-events: none;
}

.auth-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  padding: 40px;
  width: 100%;
  max-width: 480px;
  position: relative;
  z-index: 1;
}

.auth-header {
  text-align: center;
  margin-bottom: 30px;
}

.bank-title {
  font-size: 28px;
  font-weight: 700;
  color: #0066cc;
  margin: 0 0 8px 0;
  letter-spacing: 1px;
}

.subtitle {
  color: #999;
  font-size: 14px;
  margin: 0;
}

.auth-form {
  margin-bottom: 24px;
}

.instruction {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin-bottom: 24px;
  text-align: center;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.form-input {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid #d0d0d0;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.3s ease;
  box-sizing: border-box;
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

.btn-reset,
.btn-resend {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #0066cc 0%, #004499 100%);
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  letter-spacing: 0.5px;
}

.btn-reset:hover:not(:disabled),
.btn-resend:hover:not(:disabled) {
  box-shadow: 0 4px 12px rgba(0, 102, 204, 0.3);
  transform: translateY(-1px);
}

.btn-reset:disabled,
.btn-resend:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.success-message {
  margin-bottom: 24px;
}

.success-actions {
  margin-top: 24px;
}

.btn-resend {
  margin-top: 16px;
}

.auth-links {
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 13px;
}

.link-button {
  background: none;
  border: none;
  color: #0066cc;
  cursor: pointer;
  font-size: 13px;
  padding: 8px;
  text-decoration: none;
  transition: color 0.2s;
}

.link-button:hover:not(:disabled) {
  color: #004499;
  text-decoration: underline;
}

.link-button:disabled {
  color: #ccc;
  cursor: not-allowed;
}

@media (max-width: 480px) {
  .auth-card {
    padding: 30px 20px;
  }

  .bank-title {
    font-size: 24px;
  }
}
</style>
