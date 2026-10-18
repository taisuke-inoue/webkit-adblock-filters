export async function dispatchWorkflow(env, request = fetch) {
  const required = ["GITHUB_OWNER", "GITHUB_REPO", "GITHUB_WORKFLOW", "GITHUB_REF", "GITHUB_TOKEN"];
  for (const key of required) {
    if (typeof env[key] !== "string" || !env[key].trim()) {
      throw new Error(`Missing configuration: ${key}`);
    }
  }

  const path = [env.GITHUB_OWNER, env.GITHUB_REPO].map(encodeURIComponent).join("/");
  const workflow = encodeURIComponent(env.GITHUB_WORKFLOW);
  const response = await request(
    `https://api.github.com/repos/${path}/actions/workflows/${workflow}/dispatches`,
    {
      method: "POST",
      headers: {
        Accept: "application/vnd.github+json",
        Authorization: `Bearer ${env.GITHUB_TOKEN}`,
        "Content-Type": "application/json",
        "User-Agent": "onebar-filter-scheduler",
        "X-GitHub-Api-Version": "2022-11-28",
      },
      body: JSON.stringify({ ref: env.GITHUB_REF }),
      redirect: "error",
      signal: AbortSignal.timeout(20_000),
    },
  );

  // Dispatch受理はビルド・配信の完了を意味しない。
  if (response.status !== 204) {
    throw new Error(`GitHub workflow dispatch failed (HTTP ${response.status})`);
  }
}

export default {
  async scheduled(_controller, env, _ctx) {
    // 応答が失われた場合の二重起動を避けるため、無条件の自動リトライはしない。
    await dispatchWorkflow(env);
    console.log("GitHub accepted the filter build request.");
  },

  async fetch() {
    // 公開HTTPリクエストからワークフローを起動させない。
    return new Response("Not found", { status: 404 });
  },
};
