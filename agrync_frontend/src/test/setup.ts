import "@testing-library/jest-dom";
import { server } from "./mocks/server";

// Levanta el servidor MSW antes de todos los tests
beforeAll(() => server.listen({ onUnhandledRequest: "warn" }));
// Resetea handlers sobreescritos por cada test
afterEach(() => server.resetHandlers());
// Cierra el servidor al terminar
afterAll(() => server.close());
