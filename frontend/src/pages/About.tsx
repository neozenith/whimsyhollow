import { Card, CardContent, CardDescription, CardHeader } from "@/components/ui/card";

/** Static description of the shell architecture this trimmed app demonstrates. */
export function About() {
  return (
    <Card className="animate-fade-in-up">
      <CardHeader>
        <h1 className="text-2xl font-semibold leading-none">About whimsyhollow</h1>
        <CardDescription>The plain shell, and what each piece does.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4 text-sm leading-relaxed">
        <p>
          whimsyhollow is a trimmed fullstack shell — a FastAPI backend serving a React + Vite SPA from the same origin
          — with the domain functionality removed. What remains is the reusable architecture:
        </p>
        <ul className="list-disc space-y-2 pl-5">
          <li>
            <span className="font-medium text-foreground">Theme provider</span> — a dark/light theme stored in
            localStorage, applied before first paint to avoid a flash of the wrong theme.
          </li>
          <li>
            <span className="font-medium text-foreground">Brand switcher</span> — a live "rapid theme changer" that
            swaps W3C design-token packs onto CSS custom properties, repainting the whole UI without a reload.
          </li>
          <li>
            <span className="font-medium text-foreground">Collapsible sidebar</span> — a desktop rail that collapses to
            icons (persisted), plus an off-canvas drawer for mobile.
          </li>
          <li>
            <span className="font-medium text-foreground">Header identity + environment</span> — a global top bar that
            shows who is signed in and which deployment environment is serving the app.
          </li>
          <li>
            <span className="font-medium text-foreground">Playwright e2e</span> — a smoke suite that drives the running
            app to prove the shell loads and the theme/brand/navigation controls work.
          </li>
        </ul>
      </CardContent>
    </Card>
  );
}
