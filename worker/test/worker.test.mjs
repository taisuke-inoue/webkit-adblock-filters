import test from "node:test";
import assert from "node:assert/strict";
import worker, { dispatchWorkflow } from "../src/worker.mjs";

const env = {
  GITHUB_OWNER: "test-owner",
  GITHUB_REPO: "filters",
  GITHUB_WORKFLOW: "build-filters.yml",
  GITHUB_REF: "main",
  GITHUB_TOKEN: "test-token-not-a-secret",
};

test("dispatches the configured workflow and branch with authentication", async () => {
  let calls = 0;
  await dispatchWorkflow(env, async (url, options) => {
    calls++;
    assert.equal(url, "https://api.github.com/repos/test-owner/filters/actions/workflows/build-filters.yml/dispatches");
    assert.equal(options.method, "POST");
    assert.equal(options.headers.Authorization, `Bearer ${env.GITHUB_TOKEN}`);
    assert.deepEqual(JSON.parse(options.body), { ref: "main" });
    assert.equal(options.redirect, "error");
    assert.ok(options.signal instanceof AbortSignal);
    return new Response(null, { status: 204 });
  });
  assert.equal(calls, 1);
});

for (const key of Object.keys(env)) {
  test(`missing ${key} stops before network access`, async () => {
    await assert.rejects(
      dispatchWorkflow({ ...env, [key]: "" }, () => assert.fail("Unexpected request")),
      new RegExp(`Missing configuration: ${key}`),
    );
  });
}

for (const status of [401, 403, 404, 422, 429, 500]) {
  test(`HTTP ${status} fails without leaking response body or token`, async () => {
    await assert.rejects(
      dispatchWorkflow(env, async () => new Response(env.GITHUB_TOKEN, { status })),
      { message: `GitHub workflow dispatch failed (HTTP ${status})` },
    );
  });
}

test("network failures propagate without retrying a potentially accepted dispatch", async () => {
  let calls = 0;
  await assert.rejects(dispatchWorkflow(env, async () => {
    calls++;
    throw new Error("Network unavailable");
  }), /Network unavailable/);
  assert.equal(calls, 1);
});

test("public HTTP requests cannot trigger a build", async () => {
  const response = await worker.fetch();
  assert.equal(response.status, 404);
});
