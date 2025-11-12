import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");

  const redirectTo = process.env.NEXT_PUBLIC_HOME_URL ?? "/";

  // Resolve destino: permite URL absoluta no env; caso contrário, usa origem do proxy
  let redirectUrl: URL;
  try {
    // Se for uma URL absoluta válida, usa diretamente
    redirectUrl = new URL(redirectTo);
  } catch {
    // Caso seja caminho relativo, constrói a origem a partir dos cabeçalhos do proxy
    const host =
      request.headers.get("x-forwarded-host") ?? request.headers.get("host");
    const proto =
      request.headers.get("x-forwarded-proto") ??
      (host?.includes("localhost") ? "http" : "https");
    const origin = host ? `${proto}://${host}` : request.nextUrl.origin;
    redirectUrl = new URL(
      redirectTo.startsWith("/") ? redirectTo : `/${redirectTo}`,
      origin,
    );
  }

  if (!token) return NextResponse.redirect(redirectUrl);

  const res = NextResponse.redirect(redirectUrl);

  res.cookies.set({
    name: "access_token",
    value: token,
    httpOnly: true,
    path: "/",
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    maxAge: 60 * 60 * 24 * 7,
  });

  return res;
}
