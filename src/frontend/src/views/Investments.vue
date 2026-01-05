<script setup lang="ts">
import { ref, type Ref } from 'vue'
import { useApi } from '../composables/useApi'

const { api, base } = useApi()

const invQueryForm = ref({ account_id: '' })
const invPurchaseForm = ref({ account_id: '', product_id: '', amount: 0 })
type Results = { invQuery: Ref<string>, invPurchase: Ref<string> }
const results: Results = { invQuery: ref(''), invPurchase: ref('') }

const handle = async (which: keyof Results, path: string, data: any) => {
  const res = await api(path, data)
  results[which].value = JSON.stringify(res, null, 2)
  return res
}

const queryInv = async () => handle('invQuery', base + '/api/investments/query', invQueryForm.value)
const purchaseInv = async () => handle('invPurchase', base + '/api/investments/purchase', invPurchaseForm.value)
</script>

<template>
  <div class="legacy">
    <h2>投資理財</h2>
    <form @submit.prevent="queryInv">
      <input v-model="invQueryForm.account_id" name="account_id" placeholder="帳戶 ID" />
      <button type="submit">查詢投資紀錄</button>
    </form>
    <pre>{{ results.invQuery }}</pre>

    <form @submit.prevent="purchaseInv">
      <input v-model="invPurchaseForm.account_id" name="account_id" placeholder="帳戶 ID" />
      <input v-model="invPurchaseForm.product_id" name="product_id" placeholder="商品代號" />
      <input v-model.number="invPurchaseForm.amount" name="amount" placeholder="申購金額" type="number" />
      <button type="submit">投資申購</button>
    </form>
    <pre>{{ results.invPurchase }}</pre>
  </div>
</template>

<style scoped>
pre { background:#f6f8fa; padding:10px; overflow:auto }
input, select, button { margin:4px 0; display:block }
</style>
