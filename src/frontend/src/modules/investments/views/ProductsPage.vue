<template>
  <div class="page investments-products">
    <InvestmentsNav />
    <h1>投資產品</h1>

    <div v-if="loading">載入中...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <ul v-if="products.length">
      <li v-for="p in products" :key="p.id" class="product">
        <h3>{{ p.name }} <small>（風險: {{ p.risk_level }}）</small></h3>
        <p>{{ p.description }}</p>
        <p>最低金額: {{ p.min_amount }} {{ p.currency }}</p>
        <div>
          <input v-model.number="amounts[p.id]" type="number" :min="p.min_amount" />
          <button @click="purchase(p)">購買</button>
        </div>
      </li>
    </ul>

    <div v-if="!products.length && !loading">目前沒有產品。</div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, reactive, onMounted } from 'vue'
import { investmentService } from '../services/investment'
import InvestmentsNav from '../components/InvestmentsNav.vue'

export default defineComponent({
  name: 'ProductsPage',
  setup() {
    const products = ref<any[]>([])
    const loading = ref(false)
    const error = ref<string | null>(null)
    const amounts = reactive<Record<number, number>>({})

    const fetch = async () => {
      loading.value = true
      error.value = null
      try {
        const res = await investmentService.getProducts()
        products.value = res.data.items || []
        products.value.forEach(p => {
          amounts[p.id] = p.min_amount || 0
        })
      } catch (err: any) {
        error.value = err?.message || '載入產品失敗'
      } finally {
        loading.value = false
      }
    }

    const purchase = async (p: any) => {
      error.value = null
      const amount = amounts[p.id]
      if (!amount || amount < p.min_amount) {
        error.value = `金額需 >= ${p.min_amount}`
        return
      }

      try {
        // 假設使用者已登入且有主要帳戶 id，這裡暫以 1 做示範或可由使用者輸入
        const payload = { account_id: 1, product_id: p.id, amount }
        const res = await investmentService.purchaseProduct(payload)
        alert(res.data.message || '購買成功')
        // 可選: 重新載入持有部位或帳戶資訊
      } catch (err: any) {
        error.value = err?.response?.data?.detail || err?.message || '購買失敗'
      }
    }

    onMounted(fetch)

    return { products, loading, error, amounts, purchase }
  }
})
</script>

<style scoped>
.product { margin-bottom: 1rem; padding: 0.5rem; border: 1px solid #eee }
.error { color: red }
</style>
</script>

<style scoped>
.product { margin-bottom: 1rem; padding: 0.5rem; border: 1px solid #eee }
.error { color: red }
</style>
