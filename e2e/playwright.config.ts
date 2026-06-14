import { defineConfig, devices } from "@playwright/test";

// Smoke suite drives the app booted locally by the `webServer` block below: the FastAPI
// backend (port 8080) plus the Vite dev server (port 5173, which proxies /api -> 8080).
// Override BASE_URL to point the suite at a deployed environment instead (then the local
// servers are skipped — see `webServer` reuse note).
// `||` (not `??`) so an empty BASE_URL — e.g. the e2e Makefile passing an unset
// `BASE_URL=` — falls back to localhost instead of becoming an invalid empty base.
const BASE_URL = process.env.BASE_URL || "http://localhost:5173";

export default defineConfig({
  testDir: "./tests",
  // Cloud Run scales from zero; locally Vite is fast. Be patient either way.
  timeout: 60_000,
  expect: { timeout: 15_000 },
  fullyParallel: false,
  retries: 0,
  reporter: [
    ["list"],
    ["html", { outputFolder: "playwright-report", open: "never" }],
  ],
  use: {
    baseURL: BASE_URL,
    screenshot: "on",
    trace: "on",
    video: "retain-on-failure",
  },
  // Boot the full app for the smoke suite: backend + frontend. Skipped automatically when
  // BASE_URL points at an already-running server (Playwright probes the URL first).
  webServer: process.env.BASE_URL
    ? undefined
    : [
        {
          command: "uv run --directory ../backend uvicorn whimsyhollow.main:app --host 0.0.0.0 --port 8080",
          url: "http://localhost:8080/api/me",
          reuseExistingServer: !process.env.CI,
          timeout: 120_000,
        },
        {
          command: "bun run --cwd ../frontend dev:frontend-only",
          url: "http://localhost:5173",
          reuseExistingServer: !process.env.CI,
          timeout: 120_000,
        },
      ],
  projects: [
    {
      // Desktop smoke suite (shell + navigation). Excludes the mobile spec so it
      // doesn't run twice.
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
      testIgnore: /mobile-layout\.spec\.ts/,
    },
    {
      // Mobile layout suite (mobile-layout.spec.ts only). iPhone 11 descriptor =
      // WebKit, 414x715 CSS viewport, DPR 2, isMobile + hasTouch.
      name: "iphone-11",
      use: { ...devices["iPhone 11"] },
      testMatch: /mobile-layout\.spec\.ts/,
    },
  ],
});
