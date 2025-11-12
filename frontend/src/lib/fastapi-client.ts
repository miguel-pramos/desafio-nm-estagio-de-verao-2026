import { env } from "@/env";
import { stripTrailingSlash } from "@/lib/url";
import {
  AuthApi,
  ChatApi,
  Configuration,
  HealthApi,
} from "@/lib/api-client.gen";

// Use the internal URL on the server (inside Docker), and the public URL in the browser
const isServer = typeof window === "undefined";

const rawApiUrl =
  isServer && env.NODE_ENV === "production"
    ? (process.env.INTERNAL_API_URL ?? process.env.NEXT_PUBLIC_API_URL!)
    : process.env.NEXT_PUBLIC_API_URL!;

const API_URL = stripTrailingSlash(rawApiUrl);

export const config = new Configuration({
  basePath: API_URL,
  credentials: "include",
});

export const chatApi = new ChatApi(config);
export const authApi = new AuthApi(config);
export const healthApi = new HealthApi(config);
