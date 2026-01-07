<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const availableServices = [
  { id: 'accounts', label: '帳戶查詢' },
  { id: 'creditcards', label: '信用卡服務' },
  { id: 'investments', label: '投資理財' },
  { id: 'loans', label: '貸款服務' },
  { id: 'transactions', label: '交易紀錄' }
]

const selected = ref<string[]>([])
const redirectTo = (route.query.redirect as string) || '/dashboard'

function confirm() {
  localStorage.setItem('user_services', JSON.stringify(selected.value))
  
  // 根據選擇的服務決定跳轉目標
  if (selected.value.includes('accounts')) {
    router.push('/accounts')
  } else if (selected.value.includes('creditcards')) {
    router.push('/creditcards')
  } else if (selected.value.includes('investments')) {
    router.push('/investments')
  } else if (selected.value.includes('loans')) {
    router.push('/loans')
  } else if (selected.value.includes('transactions')) {
    router.push('/transactions')
  } else {
    router.push(redirectTo)
  }
}

function skip() {
  router.push(redirectTo)
}
</script>

<template>
  <div class="service-selection">
    <div class="card">
      <h2>選擇您需要的服務</h2>
      <p class="muted">您可於設定中稍後變更此設定。</p>
      <div class="list">
        <label v-for="svc in availableServices" :key="svc.id" class="item">
          <input type="checkbox" :value="svc.id" v-model="selected" />
          <span>{{ svc.label }}</span>
        </label>
      </div>
      <div class="actions">
        <button class="btn-secondary" @click="skip">略過</button>
        <button class="btn-primary" @click="confirm" :disabled="selected.length===0">確認</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.service-selection{min-height:100vh;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#f7fbff,#eef6ff);padding:24px}
.card{background:#fff;padding:28px;border-radius:10px;box-shadow:0 8px 30px rgba(0,0,0,0.06);width:100%;max-width:520px}
.list{display:flex;flex-direction:column;gap:10px;margin:16px 0}
.item{display:flex;align-items:center;gap:12px}
.actions{display:flex;justify-content:flex-end;gap:12px}
.btn-primary{background:#0066cc;color:#fff;padding:10px 16px;border-radius:6px;border:0}
.btn-secondary{background:#f3f4f6;color:#333;padding:10px 16px;border-radius:6px;border:0}
</style>
