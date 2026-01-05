<script setup lang="ts">
import { ref, computed, onMounted, type Ref } from 'vue'
import { useApi } from '../composables/useApi'

const { token, setToken, getToken, api, base } = useApi()

type Results = {
  openAccount: Ref<string>
  cc: Ref<string>
  register: Ref<string>
  login: Ref<string>
  balance: Ref<string>
  txHistory: Ref<string>
  transfer: Ref<string>
  cashless: Ref<string>
  invQuery: Ref<string>
  invPurchase: Ref<string>
  cardPay: Ref<string>
  cardCash: Ref<string>
  loanCalc: Ref<string>
  loanApply: Ref<string>
}

const results: Results = {
  openAccount: ref(''),
  cc: ref(''),
  register: ref(''),
  login: ref(''),
  balance: ref(''),
  txHistory: ref(''),
  transfer: ref(''),
  cashless: ref(''),
  invQuery: ref(''),
  invPurchase: ref(''),
  cardPay: ref(''),
  cardCash: ref(''),
  loanCalc: ref(''),
  loanApply: ref(''),
}

const authStatus = computed(() => token.value ? '已登入（有 token）' : '未登入')

onMounted(() => { token.value = localStorage.getItem('token') })

// form models
const openAccountForm = ref({ full_name: '', id_number: '', email: '', initial_deposit: 0 })
const ccForm = ref({ full_name: '', id_number: '', annual_income: 0, card_type: '' })
const registerForm = ref({ username: '', password: '', email: '' })
const loginForm = ref({ username: '', password: '' })
const balanceForm = ref({ account_id: '' })
const txHistoryForm = ref({ account_id: '', from: '', to: '' })
const transferForm = ref({ from_account: '', to_account: '', amount: 0, currency: 'TWD' })
const cashlessForm = ref({ account_id: '', enabled: false })
const invQueryForm = ref({ account_id: '' })
const invPurchaseForm = ref({ account_id: '', product_id: '', amount: 0 })
const cardPayForm = ref({ user_id: '', card_id: '', amount: 0 })
const cardCashForm = ref({ card_id: '', amount: 0 })
const loanCalcForm = ref({ amount: 0, years: 0, rate: 0 })
const loanApplyForm = ref({ user_id: '', amount: 0 })

const handle = async (which: keyof Results, path: string, data: any) => {
  const res = await api(path, data)
  results[which].value = JSON.stringify(res, null, 2)
  return res
}

const openAccount = async () => handle('openAccount', base + '/accounts/open', openAccountForm.value)
const applyCard = async () => handle('cc', base + '/creditcards/apply', ccForm.value)
const registerUser = async () => handle('register', base + '/users/register', registerForm.value)
const loginUser = async () => {
  const res = await handle('login', base + '/users/login', loginForm.value)
  if (res && (res as any).status === 200 && (res as any).body?.token) {
    setToken((res as any).body.token)
  }
}
const logoutUser = async () => {
  const res = await api(base + '/users/logout', {})
  setToken(null)
  results.login.value = JSON.stringify(res, null, 2)
}

const queryBalance = async () => handle('balance', base + '/accounts/balance', balanceForm.value)
const queryTxHistory = async () => handle('txHistory', base + '/accounts/transactions', txHistoryForm.value)
const doTransfer = async () => handle('transfer', base + '/accounts/transfer', transferForm.value)
const updateCashless = async () => handle('cashless', base + '/accounts/cashless_withdraw', cashlessForm.value)
const queryInv = async () => handle('invQuery', base + '/investments/query', invQueryForm.value)
const purchaseInv = async () => handle('invPurchase', base + '/investments/purchase', invPurchaseForm.value)
const payCard = async () => handle('cardPay', base + '/creditcards/pay', cardPayForm.value)
const cashCard = async () => handle('cardCash', base + '/creditcards/cash_advance', cardCashForm.value)
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
const applyLoan = async () => handle('loanApply', base + '/loans/apply', loanApplyForm.value)

</script>

<template>
  <div class="legacy">
    <h1>帳戶管理示範</h1>
    <nav>
      <router-link to="/">Home</router-link> |
      <router-link to="/about">About</router-link>
    </nav>

    <section id="accounts">
      <h2>帳戶管理</h2>
      <h3>線上開戶</h3>
      <form @submit.prevent="openAccount">
        <input v-model="openAccountForm.full_name" name="full_name" placeholder="全名" required />
        <input v-model="openAccountForm.id_number" name="id_number" placeholder="身分證號" required />
        <input v-model="openAccountForm.email" name="email" placeholder="email" />
        <input v-model.number="openAccountForm.initial_deposit" name="initial_deposit" placeholder="初始存款" type="number" />
        <button type="submit">送出申請</button>
      </form>
      <pre>{{ results.openAccount }}</pre>

      <h3>線上信用卡申請</h3>
      <form @submit.prevent="applyCard">
        <input v-model="ccForm.full_name" name="full_name" placeholder="全名" required />
        <input v-model="ccForm.id_number" name="id_number" placeholder="身分證號" required />
        <input v-model.number="ccForm.annual_income" name="annual_income" placeholder="年收入" type="number" />
        <input v-model="ccForm.card_type" name="card_type" placeholder="卡別 (e.g. gold)" />
        <button type="submit">申請</button>
      </form>
      <pre>{{ results.cc }}</pre>

      <h3>註冊網路銀行</h3>
      <form @submit.prevent="registerUser">
        <input v-model="registerForm.username" name="username" placeholder="帳號" required />
        <input v-model="registerForm.password" type="password" placeholder="密碼" required />
        <input v-model="registerForm.email" name="email" placeholder="email" />
        <button type="submit">註冊</button>
      </form>
      <pre>{{ results.register }}</pre>

      <h3>登入 / 登出</h3>
      <form @submit.prevent="loginUser">
        <input v-model="loginForm.username" name="username" placeholder="帳號" required />
        <input v-model="loginForm.password" type="password" placeholder="密碼" required />
        <button type="submit">登入</button>
      </form>
      <button v-if="token" @click="logoutUser">登出</button>
      <div id="auth-status">{{ authStatus }}</div>
      <pre>{{ results.login }}</pre>
    </section>

    <section id="transactions">
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
    </section>

    <section id="investments">
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
    </section>

    <section id="creditcards">
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
    </section>

    <section id="loans">
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
    </section>
  </div>
</template>

<style scoped>
pre { background:#f6f8fa; padding:10px; overflow:auto }
input, select, button { margin:4px 0; display:block }
nav a { margin-right:8px }
</style>
