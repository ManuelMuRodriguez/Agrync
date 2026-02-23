// @ts-check
const { test, expect } = require('@playwright/test')

const API = 'http://localhost:8000/api/v1'

async function setupApiMocks(page, isAuthenticated) {
  await page.route(`${API}/auth/info`, async (route) => {
    if (isAuthenticated) {
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

  await page.route(`${API}/auth/refresh`, async (route) => {
    if (isAuthenticated) {
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({ access_token: 'e2e-fake-token', token_type: 'bearer' }),
      })
    } else {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Refresh Token inválido' }),
      })
    }
  })
}

test.describe('Rutas protegidas', () => {
  test('sin autenticación, acceder a /dashboard redirige a login o muestra la página', async ({ page }) => {
    await page.addInitScript(() => localStorage.clear())
    await setupApiMocks(page, false)
    await page.goto('/dashboard')

    await page.waitForURL(/.+/, { timeout: 5000 })
    const url = page.url()

    const isOnLogin = url.includes('login')
    const loginForm = await page.locator('input[placeholder="Email"]').isVisible()
    expect(isOnLogin || loginForm).toBe(true)
  })

  test('con token válido, el dashboard carga correctamente', async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.setItem('ACCESS_TOKEN_AGRYNC', 'e2e-fake-token')
    })
    await setupApiMocks(page, true)
    await page.goto('/dashboard')

    await page.waitForURL(/.+/, { timeout: 5000 })
    expect(page.url()).not.toContain('login')
  })

  test('la página de login es accesible sin autenticación', async ({ page }) => {
    await page.addInitScript(() => localStorage.clear())
    await setupApiMocks(page, false)
    await page.goto('/login')
    await expect(page.locator('input[placeholder="Email"]')).toBeVisible()
  })

  test('la página crear-password es accesible sin autenticación', async ({ page }) => {
    await page.addInitScript(() => localStorage.clear())
    await setupApiMocks(page, false)
    await page.goto('/crear-password')
    await expect(page.locator('form')).toBeVisible()
  })
})
