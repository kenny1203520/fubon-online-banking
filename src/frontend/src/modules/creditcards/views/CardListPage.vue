<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goToApply = () => {
  router.push('/cards/apply')
}
</script>

<template>
  <div class="page-wrapper">
    <div class="page-header">
      <h1>信用卡</h1>
      <p>管理您的信用卡</p>
      <button class="btn-apply" @click="goToApply">
        + 申請信用卡
      </button>
    </div>
    <div class="page-content">
      <div class="placeholder">
        <div class="empty-icon">💳</div>
        <h3>尚無信用卡</h3>
        <p>您還沒有申請任何信用卡</p>
        <button class="btn-primary" @click="goToApply">
          立即申請信用卡
        </button>
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
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

.btn-apply {
  padding: 12px 24px;
  background: linear-gradient(135deg, #0066cc 0%, #004499 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-apply:hover {
  box-shadow: 0 4px 12px rgba(0, 102, 204, 0.3);
  transform: translateY(-1px);
}

.page-content { 
  background: white; 
  padding: 60px 24px; 
  border-radius: 8px; 
  border: 1px solid #e0e0e0; 
}

.placeholder { 
  color: #999; 
  text-align: center; 
  padding: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.empty-icon {
  font-size: 64px;
  opacity: 0.5;
}

.placeholder h3 {
  margin: 0;
  color: #333;
  font-size: 20px;
}

.placeholder p {
  margin: 0;
  color: #999;
  font-size: 14px;
}

.btn-primary {
  margin-top: 8px;
  padding: 12px 32px;
  background: linear-gradient(135deg, #0066cc 0%, #004499 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  box-shadow: 0 4px 12px rgba(0, 102, 204, 0.3);
  transform: translateY(-1px);
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .btn-apply {
    width: 100%;
  }
}
</style>
