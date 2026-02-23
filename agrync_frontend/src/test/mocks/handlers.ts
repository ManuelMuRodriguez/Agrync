import { http, HttpResponse } from "msw";

const BASE = "http://localhost:8000/api/v1";

export const handlers = [
  // POST /auth/login
  http.post(`${BASE}/auth/login`, async ({ request }) => {
    const body = await request.text();
    const params = new URLSearchParams(body);
    const username = params.get("username");
    const password = params.get("password");

    if (username === "admin@example.com" && password === "AdminPass123") {
      return HttpResponse.json({
        access_token: "fake-access-token",
        token_type: "bearer",
      });
    }
    return HttpResponse.json(
      { detail: "Incorrect email or password" },
      { status: 401 },
    );
  }),

  // POST /auth/logout
  http.post(`${BASE}/auth/logout`, () =>
    HttpResponse.json({ message: "Session closed successfully" }),
  ),

  // POST /auth/refresh
  http.post(`${BASE}/auth/refresh`, () =>
    HttpResponse.json({ access_token: "new-fake-token", token_type: "bearer" }),
  ),

  // GET /auth/info
  http.get(`${BASE}/auth/info`, ({ request }) => {
    const auth = request.headers.get("Authorization");
    if (
      auth === "Bearer fake-access-token" ||
      auth === "Bearer new-fake-token"
    ) {
      return HttpResponse.json({
        id: "user-id-123",
        full_name: "Admin Test",
        role: "Administrador",
      });
    }
    return HttpResponse.json(
      { detail: "Invalid access token" },
      { status: 401 },
    );
  }),

  // POST /auth/validate
  http.post(`${BASE}/auth/validate`, async ({ request }) => {
    const body = (await request.json()) as {
      email: string;
      password: string;
      password_confirmation: string;
    };
    if (body.password !== body.password_confirmation) {
      return HttpResponse.json(
        { detail: "Passwords do not match" },
        { status: 400 },
      );
    }
    return HttpResponse.json(
      { message: "Activation successful" },
      { status: 201 },
    );
  }),

  // POST /auth/register
  http.post(`${BASE}/auth/register`, () =>
    HttpResponse.json(
      { message: "User created successfully" },
      { status: 201 },
    ),
  ),

  // PUT /api/v1/devices/:userId/:deviceId (write value)
  http.put(`${BASE}/devices/:userId/:deviceId`, () =>
    HttpResponse.json({ message: "Value modified successfully" }),
  ),
];
