import apiClient from '@/shared/services/api'
import type {
  DashboardData,
  DashboardSummary,
  AccountSummary,
  RecentTransaction,
  Notification
} from '../types'

export const dashboardService = {
  /**
   * 取得儀表板完整資料
   */
  getDashboardData: () => 
    apiClient.get<DashboardData>('/dashboard'),
  
  /**
   * 取得儀表板摘要
   */
  getSummary: () => 
    apiClient.get<DashboardSummary>('/dashboard/summary'),
  
  /**
   * 取得帳戶概覽
   */
  getAccounts: () => 
    apiClient.get<AccountSummary[]>('/dashboard/accounts'),
  
  /**
   * 取得最近交易
   */
  getRecentTransactions: (limit: number = 10) => 
    apiClient.get<RecentTransaction[]>('/dashboard/transactions/recent', {
      params: { limit }
    }),
  
  /**
   * 取得通知
   */
  getNotifications: () => 
    apiClient.get<Notification[]>('/dashboard/notifications'),
  
  /**
   * 標記通知為已讀
   */
  markNotificationAsRead: (notificationId: number) => 
    apiClient.put(`/dashboard/notifications/${notificationId}/read`),
  
  /**
   * 標記所有通知為已讀
   */
  markAllNotificationsAsRead: () => 
    apiClient.put('/dashboard/notifications/read-all'),
}
