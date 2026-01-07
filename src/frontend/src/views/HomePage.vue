<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/modules/auth/stores/auth'
import { computed } from 'vue'

const router = useRouter()
const authStore = useAuthStore()

const isAuthenticated = computed(() => authStore.isAuthenticated);

const goToDashboard = async () => {
  if (await isAuthenticated.value) {
    router.push('/dashboard')
  } else {
    router.push('/login')
  }
}
</script>

<template>
  <div class="home-page">
    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-content">
        <h1 class="hero-title">富邦網路銀行</h1>
        <p class="hero-subtitle">安全、便捷、智能的數位金融服務</p>
        <div class="hero-actions">
          <button class="btn btn-primary" @click="goToDashboard">
            {{ isAuthenticated ? '進入帳戶' : '立即登入' }}
          </button>
          <router-link to="/register" class="btn btn-secondary">
            申請開戶
          </router-link>
        </div>
      </div>
      <div class="hero-image">
        <div class="floating-card">
          <div class="card-icon">🏦</div>
          <div class="card-text">數位金融</div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features">
      <div class="container">
        <h2 class="section-title">我們的服務</h2>
        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon">💳</div>
            <h3>帳戶管理</h3>
            <p>輕鬆管理您的帳戶，隨時查看餘額和交易記錄</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">💱</div>
            <h3>轉帳服務</h3>
            <p>快速安全的轉帳服務，支援即時轉帳和預約轉帳</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">📈</div>
            <h3>投資理財</h3>
            <p>多元化投資商品，基金、股票、保險一站式服務</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">🎫</div>
            <h3>信用卡</h3>
            <p>線上申請信用卡，即時查詢帳單和消費明細</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">🏦</div>
            <h3>貸款服務</h3>
            <p>個人信貸、房貸、車貸，輕鬆線上申請</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">🔒</div>
            <h3>安全保障</h3>
            <p>銀行級加密技術，保護您的資產安全</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Benefits Section -->
    <section class="benefits">
      <div class="container">
        <h2 class="section-title">為什麼選擇我們</h2>
        <div class="benefits-grid">
          <div class="benefit-item">
            <div class="benefit-number">01</div>
            <h3>24/7 全天候服務</h3>
            <p>隨時隨地存取您的帳戶，不受時間地點限制</p>
          </div>
          <div class="benefit-item">
            <div class="benefit-number">02</div>
            <h3>即時通知</h3>
            <p>交易即時推播通知，掌握每一筆資金動態</p>
          </div>
          <div class="benefit-item">
            <div class="benefit-number">03</div>
            <h3>專業客服</h3>
            <p>專業客服團隊隨時為您解決問題</p>
          </div>
          <div class="benefit-item">
            <div class="benefit-number">04</div>
            <h3>優惠活動</h3>
            <p>定期推出優惠活動，讓您享受更多回饋</p>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta">
      <div class="container">
        <h2>立即開始您的數位金融之旅</h2>
        <p>加入富邦網路銀行，體驗便捷的金融服務</p>
        <button class="btn btn-large" @click="goToDashboard">
          {{ isAuthenticated ? '進入帳戶' : '立即登入' }}
        </button>
      </div>
    </section>

    <!-- Footer -->
    <footer class="home-footer">
      <div class="container">
        <div class="footer-content">
          <div class="footer-section">
            <h4>關於富邦</h4>
            <ul>
              <li><a href="#">公司介紹</a></li>
              <li><a href="#">新聞中心</a></li>
              <li><a href="#">投資者關係</a></li>
            </ul>
          </div>
          <div class="footer-section">
            <h4>客戶服務</h4>
            <ul>
              <li><a href="#">常見問題</a></li>
              <li><a href="#">聯絡我們</a></li>
              <li><a href="#">服務據點</a></li>
            </ul>
          </div>
          <div class="footer-section">
            <h4>法律資訊</h4>
            <ul>
              <li><a href="#">隱私政策</a></li>
              <li><a href="#">服務條款</a></li>
              <li><a href="#">資訊安全</a></li>
            </ul>
          </div>
          <div class="footer-section">
            <h4>聯絡資訊</h4>
            <p>客服專線：0800-123-456</p>
            <p>服務時間：週一至週五 09:00-18:00</p>
          </div>
        </div>
        <div class="footer-bottom">
          <p>&copy; 2026 富邦網路銀行。版權所有。</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.home-page {
  width: 100%;
  overflow-x: hidden;
}

