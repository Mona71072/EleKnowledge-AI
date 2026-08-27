---
status: reference
last-verified: 2026-08-27
related-code: frontend/src/lib/documents.ts, frontend/src/app/doc/page.tsx, frontend/src/app/login/page.tsx, frontend/src/lib/safe-next-path.mjs, lambda/rag/rag-function/app.py
---

# E2E チェックリスト: 引用文書のログイン必須化（PR #50 / issue #68）

PR #50 のマージ条件だった実環境 E2E 4 ケースの**対象・期待・通る経路・再現手順**の定義。
実施結果は PR #50 にコメントで追記する（未実施のものを「済」にしない）。

- **環境**: develop 環境（Amplify PRODUCTION ブランチ）＋ `EleKnowledge-dev-phase2`（`CitationUriMode=presigned`）
- **テストユーザー**: itai（`itai.yuki@meltec.co.jp`、User Pool `ap-northeast-1_DN17ekXik`、CONFIRMED）
- **前提知識**: 現在は `presigned` モードだが、フロント `documentHref()` が S3 の署名付き URL を `s3://` に逆変換して `/doc` に流すため、`/doc` → `GET /rag/document` の導線は本モードのまま検証できる（`docs/api/rag.md`）

## 認証の登場人物（経路を読むための前提）

| トークン | TTL | 検証する場所 |
|---|---|---|
| ID トークン | 1時間 | API Gateway の Cognito Authorizer（署名と exp。**失効=revoke は見ない**） |
| リフレッシュトークン | 24時間（PR #46） | Cognito 本体。`fetchAuthSession` の自動リフレッシュに使う |

フロントの分岐は 2 つだけ（`frontend/src/lib/documents.ts` `resolveDocumentUrl`）:

- **client 分岐**: `getIdToken()` がトークンを返せない → **API を呼ばずに** `DocumentAuthRequiredError` → `/login?next=...`
- **server 分岐**: トークン付きで `GET /rag/document` を呼び、**401/403 応答を受けて** `DocumentAuthRequiredError` → `/login?next=...`

---

## ケース1: 未ログイン（client 分岐）

- **対象**: トークンが**無い**ブラウザでの `/doc` 直開き。フロントの client 分岐と `next` パラメータの付与
- **手順**: シークレットウィンドウで、チャット引用リンクの URL（`/doc?uri=...`）を直接開く
- **経路**: `/doc` → `resolveDocumentUrl` → `fetchAuthSession` がトークンなし → `DocumentAuthRequiredError` → `router.replace('/login?next=<元の/docパス>')`。**API 未到達**
- **期待**: ログイン画面へ誘導される。URL に `next=` が付いている。エラー画面・スピナー放置にならない

## ケース2: 期限切れトークン（古いタブ。(a)=自動復旧 / (b)=server 分岐が本命）

- **対象**: ログイン済みのまま**セッションが古くなった**タブ。特に **(b-2) サーバーが返す 401 をフロントが綺麗に処理できるか**（ケース1では API まで到達しないため、ここでしか踏めない経路）。旧方式ではこの状況で S3 の生の 403 XML がユーザーに見えていた
- **サブケースと期待**:
  - **(a) ID トークンのみ失効（リフレッシュ有効）** → `fetchAuthSession` が裏で自動リフレッシュし、**再ログインなしで文書が開くのが正**（ここでログインを求められたら不合格）
  - **(b-1) リフレッシュも無効・トークン取得不能** → client 分岐でログインへ（ケース1と同じ UX）
  - **(b-2) 「有効に見える」トークンをサーバーが拒否** → `GET /rag/document` が **401** → server 分岐でログインへ
- **短縮再現**（24h 放置の代わり。DevTools → Application → Local Storage の `CognitoIdentityServiceProvider.<ClientId>.<Username>.*` キーを操作する）:
  - **(a)**: ログイン後、`idToken` と `accessToken` のキーを**削除**（`refreshToken` は残す）→ 引用リンクをクリック → 自動リフレッシュで開けること
  - **(b-1)**: `admin-user-global-sign-out` でリフレッシュトークンを無効化（コマンドは付録）→ (a) と同様に `idToken`/`accessToken` を削除 → クリック → ログインへ
  - **(b-2)**: `admin-user-global-sign-out` 実行後、`idToken` の**署名部分（最後の数文字）を書き換え**（exp は有効のままなのでクライアントはそのまま送信する）→ クリック → API が 401 → ログインへ
- **経路**: (a) `fetchAuthSession`（リフレッシュ）→ 200 → 文書表示 / (b-1) client 分岐 / (b-2) API Gateway Cognito Authorizer が署名検証で拒否 → 401 → server 分岐

## ケース3: ログイン後復帰（next の往復と safeNextPath）

- **対象**: `next` パラメータの往復。ログイン成功後に**元の文書へ戻れる**こと。戻り先は `safeNextPath()`（`frontend/src/lib/safe-next-path.mjs`）で正規化・検査される
- **手順**: ケース1（または2(b)）でログイン画面に誘導された状態から、itai でログインする
- **経路**: `/login?next=...` → `signIn` 成功 → `router.push(safeNextPath(next))` → `/doc` が再マウント → `resolveDocumentUrl` → 200 → 文書表示
- **期待**: ホームではなく**元の `/doc` に戻り、そのまま PDF が開く**。（参考: `next` に外部 URL や `//host` を細工しても `/` に落ちることは単体テスト 7 件で固定済み）

## ケース4: 文書表示（happy path）

- **対象**: ログイン済みの正規導線全体。逆変換 → `/doc` → 都度発行 → PDF 表示
- **手順**: ログイン済みでチャットを行い、応答の引用リンクをクリックする
- **経路**: 引用リンク（`documentHref()` が署名付き URL を `s3://` に逆変換 → `/doc?uri=...`）→ `GET /rag/document`（Bearer IdToken）→ `is_allowed_document_uri` 許可判定 → 短命署名付き URL（TTL 300 秒・`Cache-Control: no-store`）→ リダイレクト → PDF 表示
- **期待**: PDF が表示される。**過去履歴**（#50 以前の期限切れ URL が保存されたメッセージ）の引用リンクでも同様に開けること（逆変換の検証）

---

## 付録: リフレッシュトークン無効化コマンド（ケース2(b)用）

itai の全セッションのリフレッシュトークンを即時無効化する（**itai 以外のユーザーには実行しない**）:

```bash
aws cognito-idp admin-user-global-sign-out \
  --user-pool-id ap-northeast-1_DN17ekXik \
  --username a7749a68-80d1-704b-fa3d-a88b3e4adaa0 \
  --region ap-northeast-1 --profile datautl-bple-mebs
```

注意: これは**リフレッシュトークンを失効させるだけ**で、発行済み ID トークンは exp（最長1時間）までAPI Gateway に受理される（Authorizer は revoke を見ない）。だからケース2の短縮再現では ID トークン側も削除 or 署名破壊してから確認する。

## 実施後

1. 4 ケースの結果（OK/NG・気づき）を PR #50 にコメントで追記
2. すべて OK なら `CitationUriMode=s3` で phase2 を再デプロイして移行完了（PR #50 本文の反映手順 4）
