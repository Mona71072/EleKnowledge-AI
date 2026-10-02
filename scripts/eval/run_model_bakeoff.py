#!/usr/bin/env python3
"""
生成モデルの切替前比較（bake-off）

同じ質問・同じ検索結果（本番 Lambda と同一の retrieve 経路）に対して、
複数の Bedrock モデルで回答を生成し、目視比較用の Markdown と JSON を出力する。

- 検索は lambda/rag/rag-function/app.py を import して本番と同じ手順（run_retrieve_eval と同じ流儀）
- 生成は app.generate_response_with_claude をそのまま使い、モデル ID だけ差し替える
- Sonnet 5 / Opus 4.7 以降は temperature 指定を 400 で拒否するため、
  リクエスト本文から sampling 指定を外し thinking を明示（本番反映時に app.py 側で同じ対応が必要）
- DynamoDB には書かない。Bedrock の Retrieve と InvokeModel だけを呼ぶ

使い方:
  python scripts/eval/run_model_bakeoff.py \
    --questions scripts/eval/bakeoff_questions.jsonl \
    --models "haiku45=jp.anthropic.claude-haiku-4-5-20251001-v1:0,sonnet5=global.anthropic.claude-sonnet-5" \
    --out eval-results/model-bakeoff.md

質問ファイル（jsonl）: {"id": "Q01", "query": "...", "filters": {"modelType": "AXIEZ", "category": []}, "note": "..."}
"""

import argparse
import importlib.util
import io
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EVAL_SCRIPT = REPO_ROOT / "scripts" / "eval" / "run_retrieve_eval.py"

# 概算用の単価（USD / 1M tokens）。Anthropic 公式単価 × 地域指定プレミアム(jp.=1.1)。請求額は AWS 料金表が正。
PRICE_TABLE = [
    ("haiku-4-5", 1.0, 5.0),
    ("sonnet-4-6", 3.0, 15.0),
    ("sonnet-4-5", 3.0, 15.0),
    ("sonnet-5", 2.0, 10.0),
    ("opus-4-7", 5.0, 25.0),
    ("opus-4-8", 5.0, 25.0),
    ("opus-5", 5.0, 25.0),
]

# 新 API 世代（sampling 指定不可・thinking 明示推奨）
NEW_API_MARKERS = ("sonnet-5", "opus-4-7", "opus-4-8", "opus-5", "fable")


def parse_args():
    p = argparse.ArgumentParser(description="RAG 生成モデルの切替前比較")
    p.add_argument("--questions", required=True, help="質問 jsonl")
    p.add_argument("--models", required=True,
                   help='"label=modelId,label=modelId" 形式。先頭が基準（現行）')
    p.add_argument("--kb-id", default=None)
    p.add_argument("--env", default="dev")
    p.add_argument("--region", default=os.environ.get("AWS_REGION", "ap-northeast-1"))
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--out", default=None, help="Markdown 出力先（省略時 eval-results/model-bakeoff-<時刻>.md）")
    return p.parse_args()


def load_eval_helpers():
    spec = importlib.util.spec_from_file_location("rag_eval_helpers", str(EVAL_SCRIPT))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def parse_models(spec: str) -> list:
    out = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        label, model_id = part.split("=", 1)
        out.append((label.strip(), model_id.strip()))
    if not out:
        raise SystemExit("--models が空です")
    return out


def price_for(model_id: str):
    premium = 1.1 if model_id.startswith(("jp.", "apac.", "us.", "eu.")) else 1.0
    for marker, pin, pout in PRICE_TABLE:
        if marker in model_id:
            return pin * premium, pout * premium
    return None, None


def load_questions(path: str, limit=None) -> list:
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            j = json.loads(line)
            if j.get("skip"):
                continue
            rows.append(j)
    return rows[:limit] if limit else rows


