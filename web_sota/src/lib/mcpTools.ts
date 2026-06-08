import { apiPath } from "@/lib/api";

export type ToolCallApiResponse = {
	status: string;
	result?: unknown;
	message?: string | null;
};

/** POST /api/v1/tools/call — same surface the Tools Hub uses. */
export async function callMcpTool(
	name: string,
	arguments_: Record<string, unknown>,
): Promise<
	| { ok: true; raw: ToolCallApiResponse }
	| { ok: false; error: string; status?: number }
> {
	const r = await fetch(apiPath("/api/v1/tools/call"), {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({ name, arguments: arguments_ }),
	});
	let j: ToolCallApiResponse;
	try {
		j = (await r.json()) as ToolCallApiResponse;
	} catch {
		return {
			ok: false,
			error: `Invalid JSON (HTTP ${r.status})`,
			status: r.status,
		};
	}
	if (!r.ok) {
		return {
			ok: false,
			error: j.message ?? `HTTP ${r.status}`,
			status: r.status,
		};
	}
	if (j.status === "error") {
		return { ok: false, error: j.message ?? "Tool returned error" };
	}
	return { ok: true, raw: j };
}
