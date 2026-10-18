# webkit-adblock-filters

Automated WebKit Content Blocker rules (`WKContentRuleList` JSON) compiled from AdGuard filters using [SafariConverterLib](https://github.com/AdguardTeam/SafariConverterLib).

## Included Filters
* AdGuard Base filter (ID: 2)
* AdGuard Tracking Protection filter (ID: 3)
* AdGuard Japanese filter (ID: 7)
* AdGuard Mobile Ads filter (ID: 11)
* AdGuard Mobile App Banners filter (ID: 20)

## License
This repository and the generated filter lists are licensed under the **GNU General Public License v3.0 (GPLv3)**.
Original filter lists are maintained by [AdGuard](https://github.com/AdguardTeam/AdguardFilters).

## Cloudflare Pagesへの配信

GitHub Actionsで作成した同じ `dist/` をArtifact（5日間）とPagesの両方に送ります。
PagesはDirect Uploadプロジェクトを作成し、production branchを `main` にします。

Repository Settings → Secrets and variables → Actions:

- Secret `CLOUDFLARE_ACCOUNT_ID`: 配信先アカウントID。
- Secret `CLOUDFLARE_API_TOKEN`: 対象アカウントのCloudflare Pages Edit権限を持つトークン。
- Variable `CLOUDFLARE_PAGES_PROJECT`: Pagesプロジェクト名。

これらはWorker側の `GITHUB_TOKEN` と別です。トークンをリポジトリに保存しません。
mainブランチで正常に生成・構造検証された場合だけPagesへ公開します。
検証失敗では公開ステップへ進まず、既存の配信を維持します。
現時点の検証はJSON構造・件数・取得ヘッダーまでです。WebKitでの実コンパイル検証は未追加です。
Safari対象バージョンは26（iOS 26以降）です。
Workerからの初回起動成功を確認してから、GitHub側のscheduleを削除してください。

Workerの設定・テスト手順は [worker/README.md](worker/README.md) を参照してください。

配信先: https://webkit-adblock-filters.pages.dev/
フィルター: https://webkit-adblock-filters.pages.dev/rules.json
