import { expect, test } from "@playwright/test";

test.describe("operator shell smoke", () => {
	test("dashboard loads and shows overview", async ({ page }) => {
		await page.goto("/");
		await expect(
			page.getByRole("heading", { name: "Automation Dashboard" }),
		).toBeVisible();
	});

	test("sidebar navigates to Targets", async ({ page }) => {
		await page.goto("/");
		await page.getByRole("link", { name: "Targets" }).click();
		await expect(
			page.getByRole("heading", { name: "Automation Targets" }),
		).toBeVisible();
		await expect(page.getByRole("button", { name: "Notepad" })).toBeVisible();
		await expect(
			page.getByRole("button", { name: "VRoid Studio" }),
		).toBeVisible();
	});

	test("HITL bar renders on Targets", async ({ page }) => {
		await page.goto("/targets");
		await expect(page.getByText("HITL", { exact: true })).toBeVisible();
		await expect(
			page.getByRole("button", { name: "Approve 5 min" }),
		).toBeVisible();
	});

	test("REST bridge health responds via UI proxy", async ({ request }) => {
		const res = await request.get("/api/v1/health");
		expect(res.ok()).toBeTruthy();
		const body = await res.json();
		expect(body).toBeTruthy();
	});
});
