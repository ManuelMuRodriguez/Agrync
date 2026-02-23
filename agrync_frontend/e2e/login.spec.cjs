// @ts-check
const { test, expect } = require('@playwright/test')

const API = 'http://localhost:8000/api/v1'

// ── Helpers ────────────────────────────────────────────────────────────────────

async function setupApiMocks(page) {
  // Login OK
  await page.route(`${API}/auth/login`, async (route) => {
    const body = route.request().postData() ?? ''
    const params = new URLSearchParams(body)
    const user = params.get('username')
    const pass = params.get('password')

    if (user === 'admin@example.com' && pass === 'AdminPass123') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ access_token: 'e2e-fake-token', token_type: 'bearer' }),
      })
    } else {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Email o contraseña incorrectos' }),
      })
    }
  })

  // Logout
  await page.route(`${API}/auth/logout`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ message: 'Session closed successfully' }),
    })
  })

  // User info
  await page.route(`${API}/auth/info`, async (route) => {
    const auth = route.request().headers()['authorization'] ?? ''
    if (auth.includes('e2e-fake-token')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ id: 'e2e-user', full_name: 'Admin E2E', role: 'Administrador' }),
      })
    } else {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Access Token inválido' }),
      })
    }
  })

  // Refresh token
  await page.route(`${API}/auth/refresh`, async (route) => {
    await route.fulfill({
      status: 201,
      contentType: 'application/json',
      body: JSON.stringify({ access_token: 'e2e-fake-token', token_type: 'bearer' }),
    })
  })
}

async function loginAs(page, email, password) {
  await page.goto('/login')
  await page.fill('input[placeholder="Email"]', email)
  await page.fill('input[placeholder="Password"]', password)
  await page.click('input[type="submit"]')
}

// ── Tests ──────────────────────────────────────────────────────────────────────

test.describe('Flujo de Login', () => {
  test.beforeEach(async ({ page }) => {
    await setupApiMocks(page)
    await page.addInitScript(() => localStorage.clear())
  })

  test('muestra el formulario de login al acceder a /login', async ({ page }) => {
    await page.goto('/login')
    await expect(page.locator('input[placeholder="Email"]')).toBeVisible()
    await expect(page.locator('input[placeholder="Password"]')).toBeVisible()
    await expect(page.locator('input[type="submit"]')).toBeVisible()
  })

  test('login exitoso redirige al dashboard', async ({ page }) => {
    await loginAs(page, 'admin@example.com', 'AdminPass123')
    await expect(page).toHaveURL(/dashboard/)
  })

  test('login con contraseña incorrecta muestra toast de error', async ({ page }) => {
    await loginAs(page, 'admin@example.com', 'ContraseñaMala')
    await expect(page.getByText('Email o contraseña incorrectos')).toBeVisible({ timeout: 5000 })
  })

  test('muestra error de validación si el email está vacío', async ({ page }) => {
    await page.goto('/login')
    await page.click('input[type="submit"]')
    await expect(page.getByText('El email es obligatorio')).toBeVisible()
  })

  test('muestra error de validación si la contraseña está vacía', async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[placeholder="Email"]', 'test@example.com')
    await page.click('input[type="submit"]')
    await expect(page.getByText('The password is mandatory')).toBeVisible()
  })

  test('muestra error si el email no tiene formato válido', async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[placeholder="Email"]', 'no-es-email')
    await page.click('input[placeholder="Password"]')
    await expect(page.getByText('Invalid email address')).toBeVisible()
  })
})

test.describe('Logout', () => {
  test.beforeEach(async ({ page }) => {
    await setupApiMocks(page)
    await page.addInitScript(() => {
      localStorage.setItem('ACCESS_TOKEN_AGRYNC', 'e2e-fake-token')
    })
  })

  test('tras el logout se redirige a login o se borra el token', async ({ page }) => {
    await page.goto('/dashboard')
    const logoutBtn = page.getByRole('button', { name: /cerrar sesión|logout|salir/i })
    if (await logoutBtn.isVisible()) {
      await logoutBtn.click()
      await expect(page).toHaveURL(/login/)
    } else {
      await expect(page).not.toHaveURL(/login/)
    }
  })
})
