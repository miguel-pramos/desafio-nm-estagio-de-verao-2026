import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export async function GET(request: NextRequest) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  const redirectTo = "/";

  // If no token provided, just redirect home
  if (!token) return NextResponse.redirect(new URL(redirectTo, request.url));

  const res = NextResponse.redirect(new URL(redirectTo, request.url));

  // Set HTTP-only cookie with reasonable defaults
  res.cookies.set({
    name: "access_token",
    value: token,
    httpOnly: true,
    path: "/",
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    maxAge: 60 * 60 * 24 * 7, // 7 days
  });

  return res;
}
