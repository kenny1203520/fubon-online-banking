<script setup lang="ts">
import { ref, onMounted, type Ref } from 'vue'
import { useApi } from '../composables/useApi'

const { token, setToken, getToken, api, base } = useApi()
const balanceForm = ref({ account_id: '' })
const txHistoryForm = ref({ account_id: '', from: '', to: '' })
const transferForm = ref({ from_account: '', to_account: '', amount: 0, currency: 'TWD' })
const cashlessForm = ref({ account_id: '', enabled: false })

type Results = { balance: Ref<string>, txHistory: Ref<string>, transfer: Ref<string>, cashless: Ref<string> }
const results: Results = { balance: ref(''), txHistory: ref(''), transfer: ref(''), cashless: ref('') }

const handle = async (which: keyof Results, path: string, data: any) => {
  const res = await api(path, data)
  results[which].value = JSON.stringify(res, null, 2)
  return res
}

const queryBalance = async () => handle('balance', base + '/api/accounts/balance', balanceForm.value)
const queryTxHistory = async () => handle('txHistory', base + '/api/accounts/transactions', txHistoryForm.value)
const doTransfer = async () => handle('transfer', base + '/api/accounts/transfer', transferForm.value)
const updateCashless = async () => handle('cashless', base + '/api/accounts/cashless_withdraw', cashlessForm.value)
</script>

<template>
  <div class="legacy">
    <h2>交易功能</h2>
    <h3>餘額查詢</h3>
    <form @submit.prevent="queryBalance">
      <input v-model="balanceForm.account_id" name="account_id" placeholder="帳戶 ID" required />
      <button type="submit">查詢餘額</button>
    </form>
    <pre>{{ results.balance }}</pre>

    <h3>交易紀錄查詢</h3>
    <form @submit.prevent="queryTxHistory">
      <input v-model="txHistoryForm.account_id" name="account_id" placeholder="帳戶 ID" required />
      <input v-model="txHistoryForm.from" name="from" placeholder="從 (YYYY-MM-DD)" />
      <input v-model="txHistoryForm.to" name="to" placeholder="到 (YYYY-MM-DD)" />
      <button type="submit">查詢交易紀錄</button>
    </form>
    <pre>{{ results.txHistory }}</pre>

    <h3>轉帳（臺幣 / 外幣）</h3>
    <form @submit.prevent="doTransfer">
      <input v-model="transferForm.from_account" name="from_account" placeholder="來源帳戶 ID" required />
      <input v-model="transferForm.to_account" name="to_account" placeholder="目標帳戶 ID" required />
      <input v-model.number="transferForm.amount" name="amount" placeholder="金額" type="number" required />
      <select v-model="transferForm.currency" name="currency">
        <option value="TWD">TWD</option>
        <option value="USD">USD</option>
        <option value="JPY">JPY</option>
      </select>
      <button type="submit">送出轉帳</button>
    </form>
    <pre>{{ results.transfer }}</pre>

    <h3>無卡提款設定 / 換匯 / 定存 / 國外匯款 / 支票 / 悠遊卡綁定</h3>
    <p>下列項目已建立 UI 骨架，示範提交方式；後端若未實作路由會回傳錯誤訊息。</p>
    <form @submit.prevent="updateCashless">
      <input v-model="cashlessForm.account_id" name="account_id" placeholder="帳戶 ID" />
      <label><input v-model="cashlessForm.enabled" name="enabled" type="checkbox" /> 啟用無卡提款</label>
      <button type="submit">更新設定</button>
    </form>
    <pre>{{ results.cashless }}</pre>
  </div>
</template>

<style scoped>
pre { background:#f6f8fa; padding:10px; overflow:auto }
input, select, button { margin:4px 0; display:block }
nav a { margin-right:8px }
</style>
