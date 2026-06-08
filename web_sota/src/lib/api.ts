/**
 * REST bridge: same origin in dev (Vite proxies `/api` → backend, see vite.config.ts).
 * Production build should be served behind the same host as the API or set VITE_API_ORIGIN.
 */
const origin =
	(import.meta.env.VITE_API_ORIGIN as string | undefined)?.replace(/\/$/, "") ??
	"";

export function apiPath(path: string): string {
	const p = path.startsWith("/") ? path : `/${path}`;
	return `${origin}${p}`;
}
