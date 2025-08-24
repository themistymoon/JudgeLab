import { render, screen } from '@testing-library/react'
import { Navigation } from '../navigation'

// Mock next/link
jest.mock('next/link', () => {
  return ({ children, href }: { children: React.ReactNode; href: string }) => {
    return <a href={href}>{children}</a>
  }
})

// Mock the auth hook
jest.mock('../../hooks/use-auth', () => ({
  useAuth: () => ({
    user: null,
    logout: jest.fn(),
  })
}))

describe('Navigation', () => {
  it('renders JudgeLab logo', () => {
    render(<Navigation />)
    expect(screen.getByText('JudgeLab')).toBeInTheDocument()
  })

  it('shows sign in and get started buttons when not authenticated', () => {
    render(<Navigation />)
    expect(screen.getByText('Sign in')).toBeInTheDocument()
    expect(screen.getByText('Get Started')).toBeInTheDocument()
  })

  it('shows navigation links when authenticated', () => {
    // Mock authenticated user
    jest.doMock('../../hooks/use-auth', () => ({
      useAuth: () => ({
        user: {
          id: 1,
          email: 'test@example.com',
          display_name: 'Test User',
          role: 'STUDENT'
        },
        logout: jest.fn(),
      })
    }))

    render(<Navigation />)
    expect(screen.getByText('Problems')).toBeInTheDocument()
    expect(screen.getByText('Submissions')).toBeInTheDocument()
    expect(screen.getByText('Leaderboard')).toBeInTheDocument()
  })
})