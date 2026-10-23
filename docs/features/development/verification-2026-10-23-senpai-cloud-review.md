---
status: draft
last-verified: 2026-10-23
related-code:
  - lambda/rag/rag-function/senpai_research_*.py
  - lambda/rag/senpai-synthesis/
  - infrastructure/sam/phase2-template.yaml
---

# #195 クラウドでの技術確認と未統合差分

## 対象と結果

> 最終検証: 2026-10-23 — #195 head d0dd03977a61e5003bf2064e82a2cb857f629e20の取得済みソース、関連テスト、SAMをローカルのLinuxで検証。実AWS・Bedrock・Windows・ブラウザ試験は未実施。

GitHub連携で取得したRAGモジュール・調査ジョブテスト・SAM等59ファイルのGit blob SHAを照合し、全件一致を確認した。まとめLambdaとチャット履歴Lambda、テスト用IAM解析も同じheadから取得した。対象コードの変更は行っていない。

| 確認 | 結果・限界 |
| --- | --- |
| 調査ジョブ＋まとめの関連テスト | 280件成功。Python 3.12、pytest 9.1.1、boto3 1.43.118、moto 5.2.4。CIのPython 3.13とは別環境 |
| 削除済み・期限切れまとめの再取得 | 既存のrace_with_hidden_winner_row等を含むまとめテスト成功。隠れた既存行を200で再公開しない回帰範囲 |
| Phase 2のSAM静的検証 | cfn-lint 1.58.0で終了0。RagApi限定W1028抑制を含む現headの結果。sam validate --lintそのもの・AWS変更セットは未実行 |
| 実回答の品質 | 未検証。モデル・KBを模擬したテストの成功を、技術的正解率・出典の意味的一致・実モデル受入と扱わない |
| Windowsのカード改行 | .gitattributesのLF固定は現headに存在。今回Windowsチェックアウト・全カードの台帳照合は未実施 |

再現コマンド（リポジトリルート、合成用AWS環境変数、モデルとKBはテスト内で模擬）:

```bash
test_paths=()
for file in tests/unit/test_senpai_research*.py tests/unit/test_senpai_synthesis.py; do
  if [[ "$file" != *research_eval.py ]]; then test_paths+=("$file"); fi
done
python -m pytest "${test_paths[@]}" -q --tb=short
cfn-lint infrastructure/sam/phase2-template.yaml
```

評価データの整合テストtest_senpai_research_eval.pyは、カード・評価fixture一式の取得を要するため今回の280件から除外した。現場報告・全フロント・全Python・実配備試験はこの検証に含めない。初回の取得不足とローカル再構成時の末尾改行差による失敗は、原本のGit blob照合で是正してから上記範囲を再実行した。製品コードの失敗として報告しない。

## itaiとの統合条件

> 最終検証: 2026-10-23 — #195/#200の最新コメントとGitHubコミット取得結果を照合。

- origin/itaiはb9076cbd。T17のccd3dcc3とT20の152c2281はGitHub APIでNo commit found。コメントにもローカルのみ・未pushとある。クラウドからの取得・統合は未実施。
- 取得後はmonaのd504d9d（引用・根拠0件・予算等）とdaa1c8c（役割・説明の統合・意図別形式・understanding受渡し）の上で差分を確認する。itaiの根拠判定を優先しつつmonaの説明指示を残す方針は、既存コメントの統合提案として扱う。未取得の変更を推測で再実装しない。
- origin/itaiの共通知識実装では、非adminの確認者がapproved保存まで行える。#200最新回答では、キーマンの内容承認と管理者の最終追加・公開を分離する。採用前にAPI/UI/IAM・操作再試行を含め契約・実装・テストを更新する。専用環境の配備記録を改訂後の共有環境受入と扱わない。
- #200は共同方針文書、#195は実装・テスト・実装仕様という分担を維持する。itai専用AWS/Amplify設定を共有devへ一括コピーしない。
- #195へのApprove・マージ可・共有dev配備・実データ投入・KB同期・有料実測は今回行っていない。mona向け公開・停止試験の結果返信も未取得。

## CIの別ブロッカー

#201はdevelopへ反映済み。#194のdevelop取込後CIで、Next.jsのGHSA-2464-fhr4-w9xw / GHSA-p3m5-59mp-jv5r / GHSA-673q-mjm6-r5xrによる全依存監査失敗を確認した。依存修正は独立PRで扱い、調査ジョブや共同確認文書へ混ぜない。過去の#195 CI成功だけを現在のマージ条件に流用せず、最終headで再確認する。
