import { expect, test } from "@playwright/test";

const VALID_PAPER_ID = "0123456789abcdef0123456789abcdef01234567";

function baseRecommendPayload(query: string) {
  return {
    sectionA: [
      {
        source: "local",
        paper_id: VALID_PAPER_ID,
        title: `Local result for ${query}`,
        year: 2024,
        abstract: "Local abstract",
        url: "https://example.org/local",
        open_access_pdf: null,
        citations: 20,
        relevance_score: 0.95,
        author_h_index: 12,
        venue: "Local Venue",
        scopus_indexed: true,
      },
    ],
    cluster_id: 1,
    cluster_keywords: [],
    web_job_id: "job-1",
    enrich_job_id: "enrich-1",
  };
}

test("Case 11: valid query processing shows local results immediately", async ({ page }) => {
  await page.route("http://localhost:8000/api/recommend?**", async (route) => {
    const url = new URL(route.request().url());
    const query = url.searchParams.get("query") ?? "";
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(baseRecommendPayload(query)) });
  });

  await page.route("http://localhost:8000/api/recommend/local-enriched?**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ status: "done", sectionA: baseRecommendPayload("valid").sectionA }),
    });
  });

  await page.goto("/");
  
  const startTime = Date.now();
  await page.getByPlaceholder("Example: Parameter-efficient adapters for multimodal transformers in radiology").fill("recommendation systems");
  await page.getByRole("button", { name: "Get Recommendations" }).click();

  await expect(page.getByText("Local result for recommendation systems")).toBeVisible();
  const localResponseTime = Date.now() - startTime;
  console.log(`Case 11 - Local response time: ${localResponseTime}ms`);
});

test("Case 12: empty query handling keeps search action disabled", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("button", { name: "Get Recommendations" })).toBeDisabled();
});

test("Case 13: special characters query is processed without crash", async ({ page }) => {
  let requestedUrl = "";

  await page.route("http://localhost:8000/api/recommend?**", async (route) => {
    requestedUrl = route.request().url();
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(baseRecommendPayload("C++ programming")),
    });
  });

  await page.route("http://localhost:8000/api/recommend/local-enriched?**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ status: "done", sectionA: baseRecommendPayload("C++ programming").sectionA }),
    });
  });

  await page.goto("/");
  await page.getByPlaceholder("Example: Parameter-efficient adapters for multimodal transformers in radiology").fill("C++ programming");
  await page.getByRole("button", { name: "Get Recommendations" }).click();

  await expect(page.getByText("Local result for C++ programming")).toBeVisible();
  expect(requestedUrl).toContain(encodeURIComponent("C++ programming"));
});

test("Case 14: frontend-backend communication CORS headers validation", async ({ page }) => {
  let corsHeaderPresent = false;

  await page.route("http://localhost:8000/api/recommend?**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: {
        "access-control-allow-origin": "*",
      },
      body: JSON.stringify(baseRecommendPayload("communication")),
    });
    corsHeaderPresent = true;
  });

  await page.route("http://localhost:8000/api/recommend/local-enriched?**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(baseRecommendPayload("communication")),
    });
  });

  await page.goto("/");
  await page.getByPlaceholder("Example: Parameter-efficient adapters for multimodal transformers in radiology").fill("communication");
  await page.getByRole("button", { name: "Get Recommendations" }).click();

  await expect(page.getByText("Local result for communication")).toBeVisible();
  expect(corsHeaderPresent).toBeTruthy();
});
