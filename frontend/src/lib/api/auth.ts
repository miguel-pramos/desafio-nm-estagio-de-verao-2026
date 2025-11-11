import { ResponseError } from "@/lib/api-client.gen";
import { authApi } from "@/lib/fastapi-client";
import { headers } from "next/headers";

export async function getUser() {
  const headersList = Object.fromEntries(await headers());

  try {
    return await authApi.meAuthMeGet({
      headers: headersList,
      cache: "no-store",
    });
  } catch (error) {
    if (error instanceof ResponseError) {
      if (error.response.status === 401) {
        return null;
      }
    }

    throw error;
  }
}
