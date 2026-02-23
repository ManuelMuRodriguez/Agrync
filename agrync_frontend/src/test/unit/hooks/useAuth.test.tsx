import { describe, it, expect, vi } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useAuth } from '../../../hooks/useAuth'
import { createTestQueryClient } from '../../mocks/wrapper'
import { QueryClientProvider } from '@tanstack/react-query'
import React from 'react'
import { server } from '../../mocks/server'
import { http, HttpResponse } from 'msw'

// Store the token before each test
function setupToken(token: string | null) {
  if (token) {
    localStorage.setItem('ACCESS_TOKEN_AGRYNC', token)
  } else {
    localStorage.removeItem('ACCESS_TOKEN_AGRYNC')
  }
}

function wrapper({ children }: { children: React.ReactNode }) {
  const queryClient = createTestQueryClient()
  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
}

describe('useAuth', () => {
  it('returns user data when the token is valid', async () => {
    setupToken('fake-access-token')
    const { result } = renderHook(() => useAuth(), { wrapper })

    expect(result.current.isLoading).toBe(true)

    await waitFor(() => expect(result.current.isLoading).toBe(false))

    expect(result.current.data).toMatchObject({
      id: 'user-id-123',
      full_name: 'Admin Test',
      role: 'Administrador',
    })
    expect(result.current.isError).toBe(false)
  })

  it('returns isError=true when the token is invalid', async () => {
    setupToken('invalid-token')

    // Override the handler to return 401
    server.use(
      http.get('http://localhost:8000/api/v1/auth/info', () =>
        HttpResponse.json({ detail: 'Invalid access token' }, { status: 401 })
      )
    )

    const { result } = renderHook(() => useAuth(), { wrapper })
    await waitFor(() => expect(result.current.isLoading).toBe(false))

    expect(result.current.isError).toBe(true)
    expect(result.current.data).toBeUndefined()
  })

  it('returns isError=true without a token', async () => {
    setupToken(null)

    server.use(
      http.get('http://localhost:8000/api/v1/auth/info', () =>
        HttpResponse.json({ detail: 'Access token not found' }, { status: 401 })
      )
    )

    const { result } = renderHook(() => useAuth(), { wrapper })
    await waitFor(() => expect(result.current.isLoading).toBe(false))

    expect(result.current.isError).toBe(true)
  })
})
