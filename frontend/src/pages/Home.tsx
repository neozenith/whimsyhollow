import { Info, Settings as SettingsIcon } from "lucide-react";
import { Link } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader } from "@/components/ui/card";

export function Home() {
  return (
    <Card className="animate-fade-in-up">
      <CardHeader>
        <h1 className="text-2xl font-semibold leading-none">whimsyhollow</h1>
        <CardDescription className="text-base leading-relaxed">
          A plain scale-to-zero Cloud Run app: an async FastAPI backend serving this React UI from the same origin. It
          ships a dark/light theme provider, a live brand switcher, a collapsible sidebar, and a Playwright e2e suite —
          the shell, with none of the domain weight.
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-wrap gap-3">
        <Button asChild>
          <Link to="/settings">
            <SettingsIcon /> Settings
          </Link>
        </Button>
        <Button asChild variant="outline">
          <Link to="/about">
            <Info /> About
          </Link>
        </Button>
      </CardContent>
    </Card>
  );
}
