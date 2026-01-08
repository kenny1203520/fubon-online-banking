<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/modules/auth/stores/auth'
import type { User } from '@/modules/auth/types'

const router = useRouter()
const authStore = useAuthStore()
const user = ref<User | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    // 檢查是否已登入
    if (!authStore.isAuthenticated) {
      error.value = '請先登入'
      setTimeout(() => {
        router.push('/login')
      }, 2000)
      return
    }

    // 從 auth store 獲取用戶信息
    if (authStore.user) {
      user.value = authStore.user
    } else {
      error.value = '無法加載用戶資訊'
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加載失敗'
  } finally {
    loading.value = false
  }
})

// 掩蓋敏感信息的函數
const maskPhone = (phone?: string) => {
  if (!phone) return '未設定'
  return phone.replace(/(\d{2})\d{4}(\d{4})/, '$1****$2')
}

const maskEmail = (email?: string) => {
  if (!email) return '未設定'
  const parts = email.split('@')
  if (parts.length !== 2) return email
  const [local, domain] = parts
  return `****${local.slice(-3)}@${domain}`
}
</script>

<template>
  <div class="page-wrapper">
    <div class="page-header">
      <h1>個人檔案</h1>
      <p>管理個人資訊</p>
    </div>
    
    <div class="page-content">
      <!-- 錯誤信息 -->
      <div v-if="error" class="error-box">
        <p>{{ error }}</p>
      </div>

      <!-- 載入中 -->
      <div v-else-if="loading" class="loading">
        <div class="spinner"></div>
        <p>載入中...</p>
      </div>

      <!-- 用戶信息 -->
      <div v-else-if="user">
        <!-- 提示框 -->
        <div class="alert-box">
          <div class="alert-icon">ℹ️</div>
          <div class="alert-content">
            <strong>親愛的客戶：</strong>
            <p>以下為您於註冊帳戶時所提供的基本資訊，如有異動，建議您立即更新。</p>
          </div>
        </div>

        <!-- 通訊資料 -->
        <div class="info-section">
          <div class="section-header">
            <h3>📱 通訊資料</h3>
            <button class="edit-btn">立即變更</button>
          </div>
          <div class="info-grid">
            <div class="info-item">
              <label>手機號碼</label>
              <div class="info-value">{{ maskPhone(user.phone) }}</div>
            </div>
            <div class="info-item">
              <label>聯絡電話</label>
              <div class="info-value">未設定</div>
            </div>
          </div>
        </div>

        <!-- 電子郵件信箱 -->
        <div class="info-section">
          <div class="section-header">
            <h3>📧 電子郵件信箱</h3>
            <button class="edit-btn">立即變更</button>
          </div>
          <div class="info-grid">
            <div class="info-item">
              <label>Email</label>
              <div class="info-value">{{ maskEmail(user.email) }}</div>
            </div>
          </div>
        </div>

        <!-- 個人資料 -->
        <div class="info-section">
          <div class="section-header">
            <h3>👤 個人資料</h3>
            <button class="edit-btn">立即變更</button>
          </div>
          <div class="info-grid">
            <div class="info-item">
              <label>使用者名稱</label>
              <div class="info-value">{{ user.username }}</div>
            </div>
            <div class="info-item">
              <label>身分</label>
              <div class="info-value">{{ user.is_admin === true ? '管理員' : '一般使用者' }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 沒有用戶資訊 -->
      <div v-else class="error-box">
        <p>無法加載用戶資訊，請重新登入。</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-wrapper {
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
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

.page-content {
  background: white;
  padding: 24px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.alert-box {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: #e3f2fd;
  border-left: 4px solid #2196f3;
  border-radius: 4px;
  margin-bottom: 24px;
}

.alert-icon {
  flex-shrink: 0;
  font-size: 20px;
}

.alert-content {
  flex: 1;
}

.alert-content strong {
  color: #1976d2;
  display: block;
  margin-bottom: 4px;
}

.alert-content p {
  margin: 0;
  color: #555;
  font-size: 14px;
}

.info-section {
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid #e0e0e0;
}

.info-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.edit-btn {
  padding: 6px 16px;
  background: #2196f3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.edit-btn:hover {
  background: #1976d2;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

@media (max-width: 768px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
}

.info-item {
  padding: 12px;
  background: #f5f5f5;
  border-radius: 4px;
}

.info-item label {
  display: block;
  color: #666;
  font-size: 12px;
  margin-bottom: 6px;
  text-transform: uppercase;
}

.info-value {
  color: #333;
  font-size: 16px;
  font-weight: 500;
}

.loading {
  text-align: center;
  color: #999;
  padding: 40px;
}

.spinner {
  display: inline-block;
  width: 30px;
  height: 30px;
  border: 3px solid #f0f0f0;
  border-top: 3px solid #2196f3;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-box {
  padding: 16px;
  background: #ffebee;
  border-left: 4px solid #f44336;
  border-radius: 4px;
  color: #c62828;
}

.error-box p {
  margin: 0;
}
</style>
