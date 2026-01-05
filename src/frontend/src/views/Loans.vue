<script setup lang="ts">
import { ref, type Ref } from 'vue'
import { useApi } from '../composables/useApi'

const { api, base } = useApi()

const loanCalcForm = ref({ amount: 0, years: 0, rate: 0 })
const loanApplyForm = ref({ user_id: '', amount: 0 })
type Results = { loanCalc: Ref<string>, loanApply: Ref<string> }
const results: Results = { loanCalc: ref(''), loanApply: ref('') }

const handle = async (which: keyof Results, path: string, data: any) => {
  const res = await api(path, data)
  results[which].value = JSON.stringify(res, null, 2)
  return res
}

const calcLoan = async () => {
  const years = Number(loanCalcForm.value.years) || 0
  const r = Number(loanCalcForm.value.rate) / 100 || 0
  const n = years * 12
  const P = Number(loanCalcForm.value.amount) || 0
  let monthly = 0
  if (r > 0 && n > 0) {
    const i = r / 12
    monthly = (P * i) / (1 - Math.pow(1 + i, -n))
  }
  results.loanCalc.value = JSON.stringify({ monthly: Math.round(monthly * 100) / 100, inputs: loanCalcForm.value }, null, 2)
}
const applyLoan = async () => handle('loanApply', base + '/api/loans/apply', loanApplyForm.value)
</script>

<template>
  <div class="legacy">
    <h2>貸款</h2>
    <form @submit.prevent="calcLoan">
      <input v-model.number="loanCalcForm.amount" name="amount" placeholder="貸款金額" type="number" />
      <input v-model.number="loanCalcForm.years" name="years" placeholder="年數" type="number" />
      <input v-model.number="loanCalcForm.rate" name="rate" placeholder="年利率 (%)" type="number" step="0.01" />
      <button type="submit">貸款試算</button>
    </form>
    <pre>{{ results.loanCalc }}</pre>

    <form @submit.prevent="applyLoan">
      <input v-model="loanApplyForm.user_id" name="user_id" placeholder="使用者 ID" />
      <input v-model.number="loanApplyForm.amount" name="amount" placeholder="貸款金額" type="number" />
      <button type="submit">申請貸款</button>
    </form>
    <pre>{{ results.loanApply }}</pre>
  </div>
</template>

<style scoped>
pre { background:#f6f8fa; padding:10px; overflow:auto }
input, select, button { margin:4px 0; display:block }
</style>
