import { render, screen } from "@testing-library/react";
import { HttpResponse, http } from "msw";
import { afterEach, describe, expect, it } from "vitest";

import { server } from "../test/server";
import { AuthProvider, useAuth } from "./auth";

afterEach(() => localStorage.clear());

const Probe = () => {
  const { me, loading } = useAuth();
  if (loading) return <p>loading</p>;
  return <p>identity:{me ? `${me.email}/${me.environment}` : "none"}</p>;
};

describe("AuthProvider", () => {
  it("fetches the signed-in identity on mount and exposes it via useAuth", async () => {
    server.use(
      http.get("/api/me", () =>
        HttpResponse.json({ email: "ada@example.com", user_id: "u1", environment: "prod", roles: ["admin"] }),
      ),
    );
    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>,
    );
    expect(await screen.findByText("identity:ada@example.com/prod")).toBeInTheDocument();
  });

  it("resolves to null identity when /api/me fails (no crash, no fake data)", async () => {
    server.use(http.get("/api/me", () => new HttpResponse(null, { status: 500 })));
    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>,
    );
    expect(await screen.findByText("identity:none")).toBeInTheDocument();
  });

  it("useAuth throws outside an AuthProvider", () => {
    expect(() => render(<Probe />)).toThrow(/useAuth must be used within AuthProvider/);
  });
});
