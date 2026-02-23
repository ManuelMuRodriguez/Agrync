import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import CrearPassword from '../../../pages/CreatePassword'
import { TestWrapper } from '../../mocks/wrapper'

vi.mock('react-toastify', () => ({
  toast: { error: vi.fn(), success: vi.fn() },
}))

const mockValidateUser = vi.fn()
vi.mock('../../../api/AuthAPI', () => ({
  validateUser: (...args: unknown[]) => mockValidateUser(...args),
  getUserInfo: vi.fn(),
}))

const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return { ...actual as object, useNavigate: () => mockNavigate }
})

function renderPage() {
  return render(<CrearPassword />, { wrapper: TestWrapper })
}

describe('CrearPassword', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockValidateUser.mockResolvedValue('Validación correcta')
  })

  describe('Renderizado', () => {
    it('muestra el campo de email', () => {
      renderPage()
      expect(screen.getByPlaceholderText(/email/i)).toBeInTheDocument()
    })

    it('muestra los campos de contraseña y confirmación', () => {
      renderPage()
      const passwordFields = screen.getAllByPlaceholderText(/password|contraseña/i)
      expect(passwordFields.length).toBeGreaterThanOrEqual(2)
    })
  })

  describe('Validación', () => {
    it('muestra error si el email está vacío', async () => {
      const user = userEvent.setup()
      renderPage()
      await user.click(screen.getByRole('button', { name: /activate user/i }))
      await waitFor(() => {
        expect(screen.getByText(/email/i)).toBeInTheDocument()
      })
    })

    it('muestra error si la contraseña está vacía', async () => {
      const user = userEvent.setup()
      renderPage()
      await user.type(screen.getByPlaceholderText(/^email$/i), 'test@example.com')
      await user.click(screen.getByRole('button', { name: /activate user/i }))
      await waitFor(() => {
        const errorMessages = screen.getAllByRole('paragraph').map(el => el.textContent)
        expect(errorMessages.some(m => m && m.trim().length > 0)).toBe(true)
      })
    })

    it('no llama a validateUser si hay errores de validación', async () => {
      const user = userEvent.setup()
      renderPage()
      await user.click(screen.getByRole('button', { name: /activate user/i }))
      await waitFor(() => expect(mockValidateUser).not.toHaveBeenCalled())
    })
  })
})
