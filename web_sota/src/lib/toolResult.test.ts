import { describe, expect, it } from "vitest";
import { extractToolResult, toolData } from "./toolResult";

describe("extractToolResult", () => {
	it("parses ToolResult-shaped dict", () => {
		const tr = extractToolResult({
			status: "success",
			message: "ok",
			data: { windows: [{ handle: 42 }] },
		});
		expect(tr.status).toBe("success");
		expect(toolData(tr).windows).toEqual([{ handle: 42 }]);
	});

	it("unwraps nested result field from REST bridge", () => {
		const tr = extractToolResult({
			status: "success",
			result: {
				status: "success",
				message: "found",
				data: { handle: 7 },
			},
		});
		expect(tr.data).toEqual({ handle: 7 });
	});

	it("parses FastMCP text JSON blocks", () => {
		const tr = extractToolResult([
			{
				type: "text",
				text: JSON.stringify({
					status: "success",
					message: "done",
					data: { task_id: "abc" },
				}),
			},
		]);
		expect(toolData(tr).task_id).toBe("abc");
	});
});
