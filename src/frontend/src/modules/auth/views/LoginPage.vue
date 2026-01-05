<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/modules/auth/store/auth'
import Alert from '@/shared/Alert.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const isLoading = ref(false)
const error = ref<string | null>(null)
const showPassword = ref(false)

const handleLogin = async () => {
  if (!username.value || !password.value) {
    error.value = '請輸入帳號和密碼'
    return
  }

  isLoading.value = true
  error.value = null

  try {
    await authStore.login(username.value, password.value)
    
    // 重定向到原始頁面或儀表板
    const redirect = route.query.redirect as string || '/dashboard'
    router.push(redirect)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '登入失敗，請重試'
  } finally {
    isLoading.value = false
  }
}

const handleKeyDown = (e: KeyboardEvent) => {
  if (e.key === 'Enter') {
    handleLogin()
  }
}
</script>

<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <h1 class="bank-title">富邦網路銀行</h1>
        <p class="subtitle">安全、便捷的線上銀行服務</p>
      </div>

      <form class="auth-form" @submit.prevent="handleLogin">
        <!-- 錯誤訊息 -->
        <Alert
          v-if="error"
          :message="error"
          type="error"
          @close="error = null"
        />

        <!-- 帳號輸入 -->
        <div class="form-group">
          <label for="username" class="form-label">帳號</label>
          <input
            id="username"
            v-model="username"
            type="text"
            placeholder="請輸入帳號"
            class="form-input"
            :disabled="isLoading"
            @keydown="handleKeyDown"
          />
        </div>

        <!-- 密碼輸入 -->
        <div class="form-group">
          <label for="password" class="form-label">密碼</label>
          <div class="password-input-wrapper">
            <input
              id="password"
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="請輸入密碼"
              class="form-input"
              :disabled="isLoading"
              @keydown="handleKeyDown"
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

        <!-- 登入按鈕 -->
        <button
          type="submit"
          class="btn-login"
          :disabled="isLoading || !username || !password"
        >
          <span v-if="!isLoading">登入</span>
          <span v-else>登入中...</span>
        </button>
      </form>

      <!-- 其他選項 -->
      <div class="auth-links">
        <router-link to="/forgot-password" class="link">忘記密碼？</router-link>
        <span class="separator">|</span>
        <router-link to="/register" class="link">申請帳號</router-link>
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
  max-width: 400px;
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

.btn-login {
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

.btn-login:hover:not(:disabled) {
  box-shadow: 0 4px 12px rgba(0, 102, 204, 0.3);
  transform: translateY(-1px);
}

.btn-login:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.auth-links {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  margin-bottom: 24px;
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

.separator {
  color: #d0d0d0;
}

.auth-footer {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
  font-size: 12px;
  color: #999;
}

.auth-footer p {
  margin: 4px 0;
}

@media (max-width: 480px) {
  .auth-card {
    padding: 30px 20px;
  }

  .bank-title {
    font-size: 24px;
  }

  .auth-links {
    flex-wrap: wrap;
  }
}
</style>
