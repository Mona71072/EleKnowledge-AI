---
status: development
last-verified: 2026-10-15
related-code: frontend/src/components/announcements/AnnouncementsSection.tsx, frontend/src/app/admin/announcements/page.tsx, frontend/src/app/globals.css, frontend/src/lib/announcement-display.mjs, frontend/tests/announcement-display.test.mjs
---

# お知らせのMarkdown・投稿日・既読表示

## 不具合と対応

お知らせ詳細と管理画面のプレビューはReactMarkdownで本文をHTMLへ変換するが、`prose`用のCSSが存在せず、Tailwindのリセットにより見出し・リスト記号・段落余白が表示されない。

追加依存を導入せず、お知らせ専用の`announcement-markdown`クラスで両画面を共通装飾する。見出し、段落、番号付き・番号なしリスト、リンク、引用、コード、区切り線、表を対象とする。長いコードや表は横スクロールできるようにする。

本文のMarkdown形式・保存済みデータ・公開状態・APIは変更しない。ReactMarkdownのraw HTMLを有効化せず、既存の安全な描画方式を維持する。

## 投稿日と既読表示

2026-10-15の利用者依頼により、一覧と詳細の投稿日は日本時間の`YYYY/MM/DD`のみ表示する。メンテナンスの開始・終了日時は日時を維持する。

`NEW`と新着件数は、お知らせの詳細を開いた時点でその1件だけ既読にする。一覧の表示だけでは既読にしない。既読IDをCognitoのユーザーIDごとにブラウザのlocalStorageへ保存し、ホーム・全件一覧・再読み込み・同じブラウザのタブ間で共有する。別端末・別ブラウザとの同期は行わない。保存できない場合も閲覧中は既読表示を更新し、画面を壊さない。

従来の一覧表示時刻による一括既読値は、実際の閲覧を表していないため引き継がない。保存済みの本文を編集しても同じお知らせIDは既読のままとする。

## 確認項目

- 2026-10-15：最新developを基準にLint（既存の警告4件、エラーなし）、TypeScript型チェック、本番ビルド（17ページの静的生成を含む）、フロントエンドテスト68件が成功。日付境界、1件単位の既読、アカウント分離、保存値の異常、保存失敗、他タブの既読保持を含む。
- 2026-10-15：ReactMarkdownと実際の専用CSS、TailwindのリセットCSSを使ったローカルHTMLをEdgeで描画し、法令チャット告知の見出し・手順番号・箇条書き・段落余白を画像確認。実サイトへの反映確認は未実施。
- 開発環境への反映後、お知らせ詳細と管理画面のプレビューで見出し、リスト記号、段落余白、長い表・コードのスクロールを確認する。
