<script setup lang="ts">
import InvestmentsNav from '../components/InvestmentsNav.vue'
</script>

<template>
  <div class="page-wrapper">
    <InvestmentsNav />
    <div class="page-header">
      <h1>基金投資</h1>
      <p>投資各類基金產品</p>
    </div>
    <div class="page-content">
      <section class="controls">
        <label>風險等級：
          <select v-model="filterRisk">
            <option value="">全部</option>
            <option value="低">低</option>
            <option value="中">中</option>
            <option value="高">高</option>
          </select>
        </label>
        <label>帳戶 ID: <input v-model.number="accountId" type="number" min="1" /></label>
        <button @click="fetchFunds">查詢基金</button>
      </section>

      <section v-if="loading">載入中...</section>
      <section v-if="error" class="error">{{ error }}</section>

      <section v-if="funds.length" class="fund-list">
        <div v-for="f in funds" :key="f.id" class="fund">
          <div class="meta">
            <h3>{{ f.name }} <small>（風險: {{ f.risk_level }}）</small></h3>
            <div class="desc">{{ f.description }}</div>
            <div>最低投資: {{ f.min_amount }} {{ f.currency }}</div>
          </div>
          <div class="buy">
            <input v-model.number="amounts[f.id]" type="number" :min="f.min_amount" />
            <button @click="purchaseFund(f)">購買</button>
          </div>
        </div>
      </section>

      <section v-if="!funds.length && !loading">目前沒有符合條件的基金。</section>
    </div>
  </div>
</template>

<script lang="ts">
import { ref, reactive } from 'vue'
import { investmentService } from '../services/investment'

const filterRisk = ref<string>('')
const accountId = ref<number | null>(null)
const funds = ref<any[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const amounts = reactive<Record<number, number>>({})

const fetchFunds = async () => {
  loading.value = true
  error.value = null
  try {
    const res = await investmentService.getFunds(filterRisk.value ? { risk_level: filterRisk.value } : undefined)
    funds.value = res.data.items || []
    funds.value.forEach((f: any) => { amounts[f.id] = f.min_amount || 0 })
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || '取得基金失敗'
  } finally { loading.value = false }
}

const purchaseFund = async (f: any) => {
  error.value = null
  const amount = amounts[f.id]
  if (!amount || amount < f.min_amount) { error.value = `金額需 >= ${f.min_amount}`; return }
  try {
    const payload = { account_id: accountId.value || 1, product_id: f.id, amount }
    const res = await investmentService.purchaseFund(payload)
    alert(res.data?.message || '申購成功')
    // optionally refresh
    if (accountId.value) await fetchFunds()
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || '申購失敗'
  }
}

export default {
  setup() {
    return { filterRisk, accountId, funds, loading, error, amounts, fetchFunds, purchaseFund }
  }
}
</script>

<style scoped>
.page-wrapper { padding: 20px; }
.page-header { margin-bottom: 30px; }
.page-header h1 { margin: 0; font-size: 28px; color: #333; }
.page-header p { margin: 8px 0 0 0; color: #999; font-size: 14px; }
.page-content { background: white; padding: 24px; border-radius: 8px; border: 1px solid #e0e0e0; }
.controls { display:flex; gap:12px; align-items:center; margin-bottom:16px }
.fund-list { display:flex; flex-direction:column; gap:12px }
.fund { display:flex; justify-content:space-between; padding:12px; border:1px solid #eee; border-radius:6px }
.buy input { width:120px; margin-right:8px }
.error { color: red; margin-top:8px }
</style>
