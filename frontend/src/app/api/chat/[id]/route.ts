import type { NextRequest } from "next/server";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function DELETE(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id } = await params;
  const backendBase =
    process.env.INTERNAL_API_URL ?? process.env.NEXT_PUBLIC_API_URL;
  if (!backendBase) {
    return new Response("Backend URL not configured", { status: 500 });
  }

  // Read the cookie from the frontend domain and forward it explicitly
  const token = req.cookies.get("access_token")?.value;

  const upstream = await fetch(
    `${backendBase.replace(/\/+$/g, "")}/chat/${id}`,
    {
      method: "DELETE",
      headers: {
        // Attach cookie header so the backend authenticates the request
        ...(token ? { cookie: `access_token=${token}` } : {}),
      },
    },
  );

  // Return the response from backend
  return new Response(upstream.body, {
    status: upstream.status,
    headers: {
      "content-type":
        upstream.headers.get("content-type") ?? "application/json",
    },
  });
}
