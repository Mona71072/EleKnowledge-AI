---
snapshot_type: "reconciliation_wave_log"
wave: 65
generated_on: "2026-10-19"
---

# Wave 65（OneNote 候補一括適用・要約 curate）

## 新規テーマ

なし。**累計 Wave テーマ: 395**。

## 実施

### 拡張 hit 再検証

- `verify_onenote_extended_hits.py` — **118 通過 / 15 却下**（8 文字 prefix のみ等）
- `lists-onenote-extended-hits.jsonl` を verified のみに更新

### navigation 一括（監査台帳）

- `apply_onenote_wave_audit.py --apply` — **113** カードに index/cross 索引（§3 navigation）
- `normalize_onenote_index_sections.py` — 追加 **37** 件簡略化

### content / hybrid 要約（連携付き）

| クラスタ | カード | 連携 |
| --- | --- | --- |
| PuTTY | 130, 119, 415 | 233/228 SCU、336 エレナビ、373 DOAS |
| ER DL/DOT | 348, 379 | 共有 `c551ee58…:1`、420 吊り |
| DOAS 工事 | 373 | 415 ELSGW、336 |
| ソフト MNT | 170 | 173/186 |
| MELD バッテリー | 174 | 227 遮煙、132 |
| VHP LO | 91 | Lists 91 正、RSRL 混載禁止 |
| DC 電源 | 249 | 267 乗場電源 |
| 遮煙 duplicate | KH-SMOKE-DOOR-MELD-227 | 主カード ALL-SMOKE-FIRE… と索引共有 |
| MRL B3 | 438 | :161 索引 navigation、354 連携 |

### 却下・未付与

- **Lists §55** 等: 拡張 prefix hit **却下**（索引 :156 との誤一致）— OneNote 未付与のまま

## registry

- `build_onenote_audit_ledger.py` — **wave_pending_candidate: 0**（card refs **185** / unique onenote **83**）
- Lists **§55** 拡張 `:157` — **verify 却下**（①/② 枝番不一致）
- `build_registry.py`: **repair 0**

## 次

- 未検出 ~108 Lists 節の手動 grep
- §384 Lists 原因文完成待ち
- カード KB 公開パイプライン（設計どおり未実装）
