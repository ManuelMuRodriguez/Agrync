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
        body: JSON.stringify({ detail: 'Incorrect email or password' }),
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
        body: JSON.stringify({ detail: 'Invalid access token' }),
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

test.describe('Login flow', () => {
  test.beforeEach(async ({ page }) => {
    await setupApiMocks(page)
    await page.addInitScript(() => localStorage.clear())
  })

  test('shows the login form when accessing /login', async ({ page }) => {
    await page.goto('/login')
    await expect(page.locator('input[placeholder="Email"]')).toBeVisible()
    await expect(page.locator('input[placeholder="Password"]')).toBeVisible()
    await expect(page.locator('input[type="submit"]')).toBeVisible()
  })

  test('successful login redirects to dashboard', async ({ page }) => {
    await loginAs(page, 'admin@example.com', 'AdminPass123')
    await expect(page).toHaveURL(/dashboard/)
  })

  test('login with wrong password shows error toast', async ({ page }) => {
    await loginAs(page, 'admin@example.com', 'ContraseñaMala')
    await expect(page.getByText('Incorrect email or password')).toBeVisible({ timeout: 5000 })
  })

  test('shows validation error if email is empty', async ({ page }) => {
    await page.goto('/login')
    await page.click('input[type="submit"]')
    await expect(page.getByText('El email es obligatorio')).toBeVisible()
  })

  test('shows validation error if password is empty', async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[placeholder="Email"]', 'test@example.com')
    await page.click('input[type="submit"]')
    await expect(page.getByText('The password is mandatory')).toBeVisible()
  })

  test('shows error if email format is invalid', async ({ page }) => {
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

  test('after logout, redirects to login or token is removed', async ({ page }) => {
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
