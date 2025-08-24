'use client'

import { useAuth } from '@/providers/auth-provider'
import { Navigation } from '@/components/navigation'
import { ProblemList } from '@/components/problem-list'
import { Hero } from '@/components/hero'

export default function Home() {
  const { user, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <main>
        {!user ? (
          <Hero />
        ) : (
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900">
                Welcome back, {user.display_name}!
              </h1>
              <p className="mt-2 text-gray-600">
                Ready to solve some problems?
              </p>
            </div>
            
            <ProblemList />
          </div>
        )}
      </main>
    </div>
  )
}