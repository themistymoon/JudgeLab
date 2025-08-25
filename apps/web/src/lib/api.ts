import axios, { AxiosError, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import Cookies from 'js-cookie'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Create axios instance with better defaults
export const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  timeout: 30000, // Increased timeout for file uploads
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - add auth token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = Cookies.get('judgelab-token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    console.error('Request interceptor error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor - handle common errors
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    // Handle network errors
    if (!error.response) {
      console.error('Network error:', error.message)
      return Promise.reject({
        ...error,
        message: 'Network error. Please check your connection.',
      })
    }

    const { status } = error.response

    switch (status) {
      case 401:
        // Token expired or invalid
        Cookies.remove('judgelab-token')
        if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
          window.location.href = '/login'
        }
        break
      
      case 403:
        console.error('Forbidden: Insufficient permissions')
        break
      
      case 404:
        console.error('Resource not found')
        break
      
      case 422:
        console.error('Validation error:', error.response.data)
        break
      
      case 429:
        console.error('Rate limit exceeded')
        break
      
      case 500:
      case 502:
      case 503:
      case 504:
        console.error('Server error:', status)
        break
      
      default:
        console.error('API error:', error.response.data)
    }

    return Promise.reject(error)
  }
)

export default api