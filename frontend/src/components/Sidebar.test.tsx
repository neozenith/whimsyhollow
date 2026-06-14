import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it } from "vitest";

import { BrandProvider } from "./brand-provider";
import { NavDrawerProvider } from "./nav-drawer";
import { MobileNavDrawer, Sidebar } from "./Sidebar";
import { ThemeProvider } from "./theme-provider";

const renderSidebar = (path = "/") =>
  render(
    <MemoryRouter initialEntries={[path]}>
      <Sidebar />
    </MemoryRouter>,
  );

afterEach(() => localStorage.clear());

describe("Sidebar", () => {
  it("renders the brand and a link per route, marking the active one", () => {
    renderSidebar("/about");
    expect(screen.getByText(/whimsyhollow/i)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Home" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Settings" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "About" })).toHaveAttribute("aria-current", "page");
    expect(screen.getByRole("link", { name: "Home" })).not.toHaveAttribute("aria-current");
  });

  it("collapses to an icon rail, hides the brand, and persists the choice", async () => {
    const user = userEvent.setup();
    renderSidebar();
    expect(screen.getByText(/whimsyhollow/i)).toBeInTheDocument();
    const rail = screen.getByText(/whimsyhollow/i).closest("aside");
    expect(rail).toHaveAttribute("data-collapsed", "false");

    await user.click(screen.getByRole("button", { name: /collapse sidebar/i }));
    expect(screen.queryByText(/whimsyhollow/i)).not.toBeInTheDocument();
    expect(localStorage.getItem("sidebar-collapsed")).toBe("1");
    // The toggle now offers to expand again.
    expect(screen.getByRole("button", { name: /expand sidebar/i })).toBeInTheDocument();
  });

  it("starts collapsed when localStorage says so", () => {
    localStorage.setItem("sidebar-collapsed", "1");
    renderSidebar();
    expect(screen.queryByText(/whimsyhollow/i)).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: /expand sidebar/i })).toBeInTheDocument();
  });
});

describe("MobileNavDrawer", () => {
  it("renders nothing while closed so it never adds to the page scroll width", () => {
    render(
      <ThemeProvider>
        <BrandProvider>
          <MemoryRouter>
            <NavDrawerProvider>
              <MobileNavDrawer />
            </NavDrawerProvider>
          </MemoryRouter>
        </BrandProvider>
      </ThemeProvider>,
    );
    expect(screen.queryByRole("complementary", { name: "Navigation" })).not.toBeInTheDocument();
  });
});
