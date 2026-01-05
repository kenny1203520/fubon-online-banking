<script setup lang="ts">
import { ref, type Ref } from 'vue'
import { useApi } from '../composables/useApi'

const { api, base } = useApi()

const cardPayForm = ref({ user_id: '', card_id: '', amount: 0 })
const cardCashForm = ref({ card_id: '', amount: 0 })
type Results = { cardPay: Ref<string>, cardCash: Ref<string> }
const results: Results = { cardPay: ref(''), cardCash: ref('') }

const handle = async (which: keyof Results, path: string, data: any) => {
  const res = await api(path, data)
  results[which].value = JSON.stringify(res, null, 2)
  return res
}

const payCard = async () => handle('cardPay', base + '/api/creditcards/pay', cardPayForm.value)
const cashCard = async () => handle('cardCash', base + '/api/creditcards/cash_advance', cardCashForm.value)
</script>

<template>
  <div class="legacy">
    <h2>信用卡</h2>
    <form @submit.prevent="payCard">
      <input v-model="cardPayForm.user_id" name="user_id" placeholder="使用者 ID" />
      <input v-model="cardPayForm.card_id" name="card_id" placeholder="卡片 ID" />
      <input v-model.number="cardPayForm.amount" name="amount" placeholder="繳款金額" type="number" />
      <button type="submit">繳交卡費</button>
    </form>
    <pre>{{ results.cardPay }}</pre>

    <form @submit.prevent="cashCard">
      <input v-model="cardCashForm.card_id" name="card_id" placeholder="卡片 ID" />
      <input v-model.number="cardCashForm.amount" name="amount" placeholder="預借現金金額" type="number" />
      <button type="submit">預借現金</button>
    </form>
    <pre>{{ results.cardCash }}</pre>
  </div>
</template>

<style scoped>
pre { background:#f6f8fa; padding:10px; overflow:auto }
input, select, button { margin:4px 0; display:block }
</style>
