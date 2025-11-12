import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  const redirectTo = "/";

  const redirectToUrl = new URL(request.nextUrl.origin);
  redirectToUrl.pathname = redirectTo;

  if (!token) return NextResponse.redirect(redirectToUrl);

  const res = NextResponse.redirect(redirectToUrl);

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
