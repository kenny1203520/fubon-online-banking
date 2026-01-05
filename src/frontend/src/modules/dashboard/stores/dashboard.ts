import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { dashboardService } from '../services/dashboard'
import type {
  DashboardData,
  DashboardSummary,
  AccountSummary,
  RecentTransaction,
  Notification
} from '../types'

export const useDashboardStore = defineStore('dashboard', () => {
  // State
  const dashboardData = ref<DashboardData | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const lastRefreshed = ref<Date | null>(null)

  // Computed
  const summary = computed(() => dashboardData.value?.summary || null)
  const accounts = computed(() => dashboardData.value?.accounts || [])
  const recentTransactions = computed(() => dashboardData.value?.recent_transactions || [])
  const cards = computed(() => dashboardData.value?.cards || [])
  const investment = computed(() => dashboardData.value?.investment || null)
  const notifications = computed(() => dashboardData.value?.notifications || [])
  
  const unreadNotifications = computed(() => 
    notifications.value.filter(n => !n.read)
  )
  
  const unreadCount = computed(() => unreadNotifications.value.length)
  
  const totalAssets = computed(() => summary.value?.total_assets || 0)
  const totalLiabilities = computed(() => summary.value?.total_liabilities || 0)
  const netWorth = computed(() => summary.value?.net_worth || 0)

  // Actions
  /**
   * 取得儀表板完整資料
   */
  const fetchDashboardData = async () => {
    isLoading.value = true
    error.value = null

    try {
      const response = await dashboardService.getDashboardData()
      dashboardData.value = response.data
      lastRefreshed.value = new Date()
    } catch (err) {
      const message = err instanceof Error ? err.message : '取得儀表板資料失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 取得儀表板摘要
   */
  const fetchSummary = async () => {
    isLoading.value = true
    error.value = null

    try {
      const response = await dashboardService.getSummary()
      if (dashboardData.value) {
        dashboardData.value.summary = response.data
      }
      return response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : '取得摘要失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 取得最近交易
   */
  const fetchRecentTransactions = async (limit: number = 10) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await dashboardService.getRecentTransactions(limit)
      if (dashboardData.value) {
        dashboardData.value.recent_transactions = response.data
      }
      return response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : '取得最近交易失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 取得通知
   */
  const fetchNotifications = async () => {
    error.value = null

    try {
      const response = await dashboardService.getNotifications()
      if (dashboardData.value) {
        dashboardData.value.notifications = response.data
      }
      return response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : '取得通知失敗'
      error.value = message
      throw new Error(message)
    }
  }

  /**
   * 標記通知為已讀
   */
  const markNotificationAsRead = async (notificationId: number) => {
    try {
      await dashboardService.markNotificationAsRead(notificationId)
      // 更新本地狀態
      if (dashboardData.value) {
        const notification = dashboardData.value.notifications.find(n => n.id === notificationId)
        if (notification) {
          notification.read = true
        }
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : '標記失敗'
      error.value = message
      throw new Error(message)
    }
  }

  /**
   * 標記所有通知為已讀
   */
  const markAllNotificationsAsRead = async () => {
    try {
      await dashboardService.markAllNotificationsAsRead()
      // 更新本地狀態
      if (dashboardData.value) {
        dashboardData.value.notifications.forEach(n => n.read = true)
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : '標記失敗'
      error.value = message
      throw new Error(message)
    }
  }

  /**
   * 刷新儀表板資料
   */
  const refresh = async () => {
    await fetchDashboardData()
  }

  /**
   * 清空錯誤訊息
   */
  const clearError = () => {
    error.value = null
  }

  /**
   * 重置狀態
   */
  const reset = () => {
    dashboardData.value = null
    error.value = null
    lastRefreshed.value = null
  }

  return {
    // State
    dashboardData,
    isLoading,
    error,
    lastRefreshed,
    
    // Computed
    summary,
    accounts,
    recentTransactions,
    cards,
    investment,
    notifications,
    unreadNotifications,
    unreadCount,
    totalAssets,
    totalLiabilities,
    netWorth,
    
    // Actions
    fetchDashboardData,
    fetchSummary,
    fetchRecentTransactions,
    fetchNotifications,
    markNotificationAsRead,
    markAllNotificationsAsRead,
    refresh,
    clearError,
    reset
  }
})
