# お知らせ機能 デプロイ依頼書（CORS + 予約公開）

@yukiworkspace（itai） cc: デプロイ担当

**依頼日:** 2026-07-29  
**ブランチ:** `mona` → **`develop` へ PR マージ後に作業**  
**緊急度:** 高（ホームの「運営からのお知らせ」がブラウザから読めない／予約公開が効かない）  
**対象アカウント／リージョン:** `730972069979` / `ap-northeast-1`  
**必要プロファイル:** `datautl-bple-mebs`  
**対象スタック:** `announcements-monitoring-dev` のみ（phase1/2/3 は触らない）

---

## 0. itai 向け：何が自動で、何が手動か

| 対象 | 反映方法 | あなた（itai）の作業 |
|---|---|---|
| **Amplify（フロント）** | `develop` マージで **自動** | **不要**（`relativeTime` の微修正のみ） |
| **announcements-monitoring（Lambda / API GW）** | git push では **反映されない** | **必須** — 下記 SAM 1 本 |

**お願い:**

1. PR の内容を確認（リソースポリシー・新規 publisher Lambda・破壊的変更の有無）
2. `develop` マージ後、本書の **§2 SAM デプロイ** を実行
3. §3 の確認コマンドで OPTIONS が 200、予約公開が届くことを確認

---

## 0.1. 3行サマリ

1. **CORS preflight（OPTIONS）** を IP ホワイトリスト外でも通す（データ API は従来どおりオフィス IP 制限）
2. **予約公開**: `scheduled` かつ `publishAt<=now` をフィードに出し、5 分毎の publisher で `published` に昇格
3. **デプロイは announcements-monitoring スタック 1 本だけ**

---

## 1. 何を直したか

| ID | 内容 | 変更ファイル |
|----|------|------------|
| A-1 | API GW ResourcePolicy: `OPTIONS/*` は全許可、それ以外は従来どおり AllowedIPList | `announcements-monitoring-template.yaml` |
| A-2 | 4XX/5XX GatewayResponse に CORS ヘッダを追加（ブラウザがエラー内容を読めるように） | 同上 |
| A-3 | Read: `scheduled` かつ期限到来分もフィードに含める | `lambda/announcements/read/app.py` |
| A-4 | Publisher Lambda（rate 5 min）で `scheduled` → `published` 昇格 | `lambda/announcements/publisher/app.py` + テンプレ |
| A-5 | 未来日時の `relativeTime` が「たった今」になる不具合を修正 | `frontend/src/lib/announcements.ts` |
| A-6 | 時刻をサーバ側で UTC `YYYY-MM-DDTHH:MM:SS.sssZ` に正規化（JS/Python/オフセット混在による文字列比較ずれを防止） | `lambda/announcements/*/timeutil.py` + write/read/publisher |

---

## 2. SAM デプロイ（必須）

```bash
cd infrastructure/sam
sam build --template announcements-monitoring-template.yaml
sam deploy --config-file samconfig-announcements-monitoring.toml --profile datautl-bple-mebs
```

> スタック名: `announcements-monitoring-dev`（toml 参照）  
> changeset に **ResourcePolicy の差し替え** と **`announcements-publisher-dev` 新規** が出る想定です。確認して実行してください。

---

## 3. デプロイ後の確認

### 3.1 CORS preflight（オフィス外 PC でも OPTIONS は 200 になること）

```bash
API=https://0q3vewys59.execute-api.ap-northeast-1.amazonaws.com/dev

curl -sS -D - -o /dev/null -X OPTIONS "$API/announcements" \
  -H 'Origin: https://example.com' \
  -H 'Access-Control-Request-Method: GET' \
  -H 'Access-Control-Request-Headers: authorization,content-type' \
  | head -20
# 期待: HTTP/2 200（または 204）と access-control-allow-origin / allow-methods
```

### 3.2 データ API は従来どおり IP 制限

```bash
# 許可 IP 外からの GET（トークンなし）→ 403（IP）または 401（Cognito）のいずれか
curl -sS -o /tmp/a.json -w '%{http_code}\n' "$API/announcements?limit=1"
cat /tmp/a.json
```

オフィス回線 + 有効な Cognito ID トークンでは 200 で `announcements` 配列が返ること。

### 3.3 予約公開

1. 管理画面 `/admin/announcements` で **予約**（過去の publishAt、または直後の時刻）を作成
2. ホームの「運営からのお知らせ」に **即時 or 数分以内** に出ること
3. 5 分以内に管理画面の状態が **予約 → 公開** になること（publisher）

```bash
# publisher の直近ログ
aws logs tail /aws/lambda/announcements-publisher-dev --since 15m \
  --profile datautl-bple-mebs --region ap-northeast-1
```

### 3.4 Amplify

フロントは `develop` マージ後に自動反映。追加作業不要。

---

## 4. ロールバック

```bash
# 直前の changeset / スタックイベントを確認のうえ、必要なら前リビジョンへ
aws cloudformation describe-stack-events \
  --stack-name announcements-monitoring-dev \
  --profile datautl-bple-mebs --region ap-northeast-1 \
  --max-items 20
```

フロントのみ戻す場合は Amplify の前ビルドへロールバック可能。

---

## 5. 補足（mona 側で分かっていること）

- **デプロイ前は本番 OPTIONS はまだ 403**（この修正は `sam deploy` 後に効く）。マージだけでは直らない。
- ローカル `NEXT_PUBLIC_SKIP_AUTH=true` の偽トークンでは本番 API は呼べない（想定どおり）。動作確認はログイン済み + オフィス IP、または依頼書の curl。
- phase1/2/3・他スタックは今回の対象外。
- changeset で **ResourcePolicy 差し替え**・**publisher 新規**・**`DataTraceEnabled: false`** を目視確認すること（`true` に戻っていないか）。
- CORS の OPTIONS 全開放は preflight 専用。GET/POST 等のデータ API は引き続き IP + Cognito。
- 既存行の `publishAt` は、管理画面で再保存するか publisher 昇格時に正規化される。新規作成は常に正規化済み。