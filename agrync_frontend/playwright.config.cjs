// CommonJS config para compatibilidad con Node 18.18
// (Playwright requiere Node 18.19+ para cargar .ts/.mjs)
const { defineConfig, devices } = require('@playwright/test')

module.exports = defineConfig({
  testDir: './e2e',
  testMatch: '**/*.spec.{js,cjs,ts}',
  timeout: 30_000,
  expect: { timeout: 5_000 },
  fullyParallel: false,
  retries: 0,
  reporter: 'list',

  use: {
    baseURL: 'http://localhost:5173',
    headless: true,
    extraHTTPHeaders: {},
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  // Levanta el servidor de Vite automáticamente antes de los tests E2E
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 30_000,
    env: {
      VITE_API_URL: 'http://localhost:8000/api/v1',
    },
  },
})
