import { render, screen } from "@testing-library/react";
import { HttpResponse, http } from "msw";
import { afterEach, describe, expect, it } from "vitest";

import { AuthProvider } from "@/components/auth";
import { BrandProvider } from "@/components/brand-provider";
import { ThemeProvider } from "@/components/theme-provider";
import { server } from "../test/server";
import { Settings } from "./Settings";

const renderSettings = () =>
  render(
    <ThemeProvider>
      <BrandProvider>
        <AuthProvider>
          <Settings />
        </AuthProvider>
      </BrandProvider>
    </ThemeProvider>,
  );

afterEach(() => {
  localStorage.clear();
  document.documentElement.removeAttribute("style");
  document.documentElement.removeAttribute("data-brand");
  document.documentElement.classList.remove("dark");
});

describe("Settings", () => {
  it("shows the active theme, brand, and deployment environment", async () => {
    server.use(
      http.get("/api/me", () =>
        HttpResponse.json({ email: "u@example.com", user_id: "u", environment: "staging", roles: ["admin"] }),
      ),
    );
    renderSettings();
    expect(screen.getByRole("heading", { name: "Settings" })).toBeInTheDocument();
    // Default theme is light (no stored value, OS reports no dark preference).
    expect(screen.getByText("light")).toBeInTheDocument();
    // Default brand is the pinned karaoke bar.
    expect(screen.getByText("Josh's Karaoke Bar")).toBeInTheDocument();
    // Environment comes from /api/me once it resolves.
    expect(await screen.findByText("staging")).toBeInTheDocument();
  });

  it("falls back to 'unknown' environment before identity resolves / on failure", async () => {
    server.use(http.get("/api/me", () => new HttpResponse(null, { status: 500 })));
    renderSettings();
    expect(await screen.findByText("unknown")).toBeInTheDocument();
  });
});
