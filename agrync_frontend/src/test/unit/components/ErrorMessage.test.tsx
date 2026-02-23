import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import ErrorMessage from '../../../components/ErrorMessage'

describe('ErrorMessage', () => {
  it('renderiza el texto pasado como children', () => {
    render(<ErrorMessage>El email es obligatorio</ErrorMessage>)
    expect(screen.getByText('El email es obligatorio')).toBeInTheDocument()
  })

  it('renderiza un elemento <p>', () => {
    const { container } = render(<ErrorMessage>Error</ErrorMessage>)
    expect(container.querySelector('p')).not.toBeNull()
  })

  it('puede renderizar contenido JSX como children', () => {
    render(
      <ErrorMessage>
        <span>Error en el campo</span>
      </ErrorMessage>
    )
    expect(screen.getByText('Error en el campo')).toBeInTheDocument()
  })

  it('no renderiza nada visible si children está vacío', () => {
    const { container } = render(<ErrorMessage>{''}</ErrorMessage>)
    expect(container.querySelector('p')?.textContent?.trim()).toBe('')
  })
})
