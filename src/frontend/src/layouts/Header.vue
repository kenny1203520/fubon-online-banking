<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/modules/auth/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const isMenuOpen = ref(false)

const isAuthenticated = computed(() => authStore.isAuthenticated)

const handleLogout = async () => {
  await authStore.logout()
  isMenuOpen.value = false
  router.push('/login')
}
</script>

<template>
  <header class="header">
    <div class="header-container">
      <!-- Logo -->
      <div class="logo">
        <router-link to="/">
          <span class="bank-name">富邦網銀</span>
        </router-link>
      </div>

      <!-- Desktop Navigation -->
      <nav class="nav-desktop" v-if="isAuthenticated">
        <router-link to="/dashboard" class="nav-link">
          <span>儀表板</span>
        </router-link>
        <router-link to="/accounts" class="nav-link">
          <span>帳戶</span>
        </router-link>
        <router-link to="/transactions" class="nav-link">
          <span>交易</span>
        </router-link>
        <router-link to="/investments" class="nav-link">
          <span>投資</span>
        </router-link>
        <router-link to="/cards" class="nav-link">
          <span>信用卡</span>
        </router-link>
      </nav>

      <!-- User Menu -->
      <div class="user-menu" v-if="isAuthenticated">
        <div class="menu-toggle" @click="isMenuOpen = !isMenuOpen">
          <span class="user-name">{{ authStore.user?.username || '使用者' }}</span>
          <svg class="icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="10" />
            <path d="M12 16v-4M12 8h.01" />
          </svg>
        </div>

        <!-- Dropdown Menu -->
        <div class="dropdown" v-if="isMenuOpen" @click="isMenuOpen = false">
          <router-link to="/settings/profile" class="menu-item">
            <span>個人檔案</span>
          </router-link>
          <router-link to="/settings/security" class="menu-item">
            <span>安全設置</span>
          </router-link>
          <div class="divider"></div>
          <button class="menu-item logout-btn" @click="handleLogout">
            <span>登出</span>
          </button>
        </div>
      </div>

      <!-- Mobile Menu Button -->
      <button class="mobile-menu-btn" v-if="!isMenuOpen">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <line x1="3" y1="6" x2="21" y2="6" />
          <line x1="3" y1="12" x2="21" y2="12" />
          <line x1="3" y1="18" x2="21" y2="18" />
        </svg>
      </button>
    </div>
  </header>
</template>

<style scoped>
.header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: linear-gradient(135deg, #0066cc 0%, #004499 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.header-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
    padding: 0 20px;
    max-width: 1400px;
    margin: 0 auto;
    width: 100%;
    flex-wrap: nowrap;
    align-content: center;
}

.logo a {
  text-decoration: none;
  color: white;
  display: flex;
  align-items: center;
  gap: 10px;
}

.bank-name {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 1px;
}

.nav-desktop {
  display: none;
  gap: 30px;
  flex: 1;
  margin-left: 40px;
}

@media (min-width: 768px) {
  .nav-desktop {
    display: flex;
  }
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 8px 12px;
  border-radius: 4px;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 500;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.nav-link.router-link-active {
  background-color: rgba(255, 255, 255, 0.2);
  border-bottom: 2px solid white;
}

.user-menu {
  position: relative;
  margin-left: auto;
}

.menu-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 4px;
  background-color: rgba(255, 255, 255, 0.1);
  cursor: pointer;
  transition: background-color 0.3s ease;
  border: none;
  color: white;
}

.menu-toggle:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.user-name {
  font-size: 14px;
  font-weight: 500;
}

.icon {
  transition: transform 0.3s ease;
}

.dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  width: 200px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  margin-top: 8px;
  overflow: hidden;
  z-index: 1001;
}

.menu-item {
  display: block;
  padding: 12px 16px;
  color: #333;
  text-decoration: none;
  border: none;
  background: none;
  cursor: pointer;
  width: 100%;
  text-align: left;
  font-size: 14px;
  transition: background-color 0.2s ease;
}

.menu-item:hover {
  background-color: #f5f5f5;
}

.logout-btn {
  color: #e74c3c;
}

.logout-btn:hover {
  background-color: #ffebee;
}

.divider {
  height: 1px;
  background-color: #e0e0e0;
}

.mobile-menu-btn {
  display: block;
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  padding: 8px;
}

@media (min-width: 768px) {
  .mobile-menu-btn {
    display: none;
  }
}
</style>
