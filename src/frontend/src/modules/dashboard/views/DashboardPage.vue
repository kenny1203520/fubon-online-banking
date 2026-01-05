<script setup lang="ts">
</script>

<template>
  <div class="dashboard-page">
    <div class="page-header">
      <h1>儀表板</h1>
      <p>歡迎回到您的帳戶</p>
    </div>

    <div class="dashboard-grid">
      <!-- 快速統計 -->
      <div class="card quick-stats">
        <h2>帳戶概覽</h2>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-value">$1,234,567</div>
            <div class="stat-label">總資產</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">3</div>
            <div class="stat-label">帳戶數</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">$50,000</div>
            <div class="stat-label">投資淨值</div>
          </div>
        </div>
      </div>

      <!-- 最近交易 -->
      <div class="card recent-transactions">
        <h2>最近交易</h2>
        <div class="placeholder">最近交易列表 - 開發中</div>
      </div>

      <!-- 快速功能 -->
      <div class="card quick-actions">
        <h2>快速功能</h2>
        <div class="action-buttons">
          <router-link to="/transactions" class="action-btn">
            <span>💱</span>
            <span>轉帳</span>
          </router-link>
          <router-link to="/transactions/exchange" class="action-btn">
            <span>🔄</span>
            <span>換匯</span>
          </router-link>
          <router-link to="/investments" class="action-btn">
            <span>📈</span>
            <span>投資</span>
          </router-link>
          <router-link to="/cards" class="action-btn">
            <span>🎫</span>
            <span>信用卡</span>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-page {
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

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.card {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid #e0e0e0;
}

.card h2 {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #333;
  font-weight: 600;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.stat-item {
  text-align: center;
  padding: 12px;
  background: #f9f9f9;
  border-radius: 6px;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #0066cc;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #999;
}

.placeholder {
  color: #999;
  text-align: center;
  padding: 40px 20px;
  background: #f9f9f9;
  border-radius: 6px;
}

.action-buttons {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px;
  background: #f9f9f9;
  border-radius: 6px;
  text-decoration: none;
  color: #333;
  transition: all 0.3s ease;
  border: 1px solid #e0e0e0;
}

.action-btn:hover {
  background: #f0f7ff;
  border-color: #0066cc;
  color: #0066cc;
}

.action-btn span:first-child {
  font-size: 24px;
}

.action-btn span:last-child {
  font-size: 13px;
  font-weight: 500;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
