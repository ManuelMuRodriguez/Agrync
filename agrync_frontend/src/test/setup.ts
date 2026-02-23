import "@testing-library/jest-dom";
import { server } from "./mocks/server";

// Start the MSW server before all tests
beforeAll(() => server.listen({ onUnhandledRequest: "warn" }));
// Reset any overridden handlers after each test
afterEach(() => server.resetHandlers());
// Close the server after all tests
afterAll(() => server.close());
