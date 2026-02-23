import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Login from '../../../pages/Login'
import { TestWrapper } from '../../mocks/wrapper'

vi.mock('react-toastify', () => ({
  toast: { error: vi.fn(), success: vi.fn() },
}))

// Mock de la API - verificamos que se llama con los datos correctos
const mockLogin = vi.fn()
vi.mock('../../../api/AuthAPI', () => ({
  login: (...args: unknown[]) => mockLogin(...args),
  getUserInfo: vi.fn(),
}))

// Mock de navigate
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return { ...actual as object, useNavigate: () => mockNavigate }
})

function renderLogin() {
  return render(<Login />, { wrapper: TestWrapper })
}

describe('Login', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockLogin.mockResolvedValue({ access_token: 'fake-token', token_type: 'bearer' })
  })

  describe('Renderizado inicial', () => {
    it('muestra el campo de email', () => {
      renderLogin()
      expect(screen.getByPlaceholderText('Email')).toBeInTheDocument()
    })

    it('muestra el campo de contraseña', () => {
      renderLogin()
      expect(screen.getByPlaceholderText('Password')).toBeInTheDocument()
    })

    it('muestra el botón de submit', () => {
      renderLogin()
      expect(screen.getByRole('button', { name: /iniciar sesión/i })).toBeInTheDocument()
    })
  })

  describe('Validación del formulario', () => {
    it('muestra error si el email está vacío al hacer submit', async () => {
      const user = userEvent.setup()
      renderLogin()
      await user.click(screen.getByRole('button', { name: /iniciar sesión/i }))
      await waitFor(() => {
        expect(screen.getByText('El email es obligatorio')).toBeInTheDocument()
      })
    })

    it('muestra error si la contraseña está vacía al hacer submit', async () => {
      const user = userEvent.setup()
      renderLogin()
      await user.click(screen.getByRole('button', { name: /iniciar sesión/i }))
      await waitFor(() => {
        expect(screen.getByText('The password is mandatory')).toBeInTheDocument()
      })
    })

    it('muestra error si el email no tiene formato válido', async () => {
      const user = userEvent.setup()
      renderLogin()
      await user.type(screen.getByPlaceholderText('Email'), 'no-es-un-email')
      await user.tab()
      await waitFor(() => {
        expect(screen.getByText(/Invalid email address/i)).toBeInTheDocument()
      })
    })

    it('no muestra error si el email tiene formato válido', async () => {
      const user = userEvent.setup()
      renderLogin()
      await user.type(screen.getByPlaceholderText('Email'), 'test@example.com')
      await user.tab()
      await waitFor(() => {
        expect(screen.queryByText(/Invalid email address/i)).toBeNull()
      })
    })
  })

  describe('Submit con datos válidos', () => {
    it('llama a login con los datos del formulario', async () => {
      const user = userEvent.setup()
      renderLogin()
      await user.type(screen.getByPlaceholderText('Email'), 'admin@example.com')
      await user.type(screen.getByPlaceholderText('Password'), 'AdminPass123')
      await user.click(screen.getByRole('button', { name: /iniciar sesión/i }))
      await waitFor(() => {
        expect(mockLogin).toHaveBeenCalledWith({
          username: 'admin@example.com',
          password: 'AdminPass123',
        })
      })
    })

    it('no llama a login si hay errores de validación', async () => {
      const user = userEvent.setup()
      renderLogin()
      // Solo rellenamos email para dejar password vacío
      await user.type(screen.getByPlaceholderText('Email'), 'admin@example.com')
      await user.click(screen.getByRole('button', { name: /iniciar sesión/i }))
      await waitFor(() => {
        expect(mockLogin).not.toHaveBeenCalled()
      })
    })
  })
})
