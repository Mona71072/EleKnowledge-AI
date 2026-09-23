# 実装ログ索引（2026-09）

> **このファイルは目次だけ。** 数字・手順・いまの正解はリンク先が正。本文をここに写さない。

| 話題 | 正本 |
|---|---|
| セッション見出し（非同期 `sessionTitle`、Sonnet 5 互換） | [docs/api/rag.md](./api/rag.md) / [docs/api/chat.md](./api/chat.md) / [docs/data-model.md](./data-model.md) |
| Global Sonnet 5 採用・本人照合 | [docs/decisions-2026-09-17-global-sonnet5-user-verification.md](./decisions-2026-09-17-global-sonnet5-user-verification.md) |
| チャットログ S3 アーカイブ失敗の復旧 | [docs/ops-runbook.md](./ops-runbook.md) §5.5 |
| Cognito メール上限・事前発行・未確認の確認済み化 | [docs/ops-runbook.md](./ops-runbook.md) §5.6 / `scripts/ops/provision_users.py` / `scripts/ops/confirm_unconfirmed_users.py` |
| PR 会話・マージ担当・合意後はどちらが押してもよい | [docs/decisions-2026-09-10-pr-conversation.md](./decisions-2026-09-10-pr-conversation.md) / [AGENTS.md](../AGENTS.md) §マージ担当 |
| WAF 利用者レート（Authorization 集計、既定 300/5min） | [docs/api/common.md](./api/common.md) / [infrastructure/sam/security-waf-template.yaml](../infrastructure/sam/security-waf-template.yaml) |
| 運用ダッシュボード v2（API・設計） | [docs/api/metrics.md](./api/metrics.md)（draft）/ [docs/design-2026-09-10-dashboard-v2.md](./design-2026-09-10-dashboard-v2.md) |

2026-07 以前の経緯は [impl-log-2026-07-29-clarify-and-page.md](./impl-log-2026-07-29-clarify-and-page.md)。
