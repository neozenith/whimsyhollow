import { HttpResponse, http } from "msw";
import { setupServer } from "msw/node";

// A shared MSW server — a real network-level fake (not an object mock). Tests register
// per-case handlers via `server.use(...)`, which override the default below.
export const server = setupServer(
  // Default identity: a sample Me. Tests that care about specific fields override /api/me.
  http.get("/api/me", () => HttpResponse.json({ email: null, user_id: null, environment: "test", roles: ["admin"] })),
);
