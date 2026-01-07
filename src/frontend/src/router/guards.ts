import type { Router, RouteLocationNormalized, NavigationGuardNext } from 'vue-router'
import { useAuthStore } from '@/modules/auth/stores/auth'

type AuthStore = ReturnType<typeof useAuthStore>

/**
 * 路由守衛類型定義
 */
export interface RouteGuardContext {
  to: RouteLocationNormalized
  from: RouteLocationNormalized
  next: NavigationGuardNext
  authStore: AuthStore
}

/**
 * 檢查用戶是否已認證
 */
export function isAuthenticated(): boolean {
  const authStore = useAuthStore()
  return authStore.isAuthenticated
}

/**
 * 檢查用戶是否有特定權限
 */
export function hasPermission(permission: string): boolean {
  const authStore = useAuthStore()
  const permissions = (authStore as unknown as { permissions?: string[] }).permissions
  return permissions?.includes(permission) || false
}

/**
 * 檢查用戶角色
 */
export function hasRole(role: string): boolean {
  const authStore = useAuthStore()
  const userRole = (authStore.user as unknown as { role?: string } | null)?.role
  return userRole === role
}

/**
 * 認證守衛：檢查用戶是否登入
 */
export function authGuard({ to, next, authStore }: RouteGuardContext) {
  const meta = to.meta as Record<string, unknown>
  const requiresAuth = meta.requiresAuth !== false

  if (requiresAuth && !authStore.isAuthenticated) {
    // 保存重定向位置
    sessionStorage.setItem('redirect', to.fullPath)
    next({
      name: 'Login',
      query: { redirect: to.fullPath },
    })
    return false
  }
  return true
}

/**
 * 公開路由守衛：已認證的用戶重定向到儀表板
 */
export function publicRouteGuard({ to, next, authStore }: RouteGuardContext) {
  const meta = to.meta as Record<string, unknown>
  const isPublicRoute = meta.requiresAuth === false

  if (isPublicRoute && authStore.isAuthenticated) {
    // 已登入用戶訪問認證頁面，重定向到儀表板
    if (to.name === 'Login' || to.name === 'Register' || to.name === 'ForgotPassword') {
      next('/dashboard')
      return false
    }
  }
  return true
}

/**
 * 角色守衛：檢查用戶角色
 */
export function roleGuard({ to, next, authStore }: RouteGuardContext) {
  const meta = to.meta as Record<string, unknown>
  const requiredRole = meta.requiredRole as string | undefined

  if (requiredRole) {
    const userRole = (authStore.user as unknown as { role?: string } | null)?.role
    if (!userRole || userRole !== requiredRole) {
      next('/dashboard')
      return false
    }
  }
  return true
}

/**
 * 權限守衛：檢查用戶權限
 */
export function permissionGuard({ to, next, authStore }: RouteGuardContext) {
  const meta = to.meta as Record<string, unknown>
  const requiredPermissions = meta.requiredPermissions as string[] | undefined

  if (requiredPermissions && Array.isArray(requiredPermissions)) {
    const userPermissions = (authStore as unknown as { permissions?: string[] }).permissions || []
    const hasAllPermissions = requiredPermissions.every((perm: string) =>
      userPermissions.includes(perm)
    )

    if (!hasAllPermissions) {
      next('/dashboard')
      return false
    }
  }
  return true
}

/**
 * 頁面標題守衛：設置頁面標題
 */
export function titleGuard({ to }: RouteGuardContext) {
  const meta = to.meta as Record<string, unknown>
  const baseTitle = '富邦網路銀行'

  if (meta.title) {
    document.title = `${meta.title as string} - ${baseTitle}`
  } else {
    document.title = baseTitle
  }
}

/**
 * 加載進度守衛
 */
export function progressGuard({ to, from }: RouteGuardContext) {
  // 可以在這裡集成進度條邏輯
  // 例如：NProgress.start()
  const currentTime = new Date().getTime()
  console.log(`[Navigation] From ${from.path || '(initial)'} to ${to.path} at ${currentTime}`)
}

/**
 * 安全檢查守衛：防止重複提交、異常狀態等
 */
export function securityGuard({ authStore }: RouteGuardContext) {
  // 檢查 Token 是否過期
  const isTokenExpired = (authStore as unknown as { isTokenExpired?: boolean }).isTokenExpired
  if (isTokenExpired && authStore.isAuthenticated) {
    authStore.logout()
    return false
  }

  return true
}

/**
 * 初始化所有路由守衛
 */
export function setupRouterGuards(router: Router) {
  router.beforeEach((to, from, next) => {
    const authStore = useAuthStore()

    const context = { to, from, next, authStore }

    // 執行安全檢查
    if (!securityGuard(context)) {
      next('/login')
      return
    }

    // 設置頁面標題
    titleGuard(context)

    // 記錄路由導航
    progressGuard(context)

    // 檢查認證
    if (!authGuard(context)) {
      return
    }

    // 檢查公開路由
    if (!publicRouteGuard(context)) {
      return
    }

    // 檢查角色
    if (!roleGuard(context)) {
      return
    }

    // 檢查權限
    if (!permissionGuard(context)) {
      return
    }

    next()
  })

  // 路由後置鉤子
  router.afterEach(() => {
    // 可以在這裡進行頁面加載完成後的操作
    // 例如：NProgress.done()
    window.scrollTo(0, 0)
  })

  // 路由錯誤處理
  router.onError((error) => {
    console.error('Router error:', error)
  })
}

/**
 * 檢查是否可以導航到特定路由
 */
export function canNavigate(routePath: string, authStore: AuthStore): boolean {
  const publicRoutes = ['/login', '/register', '/forgot-password', '/']

  if (publicRoutes.includes(routePath)) {
    return true
  }

  return authStore.isAuthenticated
}

/**
 * 獲取重定向位置
 */
export function getRedirectPath(defaultPath: string = '/dashboard'): string {
  const redirect = sessionStorage.getItem('redirect')
  if (redirect) {
    sessionStorage.removeItem('redirect')
    return redirect
  }
  return defaultPath
}
