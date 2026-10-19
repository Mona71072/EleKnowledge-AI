# OneNote 追記循環（設計どおりの一往復・記録）

[design-2026-10-01-knowhow-flywheel.md](../../docs/design-2026-10-01-knowhow-flywheel.md) §14.7 / [concept-2026-10-19-kougi-senpai-knowledge-cycle.md](../../docs/concept-2026-10-19-kougi-senpai-knowledge-cycle.md) §8 に沿った **ローカル検証用テンプレ**。

## 例: KH-LINKS-WOS-DLDP-345

### 1. カード承認版（仮）

- `knowledge_id`: KH-LINKS-WOS-DLDP-345
- `card_version`: 1
- `card_hash`: （公開処理前は未算出）

### 2. OneNote 追記案（短文化）

```text
【追加】GAW→WOS切替時、制御盤にDL/DPコネクタが無いと100V系（ブザー等）が供給できない場合がある。
対象: LINKsで発生記録あり。全機種への適用は未確認。
詳細: （社内Markdown KH-LINKS-WOS-DLDP-345 v1）
確認日: 2026-10-19
```

### 3. KB照合（**後続・今回スコープ外**）

設計上は追記前に既存KBで関連資料を照合する。パイロット段階では Lists / draft / カードの一往復のみ先に通す。

- [ ] （後続）既存KBで TI-1335 / KB3AB3500 関連を検索
- [ ] （後続）「資料で足りる」なら追記は短い案内+リンクに留める

### 4. 追加済み記録（必須項目）

| 項目 | 値 |
| --- | --- |
| 反映先 | （OneNote URL またはページ特定情報・**未記入可**） |
| 転記した版 | KH-LINKS-WOS-DLDP-345 / card_version 1 |
| 状態 | 追記案作成済み（**コピー済み≠追加済み**） |

### 5. 逆引き

- `registry/card-source-links.jsonl` に lists 345 と draft `knowhow-elv-links-wos-switch-dldp-connector-id345` を保持

## 否定テスト（設計 §14.7）

- コピーだけで「追加済み」にしない
- 掲載先または転記版が無い申告を追加済みにしない
- Markdown撤回時は転記先を逆引き（手順のみ。自動OneNote書込はしない）
