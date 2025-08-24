import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import { Navigation } from '../navigation'
import * as authProvider from '../../providers/auth-provider'

// Mock next/link
jest.mock('next/link', () => {
  const MockLink = ({ children, href }: { children: React.ReactNode; href: string }) => {
    return <a href={href}>{children}</a>
  }
  MockLink.displayName = 'MockLink'
  return MockLink
})

// Mock the auth provider module
jest.mock('../../providers/auth-provider', () => ({
  useAuth: jest.fn()
}))

const mockUseAuth = authProvider.useAuth as jest.MockedFunction<typeof authProvider.useAuth>

describe('Navigation', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders JudgeLab logo', () => {
    mockUseAuth.mockReturnValue({
      user: null,
      logout: jest.fn(),
    })

    render(<Navigation />)
    expect(screen.getByText('JudgeLab')).toBeInTheDocument()
  })

  it('shows sign in and get started buttons when not authenticated', () => {
    mockUseAuth.mockReturnValue({
      user: null,
      logout: jest.fn(),
    })

    render(<Navigation />)
    expect(screen.getByText('Sign in')).toBeInTheDocument()
    expect(screen.getByText('Get Started')).toBeInTheDocument()
  })

  it('shows navigation links when authenticated', () => {
    mockUseAuth.mockReturnValue({
      user: {
        id: 1,
        email: 'test@example.com',
        display_name: 'Test User',
        role: 'STUDENT'
      },
      logout: jest.fn(),
    })

    render(<Navigation />)
    expect(screen.getByText('Problems')).toBeInTheDocument()
    expect(screen.getByText('Submissions')).toBeInTheDocument()
    expect(screen.getByText('Leaderboard')).toBeInTheDocument()
  })
})