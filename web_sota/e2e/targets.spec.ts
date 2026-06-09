import { expect, test } from "@playwright/test";

test.describe("Targets tabs", () => {
	test.beforeEach(async ({ page }) => {
		await page.goto("/targets");
	});

	test("notepad tab shows launch controls", async ({ page }) => {
		await page.getByRole("button", { name: "Notepad" }).click();
		await expect(page.getByRole("button", { name: "Launch" })).toBeVisible();
		await expect(
			page.getByRole("button", { name: "Find window" }).first(),
		).toBeVisible();
	});

	test("custom tab exposes JSON editor", async ({ page }) => {
		await page.getByRole("button", { name: "Custom" }).click();
		await expect(page.getByLabel("Steps JSON")).toBeVisible();
		await expect(
			page.getByRole("button", { name: "Run custom steps" }),
		).toBeVisible();
	});

	test("tab choice persists in localStorage", async ({ page }) => {
		await page.getByRole("button", { name: "VRoid Studio" }).click();
		await page.reload();
		await expect(
			page.getByRole("button", { name: "Export VRM (F8)" }),
		).toBeVisible();
	});
});
