import "@testing-library/jest-dom";
import { vi } from "vitest";
import { server } from "./mocks/server";

vi.mock("react-i18next", async () => {
  const en = (await import("../i18n/locales/en.json")).default as Record<string, unknown>;

  function resolveKey(key: string, opts?: Record<string, unknown>): string {
    const parts = key.split(".");
    let val: unknown = en;
    for (const part of parts) {
      if (!val || typeof val !== "object") return key;
      val = (val as Record<string, unknown>)[part];
    }
    let str = typeof val === "string" ? val : key;
    if (opts) {
      str = Object.entries(opts).reduce(
        (acc, [k, v]) => acc.replace(new RegExp(`{{${k}}}`, "g"), String(v)),
        str
      );
    }
    return str;
  }

  return {
    useTranslation: () => ({
      t: (key: string, opts?: Record<string, unknown>) => resolveKey(key, opts),
      i18n: { language: "en", changeLanguage: vi.fn() },
    }),
    initReactI18next: { type: "3rdParty", init: vi.fn() },
    Trans: ({ children }: { children: unknown }) => children,
  };
});

// Start the MSW server before all tests
beforeAll(() => server.listen({ onUnhandledRequest: "warn" }));
// Reset any overridden handlers after each test
afterEach(() => server.resetHandlers());
// Close the server after all tests
afterAll(() => server.close());
