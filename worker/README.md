# フィルター生成の定期起動

Cloudflare WorkersのCron Triggerから、既存のGitHub Actionsを毎日午前3時（日本時間）に起動します。GitHubのscheduleイベントを使わないため、公開リポジトリの60日無活動によるschedule停止に依存しません。

このフォルダは起動部分です。フィルターの取得・変換・検証・Pagesへの公開は、呼び出し先のワークフローで実施します。iOSアプリの実装は変更しません。

## 1. GitHubワークフローを変更

対象は [taisuke-inoue/webkit-adblock-filters](https://github.com/taisuke-inoue/webkit-adblock-filters) の `main` ブランチ、`.github/workflows/update-filters.yml` です。Workerからの起動確認後、既存のワークフローの `on` を次に置き換え、`schedule` を削除してください。既存のjobsは維持します。

```yaml
on:
  workflow_dispatch:

concurrency:
  group: webkit-filter-publish
  cancel-in-progress: false
```

最初にGitHubのActions画面の「Run workflow」で正常完了を確認します。既にワークフローが無効化されている場合は有効化してください。GitHub側の実行制限、認証失効、混雑による待機まで解消する仕組みではありません。

## 2. GitHubトークンを作成

Fine-grained personal access tokenで対象リポジトリだけを選択し、Repository permissionsの **Actions: Read and write** を付与します。トークンの有効期限を管理してください。チャットやGit管理ファイルには貼りません。

## 3. Workerを設定・公開

このディレクトリで `wrangler.example.jsonc` を `wrangler.jsonc` にコピーします。指定されたリポジトリの接続先は設定済みです。

| 設定 | 内容 |
| --- | --- |
| GITHUB_OWNER | taisuke-inoue |
| GITHUB_REPO | webkit-adblock-filters |
| GITHUB_WORKFLOW | update-filters.yml |
| GITHUB_REF | main |

```sh
npx wrangler@4 login
npx wrangler@4 secret put GITHUB_TOKEN
npx wrangler@4 deploy
```

`secret put` の入力欄にトークンを貼ります。初回でWorkerが未作成の場合は、作成の案内に従います。既存のCloudflare Pages編集用トークンではなく、WorkerのデプロイにはWorkers用権限が必要です。上のloginは対話式認証です。

HTTP公開URLとプレビューURLは無効です。Cron設定の反映には最大15分程度かかることがあります。

## 4. 確認

外部サービスを呼ばないテスト:

```sh
node --test test/worker.test.mjs
```

実環境ではWorkerの実行ログと、GitHub Actionsの実行履歴を照合します。Workerの成功ログは「GitHubが起動要求を受理した」ことだけを示し、変換・公開成功はGitHub側で確認します。起動要求が失敗するとWorker実行をエラーにしますが、この構成にメール通知は含まれません。

GitHubの自動スケジュール削除はWorker設定・認証・起動確認と合わせて行い、移行中の更新停止を避けてください。

## 公式資料

- https://developers.cloudflare.com/workers/configuration/cron-triggers/
- https://developers.cloudflare.com/workers/configuration/secrets/
- https://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event
