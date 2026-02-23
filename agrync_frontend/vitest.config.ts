import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react-swc";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "happy-dom",
    globals: true,
    setupFiles: "./src/test/setup.ts",
    css: false,
    include: ["src/test/unit/**/*.{test,spec}.{ts,tsx}"],
    env: {
      VITE_API_URL: "http://localhost:8000/api/v1",
    },
    coverage: {
      provider: "v8",
      reporter: ["text", "html"],
      include: [
        "src/components/**",
        "src/pages/**",
        "src/hooks/**",
        "src/api/**",
      ],
      exclude: ["src/test/**"],
    },
  },
});
