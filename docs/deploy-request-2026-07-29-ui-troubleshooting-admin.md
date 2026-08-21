# UI 改良 + トラブルシューティング管理者制限 デプロイ依頼書

@yukiworkspace（itai） cc: デプロイ担当

**依頼日:** 2026-07-29  
**ブランチ:** `mona` → **`develop` へ PR #27 マージ後に作業**  
**緊急度:** 通常（セキュリティ修正 PR #27 と同一 PR に含まれる）

---

## 0. 自動 vs 手動

| 対象 | 反映方法 | itai の作業 |
|---|---|---|
| **Amplify（フロント）** | `develop` マージで **自動** | **不要** |
| **phase3 Lambda（TS 管理者制限）** | git push では **反映されない** | **必須** — 下記 phase3 SAM |

---

## 1. 何を直したか

| 区分 | 内容 |
|---|---|
| ホーム UI | ヒーロー刷新（クイック質問・時間帯挨拶）、機能カード優先、折りたたみガイド、品質書類チェック削除 |
| チャット UI | 空状態サジェスト、メッセージバブル整理、コピー機能、折りたたみフィルター |
| TS 管理者制限（フロント） | `/troubleshooting` を AdminOnlyGuard で保護、非管理者はホームで非クリック表示 |
| TS 管理者制限（API） | orchestrator / history が非 admin に 403 |

---

## 2. SAM デプロイ（phase3）

```bash
cd infrastructure/sam
sam build --template phase3-template.yaml
sam deploy --config-file samconfig-phase3.toml --profile datautl-bple-mebs
```

> スタック名: `troubleshooting-dev`（samconfig-phase3.toml 参照）

---

## 3. 確認項目

- [ ] ホーム: クイック質問 → チャットにプリフィルされる
- [ ] ホーム: 非管理者は TS カードがクリック不可
- [ ] `/troubleshooting`: 非 admin は 403 画面、admin は利用可
- [ ] TS API: 非 admin の Bearer トークンで analyze / history が 403

---

## 4. ロールバック

- フロント: Amplify の前バージョンへロールバック可能
- Lambda: 前リビジョンへ `update-function-code` または CFn ロールバック（phase3 スタック）
