<script setup lang="ts">
</script>

<template>
  <footer class="footer">
    <div class="footer-content">
      <div class="footer-section">
        <h4>關於我們</h4>
        <ul>
          <li><a href="#">公司介紹</a></li>
          <li><a href="#">新聞中心</a></li>
          <li><a href="#">投資者關係</a></li>
        </ul>
      </div>

      <div class="footer-section">
        <h4>客服支援</h4>
        <ul>
          <li><a href="#">聯絡我們</a></li>
          <li><a href="#">FAQ</a></li>
          <li><a href="#">線上客服</a></li>
        </ul>
      </div>

      <div class="footer-section">
        <h4>法律資訊</h4>
        <ul>
          <li><a href="#">隱私政策</a></li>
          <li><a href="#">服務條款</a></li>
          <li><a href="#">安全聲明</a></li>
        </ul>
      </div>

      <div class="footer-section">
        <h4>社群媒體</h4>
        <div class="social-links">
          <a href="#" title="Facebook">Facebook</a>
          <a href="#" title="Twitter">Twitter</a>
          <a href="#" title="LinkedIn">LinkedIn</a>
        </div>
      </div>
    </div>

    <div class="footer-bottom">
      <p>&copy; 2026 富邦網路銀行。版權所有。</p>
      <p>客服電話：0800-123-456 | 營業時間：週一至週五 09:00-18:00</p>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
  color: #ccc;
  padding: 40px 20px 20px;
  margin-top: 60px;
  border-top: 1px solid #e0e0e0;
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  max-width: 1400px;
  margin: 0 auto;
  gap: 30px;
  margin-bottom: 30px;
}

.footer-section h4 {
  color: white;
  margin-bottom: 16px;
  font-size: 14px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.footer-section ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-section li {
  margin-bottom: 8px;
}

.footer-section a {
  color: #ccc;
  text-decoration: none;
  font-size: 13px;
  transition: color 0.3s ease;
}

.footer-section a:hover {
  color: white;
}

.social-links {
  display: flex;
  gap: 16px;
}

.footer-bottom {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #444;
  font-size: 12px;
  color: #999;
}

.footer-bottom p {
  margin: 4px 0;
}

@media (max-width: 768px) {
  .footer {
    padding: 30px 16px 16px;
  }

  .footer-content {
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
  }

  .footer-section h4 {
    font-size: 12px;
  }

  .footer-section a {
    font-size: 12px;
  }
}
</style>
