# `e2e/` — Playwright smoke suite

Drives the **whimsyhollow** app shell and proves the trimmed feature set works end-to-end:

1. **Shell loads** (`tests/shell.spec.ts`) — the global header shows the deployment
   environment badge and the signed-in user; the dark/light toggle flips `html.dark`; the
   live brand `<select>` swaps `html[data-brand]`.
2. **Navigation works** (`tests/navigation.spec.ts`) — the sidebar collapse button toggles
   the rail's `data-collapsed`; navigating Home → Settings → About via the sidebar changes
   the page.
3. **Mobile layout holds up** (`tests/mobile-layout.spec.ts`) — under the `iphone-11` project
   (WebKit, 414×715, touch), on `/` and `/settings` the header hamburger opens the off-canvas
   nav drawer and the page has no horizontal overflow.

Each test attaches a **screenshot**; an HTML report is written to `playwright-report/`.

The two projects are isolated: `chromium` runs the shell + navigation specs, `iphone-11` runs
`mobile-layout.spec.ts` only.

## Run

```bash
make -C e2e install            # bun install + chromium & webkit (webkit drives iPhone 11)
make -C e2e test               # boots backend+frontend locally, runs the full suite
make -C e2e mobile             # ONLY the iPhone 11 mobile-layout suite
make -C e2e list               # list discovered tests (validate structure, no run)
make -C e2e report             # open the HTML report
```

By default the suite boots the app itself via Playwright's `webServer` block: the FastAPI
backend on `:8080` and the Vite dev server on `:5173` (which proxies `/api` → `:8080`). The
base URL is `http://localhost:5173`.

Target an already-running / deployed environment with `BASE_URL` (this skips the local
servers):

```bash
make -C e2e test BASE_URL=https://whimsyhollow.example.run.app
```
