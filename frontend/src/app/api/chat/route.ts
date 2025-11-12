import type { NextRequest } from "next/server";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function POST(req: NextRequest) {
  const backendBase =
    process.env.INTERNAL_API_URL ?? process.env.NEXT_PUBLIC_API_URL;
  if (!backendBase) {
    return new Response("Backend URL not configured", { status: 500 });
  }

  // Read the cookie from the frontend domain and forward it explicitly
  const token = req.cookies.get("access_token")?.value;

  // Forward body as-is
  const bodyText = await req.text();

  const upstream = await fetch(`${backendBase.replace(/\/+$/g, "")}/chat`, {
    method: "POST",
    headers: {
      "content-type": req.headers.get("content-type") ?? "application/json",
      // Attach cookie header so the backend authenticates the request
      ...(token ? { cookie: `access_token=${token}` } : {}),
      accept: "text/event-stream",
    },
    // Do not send credentials across domains here; we forward the cookie ourselves
    body: bodyText,
  });

  // Pipe the streaming response back to the client
  return new Response(upstream.body, {
    status: upstream.status,
    headers: {
      "content-type":
        upstream.headers.get("content-type") ?? "text/event-stream",
      "cache-control": "no-store",
    },
  });
}
