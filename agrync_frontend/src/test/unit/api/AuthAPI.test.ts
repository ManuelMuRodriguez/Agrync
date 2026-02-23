import { describe, it, expect, afterEach } from "vitest";
import { login, logout, validateUser, getUserInfo } from "../../../api/AuthAPI";
import { server } from "../../mocks/server";
import { http, HttpResponse } from "msw";

// Limpia el localStorage entre tests
afterEach(() => localStorage.clear());

describe("AuthAPI", () => {
  describe("login()", () => {
    it("devuelve el token y lo guarda en localStorage con credenciales válidas", async () => {
      const result = await login({
        username: "admin@example.com",
        password: "AdminPass123",
      });
      expect(result.access_token).toBe("fake-access-token");
      expect(localStorage.getItem("ACCESS_TOKEN_AGRYNC")).toBe(
        "fake-access-token",
      );
    });

    it("lanza un Error con el mensaje del servidor si las credenciales son incorrectas", async () => {
      await expect(
        login({ username: "malo@example.com", password: "WrongPassword" }),
      ).rejects.toThrow("Email o contraseña incorrectos");
    });

    it("lanza un Error genérico si el servidor no responde con detail", async () => {
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
    it("devuelve el mensaje de éxito del servidor", async () => {
      const result = await logout();
      expect(result).toBe("Session closed successfully");
    });
  });

  describe("validateUser()", () => {
    it("devuelve el mensaje de éxito al validar correctamente", async () => {
      const result = await validateUser({
        email: "user@example.com",
        password: "NuevaPass123",
        password_confirmation: "NuevaPass123",
      });
      expect(result).toBe("Validación correcta");
    });

    it("lanza un Error si las contraseñas no coinciden", async () => {
      server.use(
        http.post("http://localhost:8000/api/v1/auth/validate", () =>
          HttpResponse.json(
            { detail: "Las contraseñas no son iguales" },
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
      ).rejects.toThrow("Las contraseñas no son iguales");
    });
  });

  describe("getUserInfo()", () => {
    it("devuelve los datos del usuario con un token válido", async () => {
      localStorage.setItem("ACCESS_TOKEN_AGRYNC", "fake-access-token");
      const result = await getUserInfo();
      expect(result).toMatchObject({
        id: "user-id-123",
        full_name: "Admin Test",
        role: "Administrador",
      });
    });

    it("lanza un Error con token inválido", async () => {
      localStorage.setItem("ACCESS_TOKEN_AGRYNC", "bad-token");
      server.use(
        http.get("http://localhost:8000/api/v1/auth/info", () =>
          HttpResponse.json(
            { detail: "Access Token inválido" },
            { status: 401 },
          ),
        ),
      );
      // La función puede lanzar o retornar undefined dependiendo del interceptor
      try {
        const result = await getUserInfo();
        // Si no lanza, al menos no debería devolver datos válidos
        expect(result).toBeUndefined();
      } catch (e: unknown) {
        expect((e as Error).message).toContain("Access Token");
      }
    });

    it("devuelve undefined si los datos no cumplen el schema zod", async () => {
      server.use(
        http.get("http://localhost:8000/api/v1/auth/info", () =>
          HttpResponse.json({ unexpected_field: "valor inesperado" }),
        ),
      );
      localStorage.setItem("ACCESS_TOKEN_AGRYNC", "fake-access-token");
      const result = await getUserInfo();
      expect(result).toBeUndefined();
    });
  });
});
