'use client'

import { useQuery } from 'react-query'
import { api } from '@/lib/api'
import Link from 'next/link'
import { ClockIcon, TagIcon } from '@heroicons/react/24/outline'

interface Problem {
  id: number
  slug: string
  title: string
  tags: string[]
  difficulty: 'EASY' | 'MEDIUM' | 'HARD' | 'EXPERT'
  created_at: string
}

export function ProblemList() {
  const { data: problems, isLoading, error } = useQuery<Problem[]>(
    'problems',
    async () => {
      const response = await api.get('/problems')
      return response.data
    }
  )

  if (isLoading) {
    return (
      <div className="space-y-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="card card-body animate-pulse">
            <div className="flex items-center justify-between">
              <div className="space-y-2">
                <div className="h-6 bg-gray-200 rounded w-64"></div>
                <div className="h-4 bg-gray-200 rounded w-32"></div>
              </div>
              <div className="h-6 bg-gray-200 rounded w-16"></div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="card card-body">
        <div className="text-center text-error-600">
          <p>Failed to load problems. Please try again later.</p>
        </div>
      </div>
    )
  }

  if (!problems || problems.length === 0) {
    return (
      <div className="card card-body">
        <div className="text-center text-gray-500">
          <p>No problems available yet. Check back later!</p>
        </div>
      </div>
    )
  }

  const getDifficultyClass = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'easy':
        return 'badge-easy'
      case 'medium':
        return 'badge-medium'
      case 'hard':
        return 'badge-hard'
      case 'expert':
        return 'badge-expert'
      default:
        return 'badge'
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Problems</h2>
        <div className="flex items-center space-x-4">
          {/* TODO: Add filters */}
          <span className="text-sm text-gray-500">
            {problems.length} problem{problems.length !== 1 ? 's' : ''}
          </span>
        </div>
      </div>

      <div className="space-y-4">
        {problems.map((problem) => (
          <Link key={problem.id} href={`/problems/${problem.slug}`}>
            <div className="card card-body hover:shadow-md transition-shadow cursor-pointer">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900 hover:text-primary-600">
                      {problem.title}
                    </h3>
                    <span className={`badge ${getDifficultyClass(problem.difficulty)}`}>
                      {problem.difficulty.charAt(0) + problem.difficulty.slice(1).toLowerCase()}
                    </span>
                  </div>
                  
                  {problem.tags && problem.tags.length > 0 && (
                    <div className="flex items-center space-x-2 mb-2">
                      <TagIcon className="h-4 w-4 text-gray-400" />
                      <div className="flex flex-wrap gap-2">
                        {problem.tags.map((tag, index) => (
                          <span
                            key={index}
                            className="inline-flex items-center px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  <div className="flex items-center text-sm text-gray-500">
                    <ClockIcon className="h-4 w-4 mr-1" />
                    <span>Added {new Date(problem.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
                
                <div className="flex items-center space-x-4">
                  {/* TODO: Add solved status, attempt count, etc. */}
                  <span className="text-primary-600 hover:text-primary-700 font-medium">
                    Solve →
                  </span>
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}