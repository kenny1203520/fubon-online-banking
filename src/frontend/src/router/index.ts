import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/modules/auth/stores/auth'

const routes: RouteRecordRaw[] = [
  // 官網首頁
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomePage.vue'),
    meta: { requiresAuth: false },
  },

  // 認證路由
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/modules/auth/views/LoginPage.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/modules/auth/views/RegisterPage.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('@/modules/auth/views/ForgotPasswordPage.vue'),
    meta: { requiresAuth: false },
  },

  // 主應用路由
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/modules/dashboard/views/DashboardPage.vue'),
    meta: { requiresAuth: true },
  },

  // 帳戶路由
  {
    path: '/accounts',
    name: 'Accounts',
    component: () => import('@/modules/accounts/views/AccountListPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/accounts/:id',
    name: 'AccountDetail',
    component: () => import('@/modules/accounts/views/AccountDetailPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/accounts/open/new',
    name: 'OpenAccount',
    component: () => import('@/modules/accounts/views/OpenAccountPage.vue'),
    meta: { requiresAuth: true },
  },

  // 交易路由
  {
    path: '/transactions',
    name: 'Transactions',
    component: () => import('@/modules/transactions/views/TransferPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/transactions/history',
    name: 'TransactionHistory',
    component: () => import('@/modules/transactions/views/HistoryPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/transactions/exchange',
    name: 'Exchange',
    component: () => import('@/modules/transactions/views/ExchangePage.vue'),
    meta: { requiresAuth: true },
  },

  // 信用卡路由
  {
    path: '/cards',
    name: 'Cards',
    component: () => import('@/modules/creditcards/views/CardListPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/cards/:id',
    name: 'CardDetail',
    component: () => import('@/modules/creditcards/views/CardDetailPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/cards/apply',
    name: 'ApplyCard',
    component: () => import('@/modules/creditcards/views/ApplyCardPage.vue'),
    meta: { requiresAuth: true },
  },

  // 投資理財路由
  {
    path: '/investments',
    name: 'Investments',
    component: () => import('@/modules/investments/views/FundPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/investments/funds',
    name: 'Funds',
    component: () => import('@/modules/investments/views/FundPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/investments/stocks',
    name: 'Stocks',
    component: () => import('@/modules/investments/views/StockPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/investments/insurance',
    name: 'Insurance',
    component: () => import('@/modules/investments/views/InsurancePage.vue'),
    meta: { requiresAuth: true },
  },

  // 貸款路由
  {
    path: '/loans',
    name: 'Loans',
    component: () => import('@/modules/loans/views/LoansPage.vue'),
    meta: { requiresAuth: true },
  },

  // 設定路由
  {
    path: '/settings',
    redirect: '/settings/profile',
  },
  {
    path: '/settings/profile',
    name: 'SettingsProfile',
    component: () => import('@/modules/settings/views/ProfilePage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/settings/security',
    name: 'SettingsSecurity',
    component: () => import('@/modules/settings/views/SecurityPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/settings/preferences',
    name: 'SettingsPreferences',
    component: () => import('@/modules/settings/views/PreferencesPage.vue'),
    meta: { requiresAuth: true },
  },

  // 404 頁面
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFoundPage.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  },
})

// 路由守衛
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.meta.requiresAuth !== false

  if (requiresAuth && !authStore.isAuthenticated) {
    // 重定向到登入頁
    next({
      name: 'Login',
      query: { redirect: to.fullPath },
    })
  } else if (!requiresAuth && authStore.isAuthenticated) {
    // 如果已登入且訪問認證頁，重定向到儀表板
    if (to.path.startsWith('/login') || to.path.startsWith('/register')) {
      next('/dashboard')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
