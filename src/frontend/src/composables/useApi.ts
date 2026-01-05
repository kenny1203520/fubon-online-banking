import { ref } from 'vue'

const token = ref<string | null>(localStorage.getItem('token'))
const setToken = (t: string | null) => { token.value = t; if (t) localStorage.setItem('token', t); else localStorage.removeItem('token') }
const getToken = () => token.value

const base = (import.meta.env.VITE_API_BASE as string) || 'http://localhost:5000'

/**
 * Simple API helper that supports GET and POST.
 * - `path` should be full URL or relative path appended to `base` by callers.
 * - If `method` is omitted, it defaults to 'POST' when `data` is provided, otherwise 'GET'.
 */
const api = async (path: string, data?: any, method?: 'GET' | 'POST') => {
    const resolvedMethod = method || (data !== undefined && data !== null ? 'POST' : 'GET')
    const headers: Record<string, string> = { 'Content-Type': 'application/json' }
    const t = getToken()
    if (t) headers['Authorization'] = 'Bearer ' + t
    try {
        let url = path
        let body: string | undefined
        if (resolvedMethod === 'GET' && data) {
            const qs = new URLSearchParams()
            Object.keys(data).forEach(k => { if (data[k] !== undefined && data[k] !== null && data[k] !== '') qs.append(k, String(data[k])) })
            url += (url.includes('?') ? '&' : '?') + qs.toString()
        } else if (resolvedMethod === 'POST') {
            body = JSON.stringify(data || {})
        }
        const res = await fetch(url, { method: resolvedMethod, headers, body })
        try { const js = await res.json(); return { status: res.status, body: js } } catch { return { status: res.status } }
    } catch (e: any) { return { error: e?.message || String(e) } }
}

export function useApi() {
    return { token, setToken, getToken, api, base }
}

export default useApi
