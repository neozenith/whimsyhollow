// Same-origin calls: FastAPI serves this SPA and proxies the API endpoints.

/** A plain fetch wrapper. All API calls go through this so headers/handling stay consistent. */
function apiFetch(input: string, init: RequestInit = {}): Promise<Response> {
  const headers = new Headers(init.headers);
  return fetch(input, { ...init, headers });
}

export interface Me {
  email: string | null;
  user_id: string | null;
  environment: string;
  roles: string[];
}

/** The signed-in identity + deployment environment. */
export async function getMe(): Promise<Me> {
  const resp = await apiFetch("/api/me");
  if (!resp.ok) throw new Error(`me error ${resp.status}`);
  return resp.json();
}
