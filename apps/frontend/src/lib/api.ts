import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Token storage helpers
const ACCESS_TOKEN_KEY = 'leadforix_access_token'
const REFRESH_TOKEN_KEY = 'leadforix_refresh_token'
const WORKSPACE_ID_KEY = 'leadforix_workspace_id'

export const tokenStorage = {
  getAccessToken: () => localStorage.getItem(ACCESS_TOKEN_KEY),
  getRefreshToken: () => localStorage.getItem(REFRESH_TOKEN_KEY),
  getWorkspaceId: () => localStorage.getItem(WORKSPACE_ID_KEY),
  setTokens: (accessToken: string, refreshToken: string) => {
    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken)
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken)
  },
  setWorkspaceId: (workspaceId: string) => {
    localStorage.setItem(WORKSPACE_ID_KEY, workspaceId)
  },
  clear: () => {
    localStorage.removeItem(ACCESS_TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
    localStorage.removeItem(WORKSPACE_ID_KEY)
  },
}

// Request Interceptor: Attach Auth & Workspace context
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = tokenStorage.getAccessToken()
  if (token) {
    config.headers.set('Authorization', `Bearer ${token}`)
  }

  const workspaceId = tokenStorage.getWorkspaceId()
  if (workspaceId) {
    config.headers.set('X-Workspace-ID', workspaceId)
  }

  return config
})

// Response Interceptor: 401 Refresh Token Queue
let isRefreshing = false
let failedQueue: Array<{
  resolve: (value?: unknown) => void
  reject: (reason?: unknown) => void
}> = []

const processQueue = (error: AxiosError | null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve()
    }
  })
  failedQueue = []
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    // If unauthorized and not already retried
    if (error.response?.status === 401 && !originalRequest._retry) {
      // Avoid looping if the refresh endpoint itself failed
      if (originalRequest.url?.includes('/api/auth/refresh')) {
        tokenStorage.clear()
        window.location.href = '/login'
        return Promise.reject(error)
      }

      const refreshToken = tokenStorage.getRefreshToken()
      if (!refreshToken) {
        tokenStorage.clear()
        window.location.href = '/login'
        return Promise.reject(error)
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then(() => apiClient(originalRequest))
          .catch((err) => Promise.reject(err))
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const response = await axios.post<{
          access_token: string
          refresh_token: string
        }>('/api/auth/refresh', { refresh_token: refreshToken })

        const { access_token, refresh_token } = response.data
        tokenStorage.setTokens(access_token, refresh_token)

        originalRequest.headers.set('Authorization', `Bearer ${access_token}`)
        processQueue(null)
        return apiClient(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError as AxiosError)
        tokenStorage.clear()
        window.location.href = '/login'
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)
