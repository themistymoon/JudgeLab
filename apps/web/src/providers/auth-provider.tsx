'use client'

import React, { createContext, useContext, useEffect, useState } from 'react'
import Cookies from 'js-cookie'
import { api } from '@/lib/api'

export interface User {
  id: number
  email: string
  display_name: string
  role: 'STUDENT' | 'AUTHOR' | 'ADMIN'
  is_active: boolean
  created_at: string
}

interface AuthContextType {
  user: User | null
  token: string | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  register: (email: string, display_name: string, password: string) => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const abortController = new AbortController()
    
    // Check for existing token on mount
    const savedToken = Cookies.get('judgelab-token')
    if (savedToken) {
      setToken(savedToken)
      // Verify token and get user info
      api.get('/auth/me', {
        headers: { Authorization: `Bearer ${savedToken}` },
        signal: abortController.signal
      }).then(response => {
        if (!abortController.signal.aborted) {
          setUser(response.data)
        }
      }).catch(() => {
        if (!abortController.signal.aborted) {
          // Token is invalid, remove it
          Cookies.remove('judgelab-token')
          setToken(null)
        }
      }).finally(() => {
        if (!abortController.signal.aborted) {
          setIsLoading(false)
        }
      })
    } else {
      setIsLoading(false)
    }

    return () => {
      abortController.abort()
    }
  }, [])

  const login = async (email: string, password: string) => {
    const formData = new FormData()
    formData.append('username', email)
    formData.append('password', password)
    
    const response = await api.post('/auth/token', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    
    const { access_token, user: userData } = response.data
    
    setToken(access_token)
    setUser(userData)
    Cookies.set('judgelab-token', access_token, { 
      expires: 7, // 7 days
      secure: window.location.protocol === 'https:',
      sameSite: 'strict'
    })
  }

  const logout = () => {
    setUser(null)
    setToken(null)
    Cookies.remove('judgelab-token')
  }

  const register = async (email: string, display_name: string, password: string) => {
    const response = await api.post('/auth/register', {
      email,
      display_name,
      password
    })
    
    const { access_token, user: userData } = response.data
    
    setToken(access_token)
    setUser(userData)
    Cookies.set('judgelab-token', access_token, { 
      expires: 7,
      secure: window.location.protocol === 'https:',
      sameSite: 'strict'
    })
  }

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, logout, register }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}