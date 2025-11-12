import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");

  const redirectTo = process.env.NEXT_PUBLIC_HOME_URL ?? "/";
  const redirectUrl = new URL(request.nextUrl.origin);
  redirectUrl.pathname = redirectTo;

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
