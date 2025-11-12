import type { NextRequest } from "next/server";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

function resolveBackendBase() {
  return process.env.INTERNAL_API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "";
}

function buildBackendUrl(path: string, search = "") {
  const backendBase = resolveBackendBase();
  if (!backendBase) {
    throw new Error("Backend URL not configured");
  }

  const normalizedBase = backendBase.replace(/\/+$/g, "");
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  const searchSuffix = search
    ? search.startsWith("?")
      ? search
      : `?${search}`
    : "";
  return `${normalizedBase}${normalizedPath}${searchSuffix}`;
}

export async function POST(req: NextRequest) {
  const backendBase = resolveBackendBase();
  if (!backendBase) {
    return new Response("Backend URL not configured", { status: 500 });
  }

  // Read the cookie from the frontend domain and forward it explicitly
  const token = req.cookies.get("access_token")?.value;

  // Forward body as-is
  const bodyText = await req.text();

  const upstream = await fetch(buildBackendUrl("/chat"), {
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

export async function GET(req: NextRequest) {
  const token = req.cookies.get("access_token")?.value;

  const backendBase = resolveBackendBase();
  if (!backendBase) {
    return new Response("Backend URL not configured", { status: 500 });
  }

  let targetUrl: string;
  try {
    const { search } = new URL(req.url);
    targetUrl = buildBackendUrl("/chat", search);
  } catch (error) {
    console.error("Failed to parse request URL for chat list", error);
    return new Response("Invalid request", { status: 400 });
  }

  try {
    const upstream = await fetch(targetUrl, {
      method: "GET",
      headers: {
        ...(token ? { cookie: `access_token=${token}` } : {}),
        accept: req.headers.get("accept") ?? "application/json",
      },
      // Ensure cookies for backend are not automatically forwarded
      credentials: "omit",
    });

    const body = await upstream.text();

    return new Response(body, {
      status: upstream.status,
      headers: {
        "content-type":
          upstream.headers.get("content-type") ?? "application/json",
        "cache-control": "no-store",
      },
    });
  } catch (error) {
    console.error("Failed to fetch chats from backend", error);
    return new Response("Failed to load chats", { status: 502 });
  }
}