class InvokeRecorder:
    """app.bedrock_runtime.invoke_model を差し替え、モデル別の互換調整と計測を行う。"""

    def __init__(self, mod):
        self.mod = mod
        self.real = mod.bedrock_runtime.invoke_model
        self.last = None

    def __enter__(self):
        self.mod.bedrock_runtime.invoke_model = self._patched
        return self

    def __exit__(self, *exc):
        self.mod.bedrock_runtime.invoke_model = self.real

    def _patched(self, **kwargs):
        model_id = kwargs["modelId"]
        body = json.loads(kwargs["body"])
        new_api = any(m in model_id for m in NEW_API_MARKERS)
        if new_api:
            body.pop("temperature", None)
            body.pop("top_p", None)
            body.pop("top_k", None)
            body.setdefault("thinking", {"type": "disabled"})
        started = time.time()
        try:
            resp = self.real(modelId=model_id, body=json.dumps(body))
        except Exception as e:  # thinking 指定が通らないモデルへの保険
            if new_api and "thinking" in body and "ValidationException" in str(type(e).__name__) + str(e):
                body.pop("thinking", None)
                resp = self.real(modelId=model_id, body=json.dumps(body))
            else:
                raise
        raw = resp["body"].read()
        elapsed = time.time() - started
        parsed = json.loads(raw)
        usage = parsed.get("usage", {})
        self.last = {
            "modelId": model_id,
            "responseModel": parsed.get("model"),
            "latencySec": round(elapsed, 2),
            "inputTokens": usage.get("input_tokens"),
            "outputTokens": usage.get("output_tokens"),
            "thinkingTokens": (usage.get("output_tokens_details") or {}).get("thinking_tokens"),
            "stopReason": parsed.get("stop_reason"),
        }
        resp["body"] = io.BytesIO(raw)
        return resp


def run_question(mod, helpers, item: dict, models: list) -> dict:
    query = item["query"]
    filters = dict(item.get("filters") or {})
    _, filters = mod.normalize_mode_and_filters("normal", filters)
    row = {"id": item.get("id"), "query": query, "filters": filters, "note": item.get("note")}

    clarify, questions = mod.needs_clarify(query, filters, None)
    if clarify:
        row["gate"] = "clarify"
        row["clarifyQuestions"] = questions
        return row

    merged, priority_expanded, used_abbrev = helpers.run_normal_retrieve(mod, query, filters)
    kb_results = {"retrievalResults": merged}
    row["retrieveCount"] = len(merged)
    row["priorityExpanded"] = priority_expanded
    row["usedAbbrevExpansion"] = used_abbrev

    if mod.is_weak_retrieval(merged, mode="normal"):
        row["gate"] = "not_found"
        return row

    row["gate"] = "pages"
    selected = mod.select_retrieval_results(merged, mode="normal")
    row["pageCandidates"] = [
        {k: v for k, v in c.items() if k in ("documentName", "pageNumber", "relevance", "modelType", "category")}
        for c in mod.build_page_candidates(selected, max_items=5)
    ]

    row["answers"] = {}
    for label, model_id in models:
        mod.BEDROCK_MODEL_ID = model_id
        with InvokeRecorder(mod) as rec:
            try:
                text = mod.generate_response_with_claude(query, kb_results, None, "normal", search_query=query)
                stats = dict(rec.last or {})
            except Exception as e:  # noqa: BLE001 - 比較レポートに残す
                text = f"[生成エラー] {type(e).__name__}: {e}"
                stats = {"modelId": model_id, "error": str(e)}
        pin, pout = price_for(model_id)
        if pin is not None and stats.get("inputTokens") is not None:
            stats["estCostUsd"] = round(
                stats["inputTokens"] / 1e6 * pin + (stats.get("outputTokens") or 0) / 1e6 * pout, 5
            )
        row["answers"][label] = {"text": text, **stats}
    return row


def summarize(rows: list, models: list) -> dict:
    summary = {}
    for label, model_id in models:
        lat, tin, tout, cost, n = [], [], [], [], 0
        for r in rows:
            a = (r.get("answers") or {}).get(label)
            if not a or "error" in a:
                continue
            n += 1
            lat.append(a.get("latencySec") or 0)
            tin.append(a.get("inputTokens") or 0)
            tout.append(a.get("outputTokens") or 0)
            cost.append(a.get("estCostUsd") or 0)
        summary[label] = {
            "modelId": model_id,
            "answered": n,
            "avgLatencySec": round(sum(lat) / n, 2) if n else None,
            "maxLatencySec": max(lat) if lat else None,
            "avgInputTokens": round(sum(tin) / n) if n else None,
            "avgOutputTokens": round(sum(tout) / n) if n else None,
            "totalEstCostUsd": round(sum(cost), 4),
            "avgEstCostUsd": round(sum(cost) / n, 5) if n else None,
        }
    return summary


