<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/modules/auth/stores/auth'
import Alert from '@/shared/Alert.vue'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const email = ref('')
const phone = ref('')
const isLoading = ref(false)
const error = ref<string | null>(null)
const success = ref<string | null>(null)
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const agreedToTerms = ref(false)

const validateForm = (): boolean => {
  if (!username.value) {
    error.value = '請輸入帳號'
    return false
  }
  if (username.value.length < 4) {
    error.value = '帳號長度至少需要 4 個字元'
    return false
  }
  if (!password.value) {
    error.value = '請輸入密碼'
    return false
  }
  if (password.value.length < 8) {
    error.value = '密碼長度至少需要 8 個字元'
    return false
  }
  if (password.value !== confirmPassword.value) {
    error.value = '密碼與確認密碼不符'
    return false
  }
  if (email.value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
    error.value = '請輸入有效的電子郵件地址'
    return false
  }
  if (phone.value && !/^09\d{8}$/.test(phone.value)) {
    error.value = '請輸入有效的手機號碼（09開頭的10碼數字）'
    return false
  }
  if (!agreedToTerms.value) {
    error.value = '請同意服務條款及隱私權政策'
    return false
  }
  return true
}

const handleRegister = async () => {
  error.value = null
  success.value = null

  if (!validateForm()) {
    return
  }

  isLoading.value = true

  try {
    await authStore.register(username.value, password.value, email.value || undefined, phone.value || undefined)
    success.value = '註冊成功！即將跳轉至登入頁面...'
    
    setTimeout(() => {
      router.push('/login')
    }, 2000)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '註冊失敗，請重試'
  } finally {
    isLoading.value = false
  }
}

const handleBackToLogin = () => {
  router.push('/login')
}
</script>

<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <h1 class="bank-title">富邦網路銀行</h1>
        <p class="subtitle">申請帳號</p>
      </div>

      <form class="auth-form" @submit.prevent="handleRegister">
        <!-- 成功資訊 -->
        <Alert
          v-if="success"
          :message="success"
          type="success"
        />

        <!-- 錯誤資訊 -->
        <Alert
          v-if="error"
          :message="error"
          type="error"
          @close="error = null"
        />

        <!-- 帳號輸入 -->
        <div class="form-group">
          <label for="username" class="form-label">
            帳號 <span class="required">*</span>
          </label>
          <input
            id="username"
            v-model="username"
            type="text"
            placeholder="請輸入帳號（至少 4 個字元）"
            class="form-input"
            :disabled="isLoading"
          />
        </div>

        <!-- 電子郵件輸入 -->
        <div class="form-group">
          <label for="email" class="form-label">
            電子郵件 <span class="optional">(選填)</span>
          </label>
          <input
            id="email"
            v-model="email"
            type="email"
            placeholder="請輸入電子郵件"
            class="form-input"
            :disabled="isLoading"
          />
        </div>

        <!-- 手機號碼輸入 -->
        <div class="form-group">
          <label for="phone" class="form-label">
            手機號碼 <span class="optional">(選填)</span>
          </label>
          <input
            id="phone"
            v-model="phone"
            type="tel"
            placeholder="請輸入手機號碼（09開頭的10碼數字）"
            class="form-input"
            :disabled="isLoading"
          />
        </div>

        <!-- 密碼輸入 -->
        <div class="form-group">
          <label for="password" class="form-label">
            密碼 <span class="required">*</span>
          </label>
          <div class="password-input-wrapper">
            <input
              id="password"
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="請輸入密碼（至少 8 個字元）"
              class="form-input"
              :disabled="isLoading"
            />
            <button
              type="button"
              class="toggle-password"
              @click="showPassword = !showPassword"
              :disabled="isLoading"
            >
              {{ showPassword ? '隱藏' : '顯示' }}
            </button>
          </div>
        </div>

        <!-- 確認密碼輸入 -->
        <div class="form-group">
          <label for="confirmPassword" class="form-label">
            確認密碼 <span class="required">*</span>
          </label>
          <div class="password-input-wrapper">
            <input
              id="confirmPassword"
              v-model="confirmPassword"
              :type="showConfirmPassword ? 'text' : 'password'"
              placeholder="請再次輸入密碼"
              class="form-input"
              :disabled="isLoading"
            />
            <button
              type="button"
              class="toggle-password"
              @click="showConfirmPassword = !showConfirmPassword"
              :disabled="isLoading"
            >
              {{ showConfirmPassword ? '隱藏' : '顯示' }}
            </button>
          </div>
        </div>

        <!-- 服務條款同意 -->
        <div class="form-group checkbox-group">
          <label class="checkbox-label">
            <input
              v-model="agreedToTerms"
              type="checkbox"
              :disabled="isLoading"
            />
            <span>
              我已閱讀並同意
              <a href="#" class="link">服務條款</a>
              及
              <a href="#" class="link">隱私權政策</a>
            </span>
          </label>
        </div>

        <!-- 註冊按鈕 -->
        <button
          type="submit"
          class="btn-register"
          :disabled="isLoading || !username || !password || !confirmPassword || !agreedToTerms"
        >
          <span v-if="!isLoading">註冊</span>
          <span v-else>註冊中...</span>
        </button>
      </form>

      <!-- 返回登入 -->
      <div class="auth-links">
        <span>已有帳號？</span>
        <button type="button" class="link-button" @click="handleBackToLogin" :disabled="isLoading">
          立即登入
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

.required {
  color: #ff4444;
}

.optional {
  color: #999;
  font-weight: 400;
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

.password-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.password-input-wrapper .form-input {
  padding-right: 50px;
}

.toggle-password {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  color: #0066cc;
  cursor: pointer;
  font-size: 12px;
  padding: 4px 8px;
  transition: color 0.2s;
}

.toggle-password:hover:not(:disabled) {
  color: #004499;
}

.toggle-password:disabled {
  color: #ccc;
  cursor: not-allowed;
}

.checkbox-group {
  margin-bottom: 24px;
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

.btn-register {
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

.btn-register:hover:not(:disabled) {
  box-shadow: 0 4px 12px rgba(0, 102, 204, 0.3);
  transform: translateY(-1px);
}

.btn-register:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.auth-links {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #666;
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

.link-button {
  background: none;
  border: none;
  color: #0066cc;
  cursor: pointer;
  font-size: 13px;
  padding: 0;
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
