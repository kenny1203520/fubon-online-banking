<script setup lang="ts">
import { ref, computed, onMounted, type Ref } from 'vue'
import { useApi } from '../composables/useApi'

const { token, setToken, getToken, api, base } = useApi()
const authStatus = computed(() => token.value ? '已登入（有 token）' : '未登入')
onMounted(() => { token.value = localStorage.getItem('token') })

const openAccountForm = ref({ full_name: '', id_number: '', email: '', initial_deposit: 0 })
const ccForm = ref({ full_name: '', id_number: '', annual_income: 0, card_type: '' })
const registerForm = ref({ username: '', password: '', email: '' })
const loginForm = ref({ username: '', password: '' })

type Results = { openAccount: Ref<string>, cc: Ref<string>, register: Ref<string>, login: Ref<string> }
const results: Results = { openAccount: ref(''), cc: ref(''), register: ref(''), login: ref('') }

const handle = async (which: keyof Results, path: string, data: any) => {
  const res = await api(path, data)
  results[which].value = JSON.stringify(res, null, 2)
  return res
}

const openAccount = async () => handle('openAccount', base + '/api/accounts/open', openAccountForm.value)
const applyCard = async () => handle('cc', base + '/api/creditcards/apply', ccForm.value)
const registerUser = async () => handle('register', base + '/api/users/register', registerForm.value)
const loginUser = async () => {
  const res = await handle('login', base + '/api/users/login', loginForm.value)
  if (res && (res as any).status === 200 && (res as any).body?.token) {
    setToken((res as any).body.token)
  }
}
const logoutUser = async () => {
  const res = await api(base + '/api/users/logout', {})
  setToken(null)
  results.login.value = JSON.stringify(res, null, 2)
}
</script>

<template>
  <div class="legacy">
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
  </div>
</template>

<style scoped>
pre { background:#f6f8fa; padding:10px; overflow:auto }
input, select, button { margin:4px 0; display:block }
nav a { margin-right:8px }
</style>
