<template>
  <div class="page-wrapper">
    <InvestmentsNav />
    <div class="page-header">
      <h1>投資管理</h1>
      <p>查詢投資紀錄並購買投資產品</p>
    </div>

    <div class="page-content">
      <section class="query">
        <label>帳戶 ID: <input v-model.number="accountId" type="number" min="1" /></label>
        <button @click="onQuery">查詢投資紀錄</button>
      </section>

      <section class="results" v-if="investments.length">
        <h2>投資紀錄</h2>
        <table>
          <thead>
            <tr><th>ID</th><th>帳戶</th><th>產品ID</th><th>金額</th><th>建立時間</th></tr>
          </thead>
          <tbody>
            <tr v-for="inv in investments" :key="inv.id">
              <td>{{ inv.id }}</td>
              <td>{{ inv.account_id }}</td>
              <td>{{ inv.product_id }}</td>
              <td>{{ inv.amount }}</td>
              <td>{{ inv.created_at }}</td>
            </tr>
          </tbody>
        </table>
      </section>

      <section class="products">
        <h2>投資產品</h2>
        <div v-if="products.length">
          <div v-for="p in products" :key="p.id" class="product">
            <div class="meta">
              <strong>{{ p.name }}</strong> <small>風險: {{ p.risk_level }}</small>
            </div>
            <div class="desc">{{ p.description }}</div>
            <div class="actions">
              <label>金額: <input v-model.number="amounts[p.id]" type="number" :min="p.min_amount" /></label>
              <button @click="purchase(p)">購買</button>
            </div>
          </div>
        </div>
        <div v-else>尚無產品</div>
      </section>

      <div v-if="loading">載入中...</div>
      <div v-if="error" class="error">{{ error }}</div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted } from 'vue'
import { investmentService } from '../services/investment'
import InvestmentsNav from '../components/InvestmentsNav.vue'

const accountId = ref<number | null>(null)
const investments = ref<any[]>([])
const products = ref<any[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const amounts = reactive<Record<number, number>>({})

const loadProducts = async () => {
  loading.value = true
  error.value = null
  try {
    const res = await investmentService.getProducts()
    products.value = res.data.items || []
    products.value.forEach((p: any) => { amounts[p.id] = p.min_amount || 0 })
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || '載入產品失敗'
  } finally { loading.value = false }
}

const onQuery = async () => {
  if (!accountId.value) { error.value = '請輸入帳戶 ID'; return }
  loading.value = true
  error.value = null
  try {
    const res = await investmentService.queryInvestments({ account_id: accountId.value })
    investments.value = res.data.items || []
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || '查詢失敗'
  } finally { loading.value = false }
}

const purchase = async (p: any) => {
  error.value = null
  const amount = amounts[p.id]
  if (!amount || amount < p.min_amount) { error.value = `金額需 >= ${p.min_amount}`; return }
  try {
    const payload = { account_id: accountId.value || 1, product_id: p.id, amount }
    const res = await investmentService.purchaseProduct(payload)
    alert(res.data?.message || '購買成功')
    // refresh investments
    if (accountId.value) await onQuery()
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || '購買失敗'
  }
}

onMounted(loadProducts)
</script>

<style scoped>
.page-wrapper { padding: 20px }
.page-header h1 { margin:0 }
.product { border:1px solid #eee; padding:8px; margin-bottom:8px }
.actions { margin-top:8px }
.error { color: red; margin-top:8px }
table { width:100%; border-collapse: collapse }
th, td { border:1px solid #eee; padding:6px }
</style>
