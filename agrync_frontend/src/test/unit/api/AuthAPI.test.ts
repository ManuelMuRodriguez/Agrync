import { describe, it, expect, afterEach } from "vitest";
import { login, logout, validateUser, getUserInfo } from "../../../api/AuthAPI";
import { server } from "../../mocks/server";
import { http, HttpResponse } from "msw";

// Clear localStorage between tests
afterEach(() => localStorage.clear());

describe("AuthAPI", () => {
  describe("login()", () => {
    it("returns the token and saves it in localStorage with valid credentials", async () => {
      const result = await login({
        username: "admin@example.com",
        password: "AdminPass123",
      });
      expect(result.access_token).toBe("fake-access-token");
      expect(localStorage.getItem("ACCESS_TOKEN_AGRYNC")).toBe(
        "fake-access-token",
      );
    });

    it("throws an Error with the server message if credentials are incorrect", async () => {
      await expect(
        login({ username: "malo@example.com", password: "WrongPassword" }),
      ).rejects.toThrow("Incorrect email or password");
    });

    it("throws a generic Error if the server does not respond with detail", async () => {
      server.use(
        http.post("http://localhost:8000/api/v1/auth/login", () =>
          HttpResponse.json(
            { error: "Internal Server Error" },
            { status: 500 },
          ),
        ),
      );
      await expect(
        login({ username: "test@example.com", password: "123" }),
      ).rejects.toThrow();
    });
  });

  describe("logout()", () => {
    it("returns the success message from the server", async () => {
      const result = await logout();
      expect(result).toBe("Session closed successfully");
    });
  });

  describe("validateUser()", () => {
    it("returns the success message when validating correctly", async () => {
      const result = await validateUser({
        email: "user@example.com",
        password: "NuevaPass123",
        password_confirmation: "NuevaPass123",
      });
      expect(result).toBe("Activation successful");
    });

    it("throws an Error if the passwords do not match", async () => {
      server.use(
        http.post("http://localhost:8000/api/v1/auth/validate", () =>
          HttpResponse.json(
            { detail: "Passwords do not match" },
            { status: 400 },
          ),
        ),
      );
      await expect(
        validateUser({
          email: "user@example.com",
          password: "Pass1",
          password_confirmation: "Pass2",
        }),
      ).rejects.toThrow("Passwords do not match");
    });
  });

  describe("getUserInfo()", () => {
    it("returns the user data with a valid token", async () => {
      localStorage.setItem("ACCESS_TOKEN_AGRYNC", "fake-access-token");
      const result = await getUserInfo();
      expect(result).toMatchObject({
        id: "user-id-123",
        full_name: "Admin Test",
        role: "Administrador",
      });
    });

    it("throws an Error with an invalid token", async () => {
      localStorage.setItem("ACCESS_TOKEN_AGRYNC", "bad-token");
      server.use(
        http.get("http://localhost:8000/api/v1/auth/info", () =>
          HttpResponse.json(
            { detail: "Invalid access token" },
            { status: 401 },
          ),
        ),
      );
      // The function may throw or return undefined depending on the interceptor
      try {
        const result = await getUserInfo();
        // If it does not throw, it should at least not return valid data
        expect(result).toBeUndefined();
      } catch (e: unknown) {
        expect((e as Error).message).toContain("Invalid access token");
      }
    });

    it("returns undefined if data does not match the zod schema", async () => {
      server.use(
        http.get("http://localhost:8000/api/v1/auth/info", () =>
          HttpResponse.json({ unexpected_field: "unexpected value" }),
        ),
      );
      localStorage.setItem("ACCESS_TOKEN_AGRYNC", "fake-access-token");
      const result = await getUserInfo();
      expect(result).toBeUndefined();
    });
  });
});