def render_markdown(rows: list, models: list, summary: dict, meta: dict) -> str:
    L = []
    L.append(f"# RAG 生成モデル 切替前比較（{meta['date']}）\n")
    L.append("同じ質問・同じ検索結果に対する回答を並べたもの。**検索（Retrieve）は共通**なので、差はすべて生成モデルによる。\n")
    L.append("| ラベル | モデル ID |\n|---|---|")
    for label, mid in models:
        L.append(f"| {label} | `{mid}` |")
    L.append(f"\nKB: `{meta['kbId']}` / 質問数: {len(rows)} / 生成対象（pages ゲート通過）: {sum(1 for r in rows if r.get('gate') == 'pages')}\n")

    L.append("## サマリ\n")
    L.append("| ラベル | 回答数 | 平均レイテンシ(秒) | 最大(秒) | 平均入力トークン | 平均出力トークン | 1問あたり概算コスト(USD) | 合計概算(USD) |")
    L.append("|---|---|---|---|---|---|---|---|")
    for label, _ in models:
        s = summary[label]
        L.append(f"| {label} | {s['answered']} | {s['avgLatencySec']} | {s['maxLatencySec']} | {s['avgInputTokens']} | {s['avgOutputTokens']} | {s['avgEstCostUsd']} | {s['totalEstCostUsd']} |")
    L.append("\n※ コストは Anthropic 公式単価 × 地域指定プレミアム（jp. は 1.1 倍）の概算。請求額は AWS 料金表が正。\n")

    L.append("## 目視比較の観点\n")
    L.append("- 参照資料に書かれていることだけを述べているか（作文していないか）")
    L.append("- 該当資料名・頁に触れているか、不明点を不明と言えているか")
    L.append("- 日本語として現場で読みやすいか（長すぎないか）")
    L.append("- 機種未指定のときに特定機種の事実として断定していないか\n")
    L.append("各問の末尾の「判定」欄に itai / mona が `haiku45` / `sonnet5` / `同等` などを書き込む。\n")

    L.append("## 質問別\n")
    for i, r in enumerate(rows, 1):
        L.append(f"### {i}. [{r.get('id')}] {r['query']}\n")
        if r.get("note"):
            L.append(f"- 出典・メモ: {r['note']}")
        L.append(f"- フィルタ: `{json.dumps(r.get('filters') or {}, ensure_ascii=False)}`")
        L.append(f"- ゲート: **{r.get('gate')}**（検索件数 {r.get('retrieveCount', '-')}）")
        if r.get("gate") == "clarify":
            L.append(f"- 聞き返し: {r.get('clarifyQuestions')}")
            L.append("- 生成なし（両モデル共通の挙動）\n")
            continue
        if r.get("gate") == "not_found":
            L.append("- 弱い検索 → not_found 定型文（生成なし、両モデル共通）\n")
            continue
        if r.get("pageCandidates"):
            L.append("- 候補頁（共通）:")
            for c in r["pageCandidates"]:
                L.append(f"  - {c.get('documentName')} p.{c.get('pageNumber')} (score {round(float(c.get('relevance') or 0), 3)})")
        for label, _ in models:
            a = r["answers"].get(label, {})
            L.append(f"\n#### {label}  —  {a.get('latencySec', '-')} 秒 / 入力 {a.get('inputTokens', '-')} / 出力 {a.get('outputTokens', '-')} / 概算 {a.get('estCostUsd', '-')} USD\n")
            L.append("```text")
            L.append(a.get("text", ""))
            L.append("```")
        L.append("\n**判定:** （記入）\n")
    return "\n".join(L)


def main():
    args = parse_args()
    helpers = load_eval_helpers()
    kb_id = helpers.resolve_kb_id(args)
    mod = helpers.load_rag_module(kb_id, args.region)
    models = parse_models(args.models)
    questions = load_questions(args.questions, args.limit)

    rows = []
    for i, item in enumerate(questions, 1):
        print(f"[{i}/{len(questions)}] {item.get('id')} {item['query'][:40]}", file=sys.stderr)
        rows.append(run_question(mod, helpers, item, models))

    summary = summarize(rows, models)
    stamp = datetime.now().strftime("%Y%m%d-%H%M")
    out_dir = REPO_ROOT / "eval-results"
    out_dir.mkdir(exist_ok=True)
    out_md = Path(args.out) if args.out else out_dir / f"model-bakeoff-{stamp}.md"
    out_json = out_md.with_suffix(".json")
    meta = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "kbId": kb_id}
    out_md.write_text(render_markdown(rows, models, summary, meta), encoding="utf-8")
    out_json.write_text(json.dumps({"meta": meta, "models": models, "summary": summary, "rows": rows},
                                   ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"markdown: {out_md}\njson: {out_json}")


if __name__ == "__main__":
    main()
