import { createContext, type ReactNode, useContext, useEffect, useState } from "react";

import { getMe, type Me } from "../api";

interface AuthValue {
  me: Me | null;
  loading: boolean;
}

const AuthContext = createContext<AuthValue | null>(null);

/** Fetches the signed-in identity (+ deployment environment) once on mount and shares it. */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [me, setMe] = useState<Me | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    getMe()
      .catch(() => null)
      .then((m) => {
        if (!cancelled) setMe(m);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return <AuthContext.Provider value={{ me, loading }}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
