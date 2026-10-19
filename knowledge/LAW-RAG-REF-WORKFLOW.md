---
status: draft
last-verified: "2026-10-19"
related-code:
  - EleKnowledge-AI/docs/features/development/legal-rag-design.md
  - EleKnowledge-AI/docs/features/development/legal-rag-target-laws.md
  - lambda/rag/rag-function/app.py
---

# 法令 RAG 参照（テーマカード用）

EleKnowledge **法令専用 KB**（e-Gov 条文・PoC **53法令**）と、テーマカードを **リンクだけ** で結ぶ手順。条文本文はカードに写さない。

## 正本（law_id）

| 種別 | 正本 |
| --- | --- |
| 収録一覧・`law_id`（S3 フォルダ名） | 本家 `develop` の `docs/features/development/legal-rag-target-laws.md`（作業ツリーに無ければ `git show origin/develop:docs/features/development/legal-rag-target-laws.md`） |
| 設計・検索条件・dev 限定 | 同 `docs/features/development/legal-rag-design.md` |

`law_id` は一覧表の **フォルダ名** 列をそのまま使う（例: `418AC0000000091_20250401_505AC0000000024`）。

## frontmatter

```yaml
  - ref_type: law_rag
    law_title: "高齢者、障害者等の移動等の円滑化の促進に関する法律"
    law_id: "418AC0000000091_20250401_505AC0000000024"
    retrieval: "mode=law"
    law_rag_status: current   # 一覧に載る現行版のみ。載らない法令は law_rag を付けない
```

- **53件に無い**もの（告示・通知・通達、自治体条例、JIS、イエローブック PDF 等）→ `law_rag` ではなく **OneNote 法令まとめ**（`401f288f-0e3f-4ada-b89d-14799070162d:*` のスナップショット）を `onenote_page` で索引する。
- **共有 KB**（C / TI / 据付基準）とは別系統。`resolve_kb_refs.py` の対象外。

## アプリ上の利用（利用者向けメモ）

- 法令チャットは **`mode=law`**。dev で `LAW_RAG_ENABLED` 等が揃ったときのみ有効（本番は原則オフ — 設計書参照）。
- カード §8「正式資料」に **EleKnowledge 法令チャット（dev）** と **e-Gov 条文 URL**（回答に付く）を1行書いてよい。

## カード本文ルール

1. Lists 出典は **`list_item_id` / §番号** のみ（`source-snapshots/首都工_…_初期スナップショット.md` は **照合用正本** — [CONTRACT.md](./CONTRACT.md)。§8 や本索引にファイルパスを繰り返さない）。
2. Lists / OneNote は **入口・現場メモ** の要約のみ。
3. **法律・施行令・施行規則**の条文は **法令 RAG が正本** — カードに条項を転記しない。
4. **告示・検査シート・社内整理**は **OneNote 法令まとめ** — 同様に転記しない。
5. §4「統合した回答」では「どの正本を開くか」を番号付きで書く（通常 RAG と法令 RAG を混同しない）。

## よく使うテーマ索引

現場頻度の高い **Lists / OneNote ↔ 法令 RAG** 対応表: [registry/LAW-FREQUENT-THEMES.md](./registry/LAW-FREQUENT-THEMES.md)（新テーマは表に行追加）。

## Wave 作業チェック

- [ ] テーマが **53法令のどれか**に当たるか `legal-rag-target-laws.md` で確認
- [ ] 法令系なら **LAW-FREQUENT-THEMES** に行があるか確認（無ければ追加）
- [ ] 当たる → 該当行すべて `ref_type: law_rag`（法・令・規則・関連省令を漏れなく）
- [ ] 当たらないが法令系豆知識 → OneNote 法令まとめ + Lists 入口のみ（従来どおり）
- [ ] `python3 scripts/knowledge/build_registry.py` で `card-source-links.jsonl` を更新
