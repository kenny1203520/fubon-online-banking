<template>
  <div class="investments-nav">
    <router-link
      v-for="item in items"
      :key="item.path"
      :to="item.path"
      class="nav-item"
      :class="{ active: isActive(item.path) }"
    >
      <span class="label">{{ item.label }}</span>
    </router-link>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()

const items = [
  { path: '/investments/funds', label: '基金' },
  { path: '/investments/stocks', label: '股票' },
  { path: '/investments/insurance', label: '保險' },
  { path: '/investments/products', label: '產品' },
  { path: '/investments/manage', label: '投資管理' },
]

const isActive = (p: string) => route.path.startsWith(p)
</script>

<style scoped>
.investments-nav { display:flex; gap:8px; margin-bottom:16px; flex-wrap:wrap }
.nav-item { padding:8px 12px; border-radius:6px; background:#fafafa; color:#333; text-decoration:none }
.nav-item.active { background:#e8f4ff; color:#0066cc; font-weight:600 }
.nav-item:hover { background:#f5faff }
.label { font-size:14px }
</style>
