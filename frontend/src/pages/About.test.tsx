import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { About } from "./About";

describe("About", () => {
  it("renders the architecture overview", () => {
    render(<About />);
    expect(screen.getByRole("heading", { name: "About whimsyhollow" })).toBeInTheDocument();
    expect(screen.getByText(/Theme provider/i)).toBeInTheDocument();
    expect(screen.getByText(/Brand switcher/i)).toBeInTheDocument();
    expect(screen.getByText(/Collapsible sidebar/i)).toBeInTheDocument();
    expect(screen.getByText(/Playwright e2e/i)).toBeInTheDocument();
  });
});
