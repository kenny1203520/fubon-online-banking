<script setup lang="ts">
import InvestmentsNav from '../components/InvestmentsNav.vue'
</script>

<template>
  <div class="page-wrapper">
    <InvestmentsNav />
    <div class="page-header">
      <h1>保險</h1>
      <p>購買保險產品</p>
    </div>
    <div class="page-content">
      <div class="placeholder">保險頁面 - 開發中</div>
    </div>
  </div>
</template>

<style scoped>
.page-wrapper { padding: 20px; }
.page-header { margin-bottom: 30px; }
.page-header h1 { margin: 0; font-size: 28px; color: #333; }
.page-header p { margin: 8px 0 0 0; color: #999; font-size: 14px; }
.page-content { background: white; padding: 24px; border-radius: 8px; border: 1px solid #e0e0e0; }
.placeholder { color: #999; text-align: center; padding: 60px 40px; }
</style>
