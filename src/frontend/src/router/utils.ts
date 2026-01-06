import type { RouteRecordRaw, RouteLocationNormalized } from 'vue-router'
import { useAuthStore } from '@/modules/auth/stores/auth'

type AuthStore = ReturnType<typeof useAuthStore>

/**
 * 路由選單配置接口
 */
export interface MenuRoute {
  path: string
  name: string
  title: string
  icon?: string
  children?: MenuRoute[]
  menuVisible?: boolean
  requiresAuth?: boolean
}

/**
 * 路由元資料接口
 */
export interface RouteMeta {
  requiresAuth?: boolean
  title?: string
  description?: string
  icon?: string
  menuVisible?: boolean
  requiredRole?: string
  requiredPermissions?: string[]
  category?: string
  [key: string]: unknown
}

/**
 * 生成選單結構
 */
export function generateMenus(routes: RouteRecordRaw[]): MenuRoute[] {
  const menus: MenuRoute[] = []

  const processRoute = (route: RouteRecordRaw) => {
    if (!route.meta || route.meta.menuVisible === false) {
      return
    }

    const menu: MenuRoute = {
      path: route.path as string,
      name: route.name as string,
      title: (route.meta.title as string) || (route.name as string | undefined) || '',
      icon: route.meta.icon as string,
      menuVisible: route.meta.menuVisible !== false,
      requiresAuth: route.meta.requiresAuth !== false,
    }

    if (route.children && route.children.length > 0) {
      menu.children = route.children
        .map((child) => {
          if (!child.meta || child.meta.menuVisible === false) {
            return null
          }

          return {
            path: child.path as string,
            name: child.name as string,
            title: (child.meta.title as string) || child.name,
            icon: child.meta.icon as string,
            menuVisible: child.meta.menuVisible !== false,
            requiresAuth: child.meta.requiresAuth !== false,
          }
        })
        .filter((item) => item !== null) as MenuRoute[]
    }

    if (menu.children && menu.children.length === 0) {
      delete menu.children
    }

    menus.push(menu)
  }

  routes.forEach((route) => {
    processRoute(route)
  })

  return menus
}

/**
 * 按分類分組選單
 */
export function groupMenusByCategory(menus: MenuRoute[]): Record<string, MenuRoute[]> {
  const grouped: Record<string, MenuRoute[]> = {}

  menus.forEach((menu) => {
    const category = (menu as MenuRoute & { category?: string }).category || 'main'
    if (!grouped[category]) {
      grouped[category] = []
    }
    grouped[category].push(menu)
  })

  return grouped
}

/**
 * 根據路徑尋找路由
 */
export function findRouteByPath(
  routes: RouteRecordRaw[],
  path: string
): RouteRecordRaw | undefined {
  for (const route of routes) {
    if (route.path === path) {
      return route
    }

    if (route.children) {
      const found = findRouteByPath(route.children, path)
      if (found) {
        return found
      }
    }
  }

  return undefined
}

/**
 * 根據名稱尋找路由
 */
export function findRouteByName(
  routes: RouteRecordRaw[],
  name: string | symbol | undefined | null
): RouteRecordRaw | undefined {
  for (const route of routes) {
    if (route.name === name) {
      return route
    }

    if (route.children) {
      const found = findRouteByName(route.children, name)
      if (found) {
        return found
      }
    }
  }

  return undefined
}

/**
 * 檢查路由是否需要認證
 */
export function isProtectedRoute(meta?: RouteMeta): boolean {
  return meta?.requiresAuth !== false
}

/**
 * 檢查路由是否需要特定角色
 */
export function requiresRole(meta?: RouteMeta): string | undefined {
  return meta?.requiredRole
}

/**
 * 檢查路由是否需要特定權限
 */
export function requiresPermissions(meta?: RouteMeta): string[] | undefined {
  return meta?.requiredPermissions
}

/**
 * 獲取路由標題
 */
export function getRouteTitle(meta?: RouteMeta): string {
  return meta?.title || '富邦網路銀行'
}

/**
 * 獲取路由描述
 */
export function getRouteDescription(meta?: RouteMeta): string {
  return meta?.description || ''
}

/**
 * 獲取路由圖標
 */
export function getRouteIcon(meta?: RouteMeta): string | undefined {
  return meta?.icon
}

/**
 * 構建完整的面包屑路徑
 */
export function getBreadcrumbs(
  routes: RouteRecordRaw[],
  currentPath: string
): Array<{ name: string; path: string }> {
  const breadcrumbs: Array<{ name: string; path: string }> = []
  const paths = currentPath.split('/').filter((p) => p)

  let currentRoute = '/'
  breadcrumbs.push({ name: '首頁', path: '/' })

  for (const path of paths) {
    currentRoute += path + '/'
    const route = findRouteByPath(routes, '/' + currentRoute.slice(1).slice(0, -1))

    if (route && route.meta?.title) {
      breadcrumbs.push({
        name: route.meta.title as string,
        path: '/' + currentRoute.slice(1).slice(0, -1),
      })
    }
  }

  return breadcrumbs
}

/**
 * 檢查是否為外部連接
 */
export function isExternalLink(path: string): boolean {
  return /^(https?:|mailto:|tel:)/.test(path)
}

/**
 * 檢查路由是否在活動狀態
 */
export function isActiveRoute(currentPath: string, routePath: string): boolean {
  if (routePath === '/') {
    return currentPath === '/'
  }
  return currentPath.startsWith(routePath)
}

/**
 * 獲取路由的面包屑名稱
 */
export function getRouteBreadcrumbName(route: RouteRecordRaw): string {
  return (route.meta?.title as string) || (route.name as string) || route.path
}

/**
 * 驗證路由是否合法
 */
export function isValidRoute(route: RouteRecordRaw): boolean {
  return !!(route.name && route.component)
}

/**
 * 路由跳轉時的預檢查
 */
export function preCheckNavigation(
  to: RouteLocationNormalized,
  authStore: AuthStore
): { allowed: boolean; redirectTo?: string; message?: string } {
  // 檢查是否需要認證
  const meta = to.meta as Record<string, unknown>

  if (meta.requiresAuth && !authStore.isAuthenticated) {
    return {
      allowed: false,
      redirectTo: '/login',
      message: '需要登入才能訪問此頁面',
    }
  }

  // 檢查角色
  const requiredRole = meta.requiredRole as string | undefined
  const userRole = (authStore.user as unknown as { role?: string } | null)?.role
  if (requiredRole && userRole !== requiredRole) {
    return {
      allowed: false,
      redirectTo: '/dashboard',
      message: '您沒有權限訪問此頁面',
    }
  }

  // 檢查權限
  const requiredPermissions = meta.requiredPermissions as string[] | undefined
  if (requiredPermissions && Array.isArray(requiredPermissions)) {
    const permissions = (authStore as unknown as { permissions?: string[] }).permissions || []
    const hasPermissions = requiredPermissions.every((perm: string) =>
      permissions.includes(perm)
    )

    if (!hasPermissions) {
      return {
        allowed: false,
        redirectTo: '/dashboard',
        message: '您沒有足夠的權限訪問此頁面',
      }
    }
  }

  return { allowed: true }
}
