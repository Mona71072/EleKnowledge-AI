# 知識地図（AI向け）

人が一覧として読む完成資料ではなく、工技先輩が **統合済みMarkdown → 出典（Lists / OneNote / KB）** へ辿るためのレイヤー構成。カード更新時は **保存スナップショット** と必ず突合する（[CONTRACT.md](./CONTRACT.md)／[decisions](../docs/decisions-2026-10-19-knowledge-evidence-sources.md)）。

| ディレクトリ | 役割 | 回答に使うか |
| --- | --- | --- |
| `source-snapshots/` | Lists・OneNoteの取得時点（不変） | 一般利用者向け検索対象外 |
| `drafts/` | Vault由来の写し棚（630件級） | 照合・編集用（**出典ではない**） |
| `cards/` | テーマ別の統合ノウハウ（入口 [cards/INDEX.md](./cards/INDEX.md)） | **第一探索** |
| `registry/` | ID・版・カード↔原記録の機械可読対応 | 照合・逆引き |
| `queues/repair/` | frontmatter不正など、回答から隔離 | 使わない |
| `validation/` | ナビゲーション・更新循環の確認記録 | 運用 |

契約の正本: [CONTRACT.md](./CONTRACT.md)  
機種・制御方式・Vault 棚: [registry/APPLICABILITY-TAXONOMY.md](./registry/APPLICABILITY-TAXONOMY.md)  
出典3種・照合手順: [docs/decisions-2026-10-19-knowledge-evidence-sources.md](../docs/decisions-2026-10-19-knowledge-evidence-sources.md)  
カード共通: [cards/_SOURCE-LEGEND.md](./cards/_SOURCE-LEGEND.md)  
Wave 突合記録: [validation/snapshot-crosswalk-wave1-2.md](./validation/snapshot-crosswalk-wave1-2.md)  
保全方針（2026-10-19）: [PRESERVATION-2026-10-19.md](./PRESERVATION-2026-10-19.md)

**KB:** 資料番号 → カタログ索引 → PDF 本文確認 → カード要約（[KB-REF-WORKFLOW.md](./KB-REF-WORKFLOW.md)）。Wave 突合表: [validation/kb-ref-status-wave1-2.md](./validation/kb-ref-status-wave1-2.md)。RAG アプリ連携は後続 PR。
