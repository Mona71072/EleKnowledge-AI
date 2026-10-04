---
status: development
last-verified: 2026-09-18
related-code:
  - frontend/package.json
  - frontend/package-lock.json
  - infrastructure/sam/security-waf-template.yaml
  - infrastructure/sam/phase1-template.yaml
  - infrastructure/sam/phase2-template.yaml
  - infrastructure/sam/phase3-template.yaml
related-issues:
  - 21
  - 86
---

# 依存脆弱性と監視基盤の実施計画

> 最終検証: 2026-09-18 — リポジトリの依存定義・SAM テンプレート・Git 履歴および AWS 公式料金情報の確認

## 目的と優先順位

1. Issue #21 で production dependency の critical/high 脆弱性を解消または期限付き例外として管理する。
2. Issue #86 で WAF の記録・通知と RAG/chat のトレースを段階導入する。
3. troubleshooting は開発中であり、本計画では設計のみとする。SAM 反映、AWS リソース作成、デプロイはリリース判断後に別タスクで行う。

## 決定事項

| 論点 | 決定 |
| --- | --- |
| 依存更新 | 最小の非破壊更新を先行し、メジャー更新は別 Issue / PR に分ける。 |
| audit 残件 | critical/high は原則解消する。上流未修正など回避不能なものだけ、到達経路・代替防御・担当・解消期限を #120 に記録する。 |
| CI | production dependency の critical/high を検査する。例外は期限付きの記録によってのみ許可する。 |
| WAF ログ保管 | WAF ログは S3 に直接配信し、Block された要求だけを保存する。ライフサイクルを IaC で管理し、調査用の必要最小限のメトリクスとアラームは CloudWatch に置く。 |
| 通知先 | WAF Block などの運用通知は itai と mona の両方へ送る。 |
| X-Ray | RAG/chat を先行対象とし、API Gateway を含む。サンプリング率は実測後に調整する。 |
| troubleshooting | MethodSettings、ログ項目、アラーム、トレース、受入条件だけを設計する。実装・リソース作成は保留する。 |

## WAF ログのコスト前提

AWS WAF は、100 万 WAF リクエスト当たり 500 MB の WAF ログ配信を CloudWatch Logs または S3 に追加料金なしで含む。S3 宛ては、この無料分を超える vended log 配信料金と S3 の保存・リクエスト料金で構成される。本計画では Block された要求だけを保存するため、通常の許可済みトラフィックを保存する場合より配信量・保存量・個人情報露出を抑えられる。

月次費用は次で見積もる。実測前はログの平均サイズが最大の不確実性であり、リクエスト件数だけで固定額を約束しない。

```
超過配信量 = max(WAFログ配信量 - 0.5 GB × WAFリクエスト数（百万件）, 0)
月額 = 超過配信量 × ap-northeast-1 の WAF vended log 配信単価
     + S3 保存量 × S3 Standard 単価
     + S3 PUT/LIST/GET と Athena を使う場合のクエリ料金
```

概算の感度確認として、平均 1 KB/リクエストなら 100 万リクエストで約 1 GB のログとなり、無料分を超える配信量は約 0.5 GB。S3 保存部分は圧縮後容量に応じた小額だが、超過配信量は従量課金となる。初月は Cost Explorer の `S3-Egress-Bytes-WAFlog` と S3 の実測保存量で確認し、2 か月目以降の保持期間・アーカイブ階層を調整する。

根拠: [AWS WAF 料金](https://aws.amazon.com/jp/waf/pricing/)、[CloudWatch 料金](https://aws.amazon.com/jp/cloudwatch/pricing/)、[AWS WAF ログ料金](https://docs.aws.amazon.com/ja_jp/waf/latest/developerguide/logging-pricing.html)、[S3 料金](https://aws.amazon.com/jp/s3/pricing/)。

## 実施順と完了条件

### A. Issue #21 — 依存脆弱性

1. `npm audit --omit=dev` で現状を再取得し、直接・間接・到達不能候補に分類する。
2. 最小更新、lockfile 更新、CI 検査を実装する。
3. build、型検査、既存テスト、`/login`・`/chat`・資料表示の確認を行う。troubleshooting はリリース対象外のため、ビルド・既存テストのみとする。

完了条件は、critical/high がないこと、または例外を #120 に記録して合意済みであること。

### 2026-09-18 の再監査結果

> 最終検証: 2026-10-04 — Next.js 16.3.8、production audit、CI 例外撤去、Amplify Node.js 要件を確認

- `npm audit --omit=dev` の更新前は critical 2 件、high 8 件だった。
- 非破壊更新後は critical 0 件、high 1 件、moderate 1 件まで減少した。build は成功した。
- Next.js 16 系への移行で `postcss` の high を解消し、Issue #120 で追跡していた **2026-10-16 まで**の期限付き例外を CI から削除する。production dependency に critical/high があれば例外なく CI を失敗させる。Issue #21 は非破壊更新を含む PR #118 のマージにより完了した。

### B. Issue #86 — WAF logging と Block アラーム

1. S3 バケット、SSE-S3 暗号化、パブリックアクセス遮断、ライフサイクル、WAF logging configuration を IaC として設計・実装する。ログは Block のみとし、認証情報・Cookie・クエリ文字列をマスクする。
2. Block 数を短時間集計する CloudWatch アラームを設定し、SNS 経由で itai と mona に配信する。
3. テスト用の遮断イベントで、S3 記録・アラーム・両受信者への通知・ランブック手順を確認する。

Block 閾値、保存期間、夜間休日の対応水準は実トラフィック量と運用体制を確認して確定する。初期値を採用する場合も、見直し日を Issue #86 に記録する。

### C. Issue #86 — X-Ray

1. RAG/chat と該当 API Gateway のトレースを IaC に追加する。
2. 通常回答と障害相当のテストで、Gateway・Lambda・KB 検索・モデル生成の遅延を識別できることを確認する。
3. サンプリング、保存期間、コストを初月実測し、見直しを記録する。

### D. troubleshooting（設計のみ）

リリース時に必要な MethodSettings（access logging / metrics / throttling）、ログから除外する値、アラーム条件、X-Ray 対象、受入シナリオを別設計として確定する。リリース判断、実装 PR、リソース作成、デプロイはこの計画の完了条件に含めない。
