import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { setupRouterGuards } from './guards'

const routes: RouteRecordRaw[] = [
  // 官網首頁
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomePage.vue'),
    meta: {
      requiresAuth: false,
      title: '首頁',
      description: '富邦網路銀行官網首頁',
    },
  },

  // 認證路由
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/modules/auth/views/LoginPage.vue'),
    meta: {
      requiresAuth: false,
      title: '登入',
      description: '用戶登入頁面',
    },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/modules/auth/views/RegisterPage.vue'),
    meta: {
      requiresAuth: false,
      title: '註冊',
      description: '新用戶註冊頁面',
    },
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('@/modules/auth/views/ForgotPasswordPage.vue'),
    meta: {
      requiresAuth: false,
      title: '忘記密碼',
      description: '密碼重置頁面',
    },
  },
  {
    path: '/select-services',
    name: 'SelectServices',
    component: () => import('@/modules/auth/views/ServiceSelection.vue'),
    meta: {
      requiresAuth: true,
      title: '選擇服務',
      description: '登入後的服務功能選擇',
    },
  },

  // 主應用路由
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/modules/dashboard/views/DashboardPage.vue'),
    meta: {
      requiresAuth: true,
      title: '儀表板',
      description: '用戶儀表板首頁',
      icon: 'dashboard',
    },
  },

  // 帳戶路由
  {
    path: '/accounts',
    name: 'Accounts',
    component: () => import('@/modules/accounts/views/AccountListPage.vue'),
    meta: {
      requiresAuth: true,
      title: '帳戶管理',
      description: '帳戶列表頁面',
      icon: 'account',
      menuVisible: true,
    },
  },
  {
    path: '/accounts/:id',
    name: 'AccountDetail',
    component: () => import('@/modules/accounts/views/AccountDetailPage.vue'),
    meta: {
      requiresAuth: true,
      title: '帳戶詳情',
      description: '帳戶詳細資訊',
    },
  },
  {
    path: '/accounts/open/new',
    name: 'OpenAccount',
    component: () => import('@/modules/accounts/views/OpenAccountPage.vue'),
    meta: {
      requiresAuth: true,
      title: '開立帳戶',
      description: '開立新帳戶頁面',
    },
  },

  // 交易路由
  {
    path: '/transactions',
    name: 'Transactions',
    component: () => import('@/modules/transactions/views/TransferPage.vue'),
    meta: {
      requiresAuth: true,
      title: '轉帳',
      description: '轉帳頁面',
      icon: 'transfer',
      menuVisible: true,
    },
  },
  {
    path: '/transactions/history',
    name: 'TransactionHistory',
    component: () => import('@/modules/transactions/views/HistoryPage.vue'),
    meta: {
      requiresAuth: true,
      title: '交易紀錄',
      description: '交易歷史記錄',
      icon: 'history',
      menuVisible: true,
    },
  },
  {
    path: '/transactions/exchange',
    name: 'Exchange',
    component: () => import('@/modules/transactions/views/ExchangePage.vue'),
    meta: {
      requiresAuth: true,
      title: '換匯',
      description: '外幣兌換頁面',
      icon: 'exchange',
      menuVisible: true,
    },
  },

  // 信用卡路由
  {
    path: '/cards',
    name: 'Cards',
    component: () => import('@/modules/creditcards/views/CardListPage.vue'),
    meta: {
      requiresAuth: true,
      title: '信用卡',
      description: '信用卡列表頁面',
      icon: 'creditcard',
      menuVisible: true,
    },
  },
  {
    path: '/cards/:id',
    name: 'CardDetail',
    component: () => import('@/modules/creditcards/views/CardDetailPage.vue'),
    meta: {
      requiresAuth: true,
      title: '信用卡詳情',
      description: '信用卡詳細資訊',
    },
  },
  {
    path: '/cards/apply',
    name: 'ApplyCard',
    component: () => import('@/modules/creditcards/views/ApplyCardPage.vue'),
    meta: {
      requiresAuth: true,
      title: '申請信用卡',
      description: '信用卡申請頁面',
    },
  },

  // 投資理財路由
  {
    path: '/investments',
    redirect: '/investments/funds',
  },
  {
    path: '/investments/funds',
    name: 'Funds',
    component: () => import('@/modules/investments/views/FundPage.vue'),
    meta: {
      requiresAuth: true,
      title: '基金',
      description: '基金投資頁面',
      icon: 'fund',
      menuVisible: true,
      category: 'investments',
    },
  },
  {
    path: '/investments/stocks',
    name: 'Stocks',
    component: () => import('@/modules/investments/views/StockPage.vue'),
    meta: {
      requiresAuth: true,
      title: '股票',
      description: '股票投資頁面',
      icon: 'stock',
      menuVisible: true,
      category: 'investments',
    },
  },
  {
    path: '/investments/insurance',
    name: 'Insurance',
    component: () => import('@/modules/investments/views/InsurancePage.vue'),
    meta: {
      requiresAuth: true,
      title: '保險',
      description: '保險產品頁面',
      icon: 'insurance',
      menuVisible: true,
      category: 'investments',
    },
  },

  // 貸款路由
  {
    path: '/loans',
    name: 'Loans',
    component: () => import('@/modules/loans/views/LoansPage.vue'),
    meta: {
      requiresAuth: true,
      title: '貸款',
      description: '貸款管理頁面',
      icon: 'loan',
      menuVisible: true,
    },
  },

  // 生活繳費路由
  {
    path: '/utilities',
    name: 'Utilities',
    component: () => import('@/modules/utilities/views/UtilitiesPage.vue'),
    meta: {
      requiresAuth: true,
      title: '生活繳費',
      description: '生活繳費服務頁面',
      icon: 'utility',
      menuVisible: true,
    },
  },
  {
    path: '/utilities/bills',
    name: 'UtilityBills',
    component: () => import('@/modules/utilities/views/BillsPage.vue'),
    meta: {
      requiresAuth: true,
      title: '繳費帳單',
      description: '繳費帳單列表',
    },
  },
  {
    path: '/utilities/history',
    name: 'UtilityHistory',
    component: () => import('@/modules/utilities/views/HistoryPage.vue'),
    meta: {
      requiresAuth: true,
      title: '繳費紀錄',
      description: '繳費歷史記錄',
    },
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
    meta: {
      requiresAuth: true,
      title: '個人資料',
      description: '編輯個人資料',
      icon: 'profile',
      menuVisible: false,
    },
  },
  {
    path: '/settings/security',
    name: 'SettingsSecurity',
    component: () => import('@/modules/settings/views/SecurityPage.vue'),
    meta: {
      requiresAuth: true,
      title: '安全設定',
      description: '帳戶安全設定',
      icon: 'security',
      menuVisible: false,
    },
  },
  {
    path: '/settings/preferences',
    name: 'SettingsPreferences',
    component: () => import('@/modules/settings/views/PreferencesPage.vue'),
    meta: {
      requiresAuth: true,
      title: '偏好設定',
      description: '用戶偏好設定',
      icon: 'preferences',
      menuVisible: false,
    },
  },

  // 404 頁面
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFoundPage.vue'),
    meta: {
      title: '找不到頁面',
      description: '404 - 頁面不存在',
    },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0, left: 0 }
    }
  },
})

// 初始化路由守衛
setupRouterGuards(router)
// 導出路由實例和工具函數
export default router

export { useRouter } from 'vue-router'
export type { RouteLocationNormalized } from 'vue-router'