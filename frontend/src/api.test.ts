import { HttpResponse, http } from "msw";
import { describe, expect, it } from "vitest";

import { getMe } from "./api";
import { server } from "./test/server";

describe("getMe", () => {
  it("returns the parsed identity on a 200", async () => {
    server.use(
      http.get("/api/me", () =>
        HttpResponse.json({ email: "u@example.com", user_id: "u", environment: "test", roles: ["viewer"] }),
      ),
    );
    const me = await getMe();
    expect(me).toEqual({ email: "u@example.com", user_id: "u", environment: "test", roles: ["viewer"] });
  });

  it("throws with the status code on a non-OK response", async () => {
    server.use(http.get("/api/me", () => new HttpResponse(null, { status: 503 })));
    await expect(getMe()).rejects.toThrow(/me error 503/);
  });
});
