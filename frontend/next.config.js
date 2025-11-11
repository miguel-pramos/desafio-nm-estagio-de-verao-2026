/**
 * Run `build` or `dev` with `SKIP_ENV_VALIDATION` to skip env validation. This is especially useful
 * for Docker builds.
 */
import "./src/env.js";

/** @type {import("next").NextConfig} */
const config = {
  output: "standalone",
  
};

export async function rewrites() {
    return [
      { source: '/api/:path*', destination: 'https://desafio-nm-estagio-de-verao-2026-production.up.railway.app/:path*' },
    ];
  }

export default config;
