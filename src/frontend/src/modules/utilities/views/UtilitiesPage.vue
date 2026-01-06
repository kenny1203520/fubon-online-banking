<script setup lang="ts">
import { useUtilityStore } from '../stores/utility'
import { onMounted } from 'vue'

const utilityStore = useUtilityStore()

onMounted(async () => {
  await utilityStore.fetchServices()
})
</script>

<template>
  <div class="utilities-page">
    <div class="page-header">
      <h1>生活繳費</h1>
      <p>一站式線上繳費服務，方便快捷</p>
    </div>

    <!-- 加載狀態 -->
    <div v-if="utilityStore.isLoading" class="loading-spinner">
      加載中...
    </div>

    <!-- 錯誤提示 -->
    <div v-if="utilityStore.error" class="alert alert-error">
      {{ utilityStore.error }}
    </div>

    <!-- 統計資訊 -->
    <div v-if="utilityStore.billStats" class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">待繳帳單</div>
        <div class="stat-value">{{ utilityStore.billStats.pending }}</div>
        <div class="stat-amount">新台幣 {{ utilityStore.billStats.totalAmount.toLocaleString() }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">已繳帳單</div>
        <div class="stat-value">{{ utilityStore.billStats.paid }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">逾期帳單</div>
        <div class="stat-value alert">{{ utilityStore.billStats.overdue }}</div>
      </div>
    </div>

    <!-- 服務列表 -->
    <div v-if="utilityStore.services.length > 0" class="services-section">
      <h2>可用服務</h2>
      <div class="services-grid">
        <div v-for="service in utilityStore.services" :key="service.service_type" class="service-card">
          <div class="service-title">{{ service.description }}</div>
          <div class="service-type">{{ service.service_type }}</div>
          <div class="providers">
            <span v-for="provider in service.providers" :key="provider" class="provider-badge">
              {{ provider }}
            </span>
          </div>
          <router-link :to="`/utilities/bills?type=${service.service_type}`" class="btn btn-primary">
            查看帳單
          </router-link>
        </div>
      </div>
    </div>

    <!-- 快速操作 -->
    <div class="quick-actions">
      <router-link to="/utilities/bills" class="action-button">
        <span class="icon">📄</span>
        <span>查看帳單</span>
      </router-link>
      <router-link to="/utilities/history" class="action-button">
        <span class="icon">📊</span>
        <span>繳費紀錄</span>
      </router-link>
    </div>
  </div>
</template>

<style scoped>
.utilities-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.page-header h1 {
  font-size: 32px;
  color: #333;
  margin: 0 0 10px 0;
}

.page-header p {
  color: #666;
  margin: 0;
}

.loading-spinner {
  text-align: center;
  padding: 40px;
  color: #999;
}

.alert {
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.alert-error {
  background-color: #ffebee;
  color: #c62828;
  border-left: 4px solid #c62828;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e0e0e0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.stat-label {
  color: #666;
  font-size: 14px;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #0066cc;
  margin-bottom: 8px;
}

.stat-value.alert {
  color: #d32f2f;
}

.stat-amount {
  color: #999;
  font-size: 12px;
}

.services-section {
  margin-bottom: 40px;
}

.services-section h2 {
  font-size: 24px;
  color: #333;
  margin: 0 0 20px 0;
}

.services-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.service-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e0e0e0;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
}

.service-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.service-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.service-type {
  color: #666;
  font-size: 12px;
  text-transform: uppercase;
  margin-bottom: 12px;
}

.providers {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
  flex: 1;
}

.provider-badge {
  background-color: #f0f0f0;
  color: #333;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.btn {
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  text-decoration: none;
  text-align: center;
  transition: all 0.3s ease;
  display: inline-block;
}

.btn-primary {
  background-color: #0066cc;
  color: white;
}

.btn-primary:hover {
  background-color: #0052a3;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.action-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 20px;
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  text-decoration: none;
  color: #333;
  font-weight: 600;
  transition: all 0.3s ease;
}

.action-button:hover {
  border-color: #0066cc;
  background-color: #f0f6ff;
  color: #0066cc;
}

.icon {
  font-size: 24px;
}
</style>
