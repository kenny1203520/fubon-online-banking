<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = () => {
  router.back()
}

const goHome = () => {
  router.push('/dashboard')
}
</script>

<template>
  <div class="not-found-page">
    <div class="error-container">
      <div class="error-code">404</div>
      <h1 class="error-title">頁面未找到</h1>
      <p class="error-message">抱歉，您訪問的頁面不存在或已被移除。</p>

      <div class="error-actions">
        <button class="btn btn-primary" @click="goHome">
          返回首頁
        </button>
        <button class="btn btn-secondary" @click="goBack">
          返回上一頁
        </button>
      </div>

      <div class="error-image">
        <svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
          <circle cx="100" cy="100" r="90" fill="none" stroke="#e0e0e0" stroke-width="2" />
          <text x="100" y="120" font-size="80" text-anchor="middle" fill="#d0d0d0" font-weight="bold">?</text>
        </svg>
      </div>
    </div>
  </div>
</template>

<style scoped>
.not-found-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  padding: 40px 20px;
}

.error-container {
  text-align: center;
  max-width: 500px;
}

.error-code {
  font-size: 120px;
  font-weight: 700;
  color: #0066cc;
  line-height: 1;
  margin-bottom: 16px;
  opacity: 0.8;
}

.error-title {
  font-size: 32px;
  color: #333;
  margin: 0 0 12px 0;
}

.error-message {
  font-size: 16px;
  color: #666;
  margin: 0 0 40px 0;
}

.error-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 40px;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: #0066cc;
  color: white;
}

.btn-primary:hover {
  background: #004499;
}

.btn-secondary {
  background: #f0f0f0;
  color: #333;
  border: 1px solid #d0d0d0;
}

.btn-secondary:hover {
  background: #e0e0e0;
}

.error-image {
  margin-top: 40px;
  opacity: 0.3;
}

.error-image svg {
  width: 150px;
  height: 150px;
  margin: 0 auto;
}

@media (max-width: 480px) {
  .error-code {
    font-size: 80px;
  }

  .error-title {
    font-size: 24px;
  }

  .error-message {
    font-size: 14px;
  }
}
</style>
