import axios from 'axios'
import { useAuthStore } from '../store/authStore'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request Interceptor: Add Auth Token
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response Interceptor: Handle 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authApi = {
  login: async (username: string, password: string) => {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)

    const response = await api.post('/api/v1/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },

  getCurrentUser: async () => {
    const response = await api.get('/api/v1/auth/me')
    return response.data
  },

  changePassword: async (oldPassword: string, newPassword: string) => {
    const response = await api.post('/api/v1/auth/password/change', {
      old_password: oldPassword,
      new_password: newPassword,
    })
    return response.data
  },
}

// Patients API
export const patientsApi = {
  list: async (skip = 0, limit = 100) => {
    const response = await api.get(`/api/v1/patients?skip=${skip}&limit=${limit}`)
    return response.data
  },

  get: async (id: number) => {
    const response = await api.get(`/api/v1/patients/${id}`)
    return response.data
  },

  create: async (data: any) => {
    const response = await api.post('/api/v1/patients', data)
    return response.data
  },

  update: async (id: number, data: any) => {
    const response = await api.put(`/api/v1/patients/${id}`, data)
    return response.data
  },

  delete: async (id: number) => {
    const response = await api.delete(`/api/v1/patients/${id}`)
    return response.data
  },
}
