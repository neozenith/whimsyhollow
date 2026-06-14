import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { HttpResponse, http } from "msw";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, describe, expect, it } from "vitest";

import { App } from "./App";
import { AuthProvider } from "./components/auth";
import { BrandProvider } from "./components/brand-provider";
import { ThemeProvider } from "./components/theme-provider";
import { About } from "./pages/About";
import { Home } from "./pages/Home";
import { Settings } from "./pages/Settings";
import { server } from "./test/server";

// The header (rendered inside App) consumes Theme + Brand context, so the shell is wrapped
// exactly as in main.tsx (ThemeProvider outermost, then BrandProvider).
const renderApp = (path = "/") =>
  render(
    <ThemeProvider>
      <BrandProvider>
        <AuthProvider>
          <MemoryRouter initialEntries={[path]}>
            <Routes>
              <Route element={<App />}>
                <Route path="/" element={<Home />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="/about" element={<About />} />
              </Route>
            </Routes>
          </MemoryRouter>
        </AuthProvider>
      </BrandProvider>
    </ThemeProvider>,
  );

afterEach(() => localStorage.clear());

describe("App shell", () => {
  it("renders the brand, nav links, the active route, and the outlet", () => {
    renderApp("/settings");
    expect(screen.getByText(/whimsyhollow/i)).toBeInTheDocument();
    // NavLink marks the active route with aria-current="page".
    expect(screen.getByRole("link", { name: "Settings" })).toHaveAttribute("aria-current", "page");
    expect(screen.getByRole("link", { name: "Home" })).not.toHaveAttribute("aria-current");
    // Settings page content (its CardTitle) is shown in the outlet.
    expect(screen.getByRole("heading", { name: "Settings" })).toBeInTheDocument();
  });

  it("navigates Home -> About via the sidebar links", async () => {
    const user = userEvent.setup();
    renderApp("/");
    expect(screen.getByRole("heading", { name: "whimsyhollow" })).toBeInTheDocument();
    // Scope to the desktop rail (implicit complementary role) — the Home page also has an
    // "About" link button, so the bare query would be ambiguous.
    const rail = screen.getByRole("complementary");
    await user.click(within(rail).getByRole("link", { name: "About" }));
    expect(screen.getByRole("heading", { name: "About whimsyhollow" })).toBeInTheDocument();
  });

  it("shows the signed-in user and environment in the header", async () => {
    server.use(
      http.get("/api/me", () =>
        HttpResponse.json({ email: "alice@example.com", user_id: "u1", environment: "prod", roles: ["admin"] }),
      ),
    );
    renderApp("/");
    expect(await screen.findByText("alice@example.com")).toBeInTheDocument();
    expect(screen.getByText("prod")).toBeInTheDocument();
  });

  it("falls back to 'guest' when there is no signed-in identity", async () => {
    renderApp("/"); // default /api/me handler returns null identity
    expect(await screen.findByText("guest")).toBeInTheDocument();
  });
});

// The shell carries no fixed-width column on mobile: the rail is `hidden md:flex` (out of the
// flex row), and a hamburger in the header opens an off-canvas drawer instead. jsdom has no
// layout engine, so we assert the structural/aria contract (toggle state, drawer mount, nav
// reachability) rather than pixel widths — the e2e mobile suite owns the overflow measurement.
describe("mobile nav drawer", () => {
  it("opens from the header hamburger, exposes the nav, and closes via the backdrop", async () => {
    const user = userEvent.setup();
    renderApp("/");

    const hamburger = screen.getByRole("button", { name: /toggle navigation menu/i });
    expect(hamburger).toHaveAttribute("aria-expanded", "false");
    expect(hamburger).toHaveAttribute("aria-controls", "mobile-nav-drawer");
    // Closed: the drawer (and its backdrop) is not mounted, so it can't add to the scroll width.
    expect(screen.queryByRole("button", { name: /close navigation menu/i })).not.toBeInTheDocument();

    await user.click(hamburger);
    expect(hamburger).toHaveAttribute("aria-expanded", "true");
    const backdrop = screen.getByRole("button", { name: /close navigation menu/i });
    expect(backdrop).toBeInTheDocument();
    // Nav is reachable inside the drawer (a second "Settings" link, plus the desktop rail).
    const drawer = screen.getByRole("complementary", { name: "Navigation" });
    expect(within(drawer).getByRole("link", { name: "Settings" })).toBeInTheDocument();

    await user.click(backdrop);
    expect(hamburger).toHaveAttribute("aria-expanded", "false");
    expect(screen.queryByRole("button", { name: /close navigation menu/i })).not.toBeInTheDocument();
  });

  it("closes the drawer when a nav item is tapped", async () => {
    const user = userEvent.setup();
    renderApp("/");
    await user.click(screen.getByRole("button", { name: /toggle navigation menu/i }));

    const drawer = screen.getByRole("complementary", { name: "Navigation" });
    await user.click(within(drawer).getByRole("link", { name: "About" }));

    expect(screen.queryByRole("complementary", { name: "Navigation" })).not.toBeInTheDocument();
  });

  it("closes the drawer on Escape", async () => {
    const user = userEvent.setup();
    renderApp("/");
    const hamburger = screen.getByRole("button", { name: /toggle navigation menu/i });
    await user.click(hamburger);
    expect(screen.getByRole("complementary", { name: "Navigation" })).toBeInTheDocument();

    await user.keyboard("{Escape}");
    expect(hamburger).toHaveAttribute("aria-expanded", "false");
    expect(screen.queryByRole("complementary", { name: "Navigation" })).not.toBeInTheDocument();
  });
});
