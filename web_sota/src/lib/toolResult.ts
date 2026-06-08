/** Normalize FastMCP /api/v1/tools/call payloads to ToolResult-shaped dicts. */

export type ToolResultShape = {
	status: string;
	message?: string;
	data?: Record<string, unknown>;
	recovery_tip?: string;
};

export function extractToolResult(raw: unknown): ToolResultShape {
	if (raw == null) {
		return { status: "error", message: "empty tool result" };
	}

	if (typeof raw === "string") {
		try {
			return extractToolResult(JSON.parse(raw));
		} catch {
			return { status: "success", message: raw, data: { text: raw } };
		}
	}

	if (Array.isArray(raw)) {
		for (const block of raw) {
			if (!block || typeof block !== "object") continue;
			const rec = block as Record<string, unknown>;
			const text = rec.text;
			if (typeof text === "string") {
				try {
					const parsed = JSON.parse(text) as ToolResultShape;
					if (parsed && typeof parsed === "object" && "status" in parsed) {
						return parsed;
					}
				} catch {
					/* try next block */
				}
			}
		}
		return { status: "error", message: "unparseable tool result list" };
	}

	if (typeof raw === "object") {
		const obj = raw as Record<string, unknown>;
		const sc = obj.structured_content;
		if (sc && typeof sc === "object" && "status" in (sc as object)) {
			return sc as ToolResultShape;
		}
		if ("status" in obj && "message" in obj) {
			return obj as ToolResultShape;
		}
		if ("result" in obj) {
			return extractToolResult(obj.result);
		}
		if (
			obj.data &&
			typeof obj.data === "object" &&
			"status" in (obj.data as object)
		) {
			return obj.data as ToolResultShape;
		}
	}

	return {
		status: "error",
		message: `unexpected tool result type: ${typeof raw}`,
	};
}

export function toolData(raw: unknown): Record<string, unknown> {
	const tr = extractToolResult(raw);
	return (tr.data as Record<string, unknown>) ?? {};
}
