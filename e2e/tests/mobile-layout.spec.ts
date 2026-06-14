import { expect, test } from "@playwright/test";
import { measureHorizontalOverflow, settleRoute } from "./helpers/mobile";

// Trimmed mobile suite — runs ONLY under the "iphone-11" Playwright project
// (devices["iPhone 11"]: WebKit, 414x715 CSS viewport, DPR 2, isMobile + hasTouch).
// At mobile width the desktop rail is display:none; navigation must come from the
// header hamburger opening the off-canvas drawer. We assert that contract on the
// key routes, plus the classic "no horizontal overflow" check.

const ROUTES = [
  { path: "/", name: "home" },
  { path: "/settings", name: "settings" },
] as const;

const OVERFLOW_TOLERANCE = 2;

for (const route of ROUTES) {
  test(`mobile: hamburger opens the nav drawer on ${route.name} (${route.path})`, async ({ page }, testInfo) => {
    await settleRoute(page, route.path);

    // The desktop rail (md:flex) is hidden at this width; the hamburger is the nav entry point.
    const hamburger = page.getByRole("button", { name: /toggle navigation menu/i });
    await expect(hamburger).toBeVisible();
    await expect(hamburger).toHaveAttribute("aria-expanded", "false");

    await hamburger.click();
    await expect(hamburger).toHaveAttribute("aria-expanded", "true");

    const drawer = page.getByRole("complementary", { name: "Navigation" });
    await expect(drawer).toBeVisible();
    await expect(drawer.getByRole("link", { name: "Settings" })).toBeVisible();

    // No page-level horizontal overflow on a phone.
    const overflow = await measureHorizontalOverflow(page);
    expect(overflow.overflowBy).toBeLessThanOrEqual(OVERFLOW_TOLERANCE);

    await testInfo.attach(`${route.name}-mobile.png`, {
      body: await page.screenshot({ fullPage: true }),
      contentType: "image/png",
    });
  });
}
