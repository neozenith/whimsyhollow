import { expect, test } from "@playwright/test";

// Navigation smoke suite (desktop / chromium project): the collapsible sidebar rail and
// route changes via the sidebar links.

test("the sidebar collapse button toggles the rail's data-collapsed state", async ({ page }) => {
  await page.goto("/");
  const rail = page.locator("aside[data-collapsed]");
  await expect(rail).toBeVisible();
  await expect(rail).toHaveAttribute("data-collapsed", "false");

  await page.getByRole("button", { name: /collapse sidebar/i }).click();
  await expect(rail).toHaveAttribute("data-collapsed", "true");

  await page.getByRole("button", { name: /expand sidebar/i }).click();
  await expect(rail).toHaveAttribute("data-collapsed", "false");
});

test("navigating Home -> Settings -> About via the sidebar changes the page", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "whimsyhollow" })).toBeVisible();

  // Scope clicks to the sidebar's navigation landmark — the Home page also renders
  // CTA links to these routes, so an unscoped getByRole("link") is ambiguous.
  const nav = page.getByRole("navigation");

  await nav.getByRole("link", { name: "Settings" }).click();
  await expect(page).toHaveURL(/\/settings$/);
  await expect(page.getByRole("heading", { name: "Settings" })).toBeVisible();

  await nav.getByRole("link", { name: "About" }).click();
  await expect(page).toHaveURL(/\/about$/);
  await expect(page.getByRole("heading", { name: "About whimsyhollow" })).toBeVisible();

  await nav.getByRole("link", { name: "Home" }).click();
  await expect(page).toHaveURL(/\/$/);
  await expect(page.getByRole("heading", { name: "whimsyhollow" })).toBeVisible();
});
