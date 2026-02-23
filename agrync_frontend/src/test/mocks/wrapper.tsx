/**
 * Wrapper de proveedores para usarlo con Testing Library:
 *   render(<Component />, { wrapper: TestWrapper })
 */
import React from 'react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MantineProvider } from '@mantine/core'

export function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })
}

type Props = { children: React.ReactNode }

export function TestWrapper({ children }: Props) {
  const queryClient = createTestQueryClient()
  return (
    <QueryClientProvider client={queryClient}>
      <MantineProvider>
        <MemoryRouter>{children}</MemoryRouter>
      </MantineProvider>
    </QueryClientProvider>
  )
}
