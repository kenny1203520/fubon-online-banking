<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()

interface MenuItem {
  name: string
  path: string
  icon: string
  label: string
}

const menuItems: MenuItem[] = [
  { name: 'dashboard', path: '/dashboard', icon: '📊', label: '儀表板' },
  { name: 'accounts', path: '/accounts', icon: '💳', label: '帳戶管理' },
  { name: 'transactions', path: '/transactions', icon: '💱', label: '交易轉帳' },
  { name: 'investments', path: '/investments', icon: '📈', label: '投資理財' },
  { name: 'cards', path: '/cards', icon: '🎫', label: '信用卡' },
  { name: 'loans', path: '/loans', icon: '🏦', label: '貸款服務' },
]

const isActive = (itemPath: string) => {
  return route.path.startsWith(itemPath)
}
</script>

<template>
  <aside class="sidebar">
    <!-- Navigation Menu -->
    <nav class="menu">
      <router-link
        v-for="item in menuItems"
        :key="item.name"
        :to="item.path"
        class="menu-item"
        :class="{ active: isActive(item.path) }"
        :title="item.label"
      >
        <span class="icon">{{ item.icon }}</span>
        <span class="label">{{ item.label }}</span>
      </router-link>
    </nav>
  </aside>
</template>

<style scoped>
.sidebar {
  position: fixed;
  left: 0;
  right: 0;
  top: 60px;
  height: 60px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  z-index: 999;
  display: flex;
  align-items: center;
  overflow-x: auto;
  overflow-y: hidden;
}

.menu {
    display: flex;
    align-items: center;
    gap: 0;
    list-style: none;
    padding: 0;
    margin: 0;
    width: 100%;
    flex-wrap: nowrap;
    justify-content: center;
    align-content: center;
}

.menu-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 8px 20px;
  color: #666;
  text-decoration: none;
  border-bottom: 3px solid transparent;
  transition: all 0.3s ease;
  font-size: 13px;
  white-space: nowrap;
  min-width: 100px;
  height: 100%;
}

.menu-item:hover {
  background-color: #f5f5f5;
  color: #0066cc;
}

.menu-item.active {
  background-color: #f0f7ff;
  color: #0066cc;
  border-bottom-color: #0066cc;
  font-weight: 600;
}

.icon {
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.label {
  font-size: 12px;
  white-space: nowrap;
}

/* Responsive Design */
@media (max-width: 768px) {
  .sidebar {
    top: 50px;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .menu {
    justify-content: flex-start;
  }

  .menu-item {
    min-width: 80px;
    padding: 8px 12px;
  }

  .icon {
    font-size: 18px;
  }

  .label {
    font-size: 11px;
  }
}

/* 隱藏滾動條但保持滾動功能 */
.sidebar::-webkit-scrollbar {
  height: 4px;
}

.sidebar::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar::-webkit-scrollbar-thumb {
  background: #e0e0e0;
  border-radius: 2px;
}

.sidebar::-webkit-scrollbar-thumb:hover {
  background: #ccc;
}
</style>
