// Small helpers to safely compose API URLs without generating double slashes

/** Remove trailing slashes from a base URL string */
export function stripTrailingSlash(url: string): string {
  return url.replace(/\/+$/g, "");
}

/** Get normalized API base URL from env (without trailing slash). */
export function getApiBaseUrl(): string {
  const raw = process.env.NEXT_PUBLIC_API_URL;
  if (!raw) throw new Error("NEXT_PUBLIC_API_URL is not defined");
  return stripTrailingSlash(raw);
}

/** Join base and path ensuring a single slash between them. */
export function joinApi(base: string, path: string): string {
  const b = stripTrailingSlash(base);
  const p = path.startsWith("/") ? path : `/${path}`;
  return `${b}${p}`;
}
