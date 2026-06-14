import { useAuth } from "@/components/auth";
import { useBrand } from "@/components/brand-provider";
import { useTheme } from "@/components/theme-provider";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader } from "@/components/ui/card";

/** Read-only view of the live shell state: the active theme, the active brand, and the
 * deployment environment. The controls that change theme + brand live in the header. */
export function Settings() {
  const { theme } = useTheme();
  const { brand } = useBrand();
  const { me } = useAuth();
  const environment = me?.environment ?? "unknown";

  return (
    <Card className="animate-fade-in-up">
      <CardHeader>
        <h1 className="text-2xl font-semibold leading-none">Settings</h1>
        <CardDescription>
          The current shell state. Use the dark/light toggle and the brand switcher in the header to change the theme
          and brand live.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <dl className="grid grid-cols-[8rem_1fr] gap-x-4 gap-y-3 text-sm">
          <dt className="text-muted-foreground">Theme</dt>
          <dd>
            <Badge variant="muted">{theme}</Badge>
          </dd>
          <dt className="text-muted-foreground">Brand</dt>
          <dd>
            <Badge variant="muted">{brand.name}</Badge>
          </dd>
          <dt className="text-muted-foreground">Environment</dt>
          <dd>
            <Badge variant="muted" className="uppercase">
              {environment}
            </Badge>
          </dd>
        </dl>
      </CardContent>
    </Card>
  );
}
