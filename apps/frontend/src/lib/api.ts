import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''
const DEFAULT_TIMEOUT_MS = 15000 // 15 seconds to prevent hanging requests

/**
 * In-Memory Token Manager
 *
 * Security Architecture (OWASP / XSS Defense):
 * 1. Short-lived Access Tokens are stored STRICTLY in memory (closure scope).
 *    They are never exposed to localStorage where rogue 3rd-party scripts can inspect them.
 * 2. Refresh Tokens are kept in memory with a scoped sessionStorage fallback,
 *    and withCredentials is enabled for seamless zero-code-change migration to httpOnly cookies.
 */
let inMemoryAccessToken: string | null = null
let inMemoryRefreshToken: string | null = null
let currentWorkspaceId: string | null = null

export const tokenStore = {
  getAccessToken: () => inMemoryAccessToken,
  setAccessToken: (token: string | null) => {
    inMemoryAccessToken = token
  },
  getRefreshToken: () => inMemoryRefreshToken || sessionStorage.getItem('lf_rt'),
  setRefreshToken: (token: string | null) => {
    inMemoryRefreshToken = token
    if (token) {
      sessionStorage.setItem('lf_rt', token)
    } else {
      sessionStorage.removeItem('lf_rt')
    }
  },
  getWorkspaceId: () => currentWorkspaceId || localStorage.getItem('lf_ws_id'),
  setWorkspaceId: (workspaceId: string | null) => {
    currentWorkspaceId = workspaceId
    if (workspaceId) {
      localStorage.setItem('lf_ws_id', workspaceId)
    } else {
      localStorage.removeItem('lf_ws_id')
    }
  },
  clear: () => {
    inMemoryAccessToken = null
    inMemoryRefreshToken = null
    currentWorkspaceId = null
    sessionStorage.removeItem('lf_rt')
    localStorage.removeItem('lf_ws_id')
  },
}

/**
 * Dedicated Raw HTTP Client for Auth Operations
 * - Shares the exact same baseURL and timeout
 * - Does NOT have the 401 refresh interceptor to prevent recursive loops
 */
export const authClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: DEFAULT_TIMEOUT_MS,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
})

/**
 * Main Application API Client
 */
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: DEFAULT_TIMEOUT_MS,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
})

/**
 * Event-driven SPA Auth Failure Listener
 * Avoids window.location.href which destroys React in-memory state and cache.
 */
type AuthFailureHandler = () => void
let authFailureHandlers: AuthFailureHandler[] = []

export const onAuthFailure = (handler: AuthFailureHandler) => {
  authFailureHandlers.push(handler)
  return () => {
    authFailureHandlers = authFailureHandlers.filter((h) => h !== handler)
  }
}

const notifyAuthFailure = () => {
  tokenStore.clear()
  if (authFailureHandlers.length > 0) {
    authFailureHandlers.forEach((handler) => handler())
  } else {
    // Fallback if no SPA listener is mounted yet
    window.location.replace('/login')
  }
}

// Request Interceptor: Attach Auth & Workspace context
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = tokenStore.getAccessToken()
  if (token) {
    config.headers.set('Authorization', `Bearer ${token}`)
  }

  const workspaceId = tokenStore.getWorkspaceId()
  if (workspaceId) {
    config.headers.set('X-Workspace-ID', workspaceId)
  }

  return config
})

// Concurrency Queue Architecture
interface QueuedRequest {
  resolve: (token: string) => void
  reject: (error: AxiosError | Error) => void
}

let isRefreshing = false
let failedQueue: QueuedRequest[] = []

const processQueue = (error: AxiosError | Error | null, token: string | null = null) => {
  failedQueue.forEach((promise) => {
    if (error) {
      promise.reject(error)
    } else if (token) {
      promise.resolve(token)
    }
  })
  failedQueue = []
}

// Response Interceptor: 401 Token Refresh Queue with Token Propagation
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    // If unauthorized and request has not already been retried
    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      // Abort if the refresh endpoint itself triggered a 401 to prevent recursion
      if (originalRequest.url?.includes('/api/auth/refresh')) {
        notifyAuthFailure()
        return Promise.reject(error)
      }

      const refreshToken = tokenStore.getRefreshToken()
      if (!refreshToken) {
        notifyAuthFailure()
        return Promise.reject(error)
      }

      // If a refresh is already in flight, queue this request until the fresh token resolves
      if (isRefreshing) {
        return new Promise<string>((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then((freshToken) => {
            // Patch the queued request's Authorization header with the newly acquired token
            originalRequest.headers.set('Authorization', `Bearer ${freshToken}`)
            return apiClient(originalRequest)
          })
          .catch((err) => Promise.reject(err))
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const response = await authClient.post<{
          access_token: string
          refresh_token: string
          token_type: string
          expires_in: number
        }>('/api/auth/refresh', {
          refresh_token: refreshToken,
        })

        const { access_token, refresh_token } = response.data
        tokenStore.setAccessToken(access_token)
        tokenStore.setRefreshToken(refresh_token)

        // Patch the current request with the new access token
        originalRequest.headers.set('Authorization', `Bearer ${access_token}`)

        // Propagate the new access token to all waiting queued requests
        processQueue(null, access_token)

        return apiClient(originalRequest)
      } catch (refreshError) {
        // Token reuse breach detected (RFC 6819) or expired refresh token
        processQueue(refreshError as AxiosError)
        notifyAuthFailure()
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)
