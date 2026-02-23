import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import VariableCard from '../../../components/VariableCard'
import { TestWrapper } from '../../mocks/wrapper'
import type { VariableAtributes, LastDataCard, GenericDevice, User, Role } from '../../../types'

// Mock react-toastify
vi.mock('react-toastify', () => ({
  toast: { error: vi.fn(), success: vi.fn() },
}))

// Mock write API
vi.mock('../../../api/WriteValueAPI', () => ({
  writeValue: vi.fn().mockResolvedValue({ message: 'Valor modificado correctamente' }),
}))

const defaultVariable: VariableAtributes = {
  name: 'Temperatura',
  type: 'Float32',
  decimals: 2,
  writable: false,
  scaling: null,
  min_value: null,
  max_value: null,
  unit: 'ºC',
}

const defaultLastValue: LastDataCard = {
  value: 23.45,
  timestamp: '2024-06-15T10:30:00.000Z',
}

function renderCard(
  variable: Partial<VariableAtributes> = {},
  lastValue: Partial<LastDataCard> = {},
  role: Role = 'Administrador'
) {
  return render(
    <VariableCard
      variable={{ ...defaultVariable, ...variable }}
      last_value={{ ...defaultLastValue, ...lastValue }}
      deviceName={'Sensor-01' as GenericDevice['name']}
      deviceType={'Modbus'}
      userId={'user-id-1' as User['id']}
      role={role}
    />,
    { wrapper: TestWrapper }
  )
}

describe('VariableCard', () => {
  beforeEach(() => vi.clearAllMocks())

  describe('Muestra información básica', () => {
    it('muestra el nombre de la variable', () => {
      renderCard()
      expect(screen.getByText('Temperatura')).toBeInTheDocument()
    })

    it('muestra el tipo de la variable', () => {
      renderCard()
      expect(screen.getByText(/Float32/)).toBeInTheDocument()
    })

    it('muestra el valor actual', () => {
      renderCard()
      expect(screen.getByText(/23\.45/)).toBeInTheDocument()
    })

    it('muestra la unidad de la variable', () => {
      renderCard()
      expect(screen.getByText(/ºC/)).toBeInTheDocument()
    })

    it('muestra "--" si el valor es null', () => {
      renderCard({}, { value: null })
      expect(screen.getByText('--')).toBeInTheDocument()
    })

    it('muestra el scaling si está definido', () => {
      renderCard({ scaling: 0.001 })
      expect(screen.getByText(/Scaling: 0\.001/)).toBeInTheDocument()
    })

    it('no muestra scaling si es null', () => {
      renderCard({ scaling: null })
      expect(screen.queryByText(/Scaling/)).toBeNull()
    })

    it('renderiza sin errores cuando min y max están definidos', () => {
      // Component accepts min_value/max_value without displaying them as fixed text
      renderCard({ min_value: 0, max_value: 100 })
      // Component still renders name and value
      expect(screen.getByText('Temperatura')).toBeInTheDocument()
      expect(screen.getByText('23.45')).toBeInTheDocument()
    })
  })

  describe('Formato de timestamp', () => {
    it('convierte UTC a hora de Madrid correctamente', () => {
      // 2024-06-15T10:30:00Z → Madrid (UTC+2 in summer) → 12:30:00
      renderCard()
      expect(screen.getByText(/Timestamp:/)).toBeInTheDocument()
      expect(screen.getByText(/12:30:00/)).toBeInTheDocument()
    })

    it('muestra "Not available" si timestamp es null', () => {
      renderCard({}, { timestamp: null })
      expect(screen.getByText(/Not available/)).toBeInTheDocument()
    })

    it('muestra "Not available" si timestamp es inválido', () => {
      renderCard({}, { timestamp: 'fecha-invalida' })
      expect(screen.getByText(/Not available/)).toBeInTheDocument()
    })
  })

  describe('Formulario de escritura', () => {
    it('no muestra el formulario si la variable no es writable', () => {
      renderCard({ writable: false })
      expect(screen.queryByPlaceholderText('New Value')).toBeNull()
    })

    it('muestra el formulario si la variable es writable', () => {
      renderCard({ writable: true })
      expect(screen.getByPlaceholderText('New Value')).toBeInTheDocument()
    })

    it('el input está deshabilitado para rol Lector', () => {
      renderCard({ writable: true }, {}, 'Lector')
      const input = screen.getByPlaceholderText('New Value')
      expect(input).toBeDisabled()
    })

    it('el input está habilitado para rol Administrador', () => {
      renderCard({ writable: true }, {}, 'Administrador')
      const input = screen.getByPlaceholderText('New Value')
      expect(input).not.toBeDisabled()
    })

    it('el botón Modificar está deshabilitado para Lector', () => {
      renderCard({ writable: true }, {}, 'Lector')
      expect(screen.getByDisplayValue('Modify')).toBeDisabled()
    })

    it('muestra error si se envía el formulario vacío', async () => {
      const user = userEvent.setup()
      renderCard({ writable: true })
      await user.click(screen.getByDisplayValue('Modify'))
      await waitFor(() => {
        expect(screen.getByText('Value is required')).toBeInTheDocument()
      })
    })

    it('muestra error si el valor no es un número', async () => {
      const user = userEvent.setup()
      renderCard({ writable: true })
      await user.type(screen.getByPlaceholderText('New Value'), 'abc')
      await user.click(screen.getByDisplayValue('Modify'))
      await waitFor(() => {
        expect(screen.getByText('Must be a number')).toBeInTheDocument()
      })
    })

    it('acepta valores negativos', async () => {
      const user = userEvent.setup()
      renderCard({ writable: true })
      const input = screen.getByPlaceholderText('New Value')
      await user.type(input, '-15.3')
      // Should not show a format error
      await user.click(screen.getByDisplayValue('Modify'))
      await waitFor(() => {
        expect(screen.queryByText('Must be a number')).toBeNull()
      })
    })
  })
})
