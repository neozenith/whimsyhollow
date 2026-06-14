import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { Home } from "./Home";

describe("Home", () => {
  it("renders the heading and links to Settings and About", () => {
    render(
      <MemoryRouter>
        <Home />
      </MemoryRouter>,
    );
    expect(screen.getByRole("heading", { name: "whimsyhollow" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Settings/i })).toHaveAttribute("href", "/settings");
    expect(screen.getByRole("link", { name: /About/i })).toHaveAttribute("href", "/about");
  });
});
