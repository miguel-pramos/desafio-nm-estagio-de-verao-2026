"use server";

import { redirect } from "next/navigation";
import { getApiBaseUrl, joinApi } from "@/lib/url";

export async function logout() {
  redirect(joinApi(getApiBaseUrl(), "/auth/logout"));
}