/* Hero Section */
.hero {
  background: linear-gradient(135deg, #0066cc 0%, #004499 100%);
  color: white;
  padding: 80px 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 600px;
  position: relative;
  overflow: hidden;
}

.hero::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: radial-gradient(circle at 20% 50%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 80% 80%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
  pointer-events: none;
}

.hero-content {
  max-width: 600px;
  z-index: 1;
  text-align: center;
}

.hero-title {
  font-size: 48px;
  font-weight: 700;
  margin: 0 0 16px 0;
  letter-spacing: 2px;
}

.hero-subtitle {
  font-size: 20px;
  margin: 0 0 40px 0;
  opacity: 0.95;
}

.hero-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

.btn {
  padding: 14px 32px;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-block;
}

.btn-primary {
  background: white;
  color: #0066cc;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}

.btn-secondary {
  background: transparent;
  color: white;
  border: 2px solid white;
}

.btn-secondary:hover {
  background: white;
  color: #0066cc;
}

.hero-image {
  position: absolute;
  right: 10%;
  top: 50%;
  transform: translateY(-50%);
  display: none;
}

.floating-card {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  animation: float 3s ease-in-out infinite;
}

.card-icon {
  font-size: 64px;
  margin-bottom: 12px;
}

.card-text {
  font-size: 18px;
  font-weight: 600;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

/* Features Section */
.features {
  padding: 80px 20px;
  background: #f9f9f9;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.section-title {
  text-align: center;
  font-size: 36px;
  color: #333;
  margin: 0 0 60px 0;
  font-weight: 700;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 30px;
}

.feature-card {
  background: white;
  padding: 40px 30px;
  border-radius: 12px;
  text-align: center;
  transition: all 0.3s ease;
  border: 1px solid #e0e0e0;
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.feature-card h3 {
  font-size: 20px;
  color: #333;
  margin: 0 0 12px 0;
}

.feature-card p {
  color: #666;
  line-height: 1.6;
  margin: 0;
}

/* Benefits Section */
.benefits {
  padding: 80px 20px;
  background: white;
}

.benefits-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 40px;
}

.benefit-item {
  text-align: center;
}

.benefit-number {
  display: inline-block;
  width: 60px;
  height: 60px;
  line-height: 60px;
  background: linear-gradient(135deg, #0066cc 0%, #004499 100%);
  color: white;
  border-radius: 50%;
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 20px;
}

.benefit-item h3 {
  font-size: 20px;
  color: #333;
  margin: 0 0 12px 0;
}

.benefit-item p {
  color: #666;
  line-height: 1.6;
  margin: 0;
}

/* CTA Section */
.cta {
  padding: 80px 20px;
  background: linear-gradient(135deg, #0066cc 0%, #004499 100%);
  color: white;
  text-align: center;
}

.cta h2 {
  font-size: 32px;
  margin: 0 0 16px 0;
}

.cta p {
  font-size: 18px;
  margin: 0 0 40px 0;
  opacity: 0.95;
}

.btn-large {
  padding: 16px 48px;
  font-size: 18px;
  background: white;
  color: #0066cc;
}

.btn-large:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}

/* Footer */
.home-footer {
  background: #1a1a1a;
  color: #ccc;
  padding: 60px 20px 20px;
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 40px;
  margin-bottom: 40px;
}

.footer-section h4 {
  color: white;
  font-size: 16px;
  margin: 0 0 20px 0;
  font-weight: 600;
}

.footer-section ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-section li {
  margin-bottom: 12px;
}

.footer-section a {
  color: #ccc;
  text-decoration: none;
  transition: color 0.3s ease;
}

.footer-section a:hover {
  color: white;
}

.footer-section p {
  margin: 0 0 8px 0;
  font-size: 14px;
}

.footer-bottom {
  text-align: center;
  padding-top: 30px;
  border-top: 1px solid #333;
  font-size: 14px;
}

/* Responsive */
@media (min-width: 1024px) {
  .hero-image {
    display: block;
  }
  
  .hero-content {
    text-align: left;
  }
  
  .hero-actions {
    justify-content: flex-start;
  }
}

@media (max-width: 768px) {
  .hero {
    padding: 60px 20px;
    min-height: 500px;
  }
  
  .hero-title {
    font-size: 36px;
  }
  
  .hero-subtitle {
    font-size: 16px;
  }
  
  .section-title {
    font-size: 28px;
  }
  
  .features,
  .benefits,
  .cta {
    padding: 60px 20px;
  }
  
  .cta h2 {
    font-size: 24px;
  }
}
</style>
