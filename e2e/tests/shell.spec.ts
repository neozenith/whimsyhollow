import { expect, test } from "@playwright/test";

// Smoke suite for the app shell (desktop / chromium project). Proves the global header
// (identity + deployment environment), the dark/light theme toggle, and the live brand
// switcher all work end-to-end against the running app.

test("the app loads and the header shows the environment and a user", async ({ page }, testInfo) => {
  await page.goto("/");

  // The header's environment Badge is rendered in uppercase from /api/me.environment.
  const header = page.locator("header");
  await expect(header).toBeVisible();
  // The signed-in user (or "guest") is shown next to the user icon.
  await expect(header.getByText(/@|guest|^user /).first()).toBeVisible();
  // The environment badge is one of the known deployment envs.
  await expect(header.getByText(/^(dev|test|staging|prod|local)$/i).first()).toBeVisible();

  await testInfo.attach("shell-home.png", { body: await page.screenshot({ fullPage: true }), contentType: "image/png" });
});

test("the dark-mode toggle flips html.dark", async ({ page }) => {
  await page.goto("/");
  const html = page.locator("html");
  const toggle = page.getByRole("button", { name: /toggle dark mode/i });

  const startedDark = await html.evaluate((el) => el.classList.contains("dark"));
  await toggle.click();
  await expect
    .poll(() => html.evaluate((el) => el.classList.contains("dark")))
    .toBe(!startedDark);

  // Toggling back restores the original theme.
  await toggle.click();
  await expect
    .poll(() => html.evaluate((el) => el.classList.contains("dark")))
    .toBe(startedDark);
});

test("the brand switcher swaps html[data-brand]", async ({ page }) => {
  await page.goto("/");
  const html = page.locator("html");
  const select = page.getByLabel(/switch brand/i);
  await expect(select).toBeVisible();

  const before = await html.getAttribute("data-brand");
  // Pick whichever brand option is not currently selected.
  const optionValues = await select.locator("option").evaluateAll((opts) =>
    opts.map((o) => (o as HTMLOptionElement).value),
  );
  const other = optionValues.find((v) => v !== before);
  expect(other, "expected more than one brand to switch between").toBeTruthy();

  await select.selectOption(other as string);
  await expect(html).toHaveAttribute("data-brand", other as string);
  expect(other).not.toBe(before);
});
