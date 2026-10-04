#!/usr/bin/env python3
"""
生成モデルの切替前比較（bake-off）

同じ質問・同じ検索結果（本番 Lambda と同一の retrieve 経路）に対して、
複数の Bedrock モデルで回答を生成し、目視比較用の Markdown と JSON を出力する。

- 検索は lambda/rag/rag-function/app.py を import して本番と同じ手順（run_retrieve_eval と同じ流儀）
- 生成は app.generate_response_with_claude を使い、モデル能力プロファイルに従って API を選ぶ
- 同じ検索結果を再利用できるよう、Retrieve 結果を JSON に保存・読込できる
- DynamoDB には書かず、Bedrock の Retrieve と InvokeModel / Converse を呼ぶ

使い方:
  python scripts/eval/run_model_bakeoff.py \
    --questions scripts/eval/bakeoff_questions.jsonl \
    --models "haiku45=jp.anthropic.claude-haiku-4-5-20251001-v1:0,sonnet5=global.anthropic.claude-sonnet-5" \
    --out eval-results/model-bakeoff.md

質問ファイル（jsonl）: {"id": "Q01", "query": "...", "filters": {"modelType": "AXIEZ", "category": []}, "note": "..."}
"""

import argparse
import importlib.util
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EVAL_SCRIPT = REPO_ROOT / "scripts" / "eval" / "run_retrieve_eval.py"

# 概算用の単価（USD / 1M tokens）。Sonnet 5 は Anthropic 公式単価の参考値。
PRICE_TABLE = [
    ("haiku-4-5", 1.0, 5.0),
    ("sonnet-4-6", 3.0, 15.0),
    ("sonnet-4-5", 3.0, 15.0),
    ("sonnet-5", 2.0, 10.0),
    ("opus-4-7", 5.0, 25.0),
    ("opus-4-8", 5.0, 25.0),
    ("opus-5", 5.0, 25.0),
]

# 生成リクエストの設定と API 選択は app.py のモデル能力プロファイルを共用する。
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
    p.add_argument("--save-retrieval", default=None, help="共通 Retrieve 結果の JSON 保存先")
    p.add_argument("--load-retrieval", default=None, help="保存済み Retrieve 結果を再利用")
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


def price_for(model_id: str, input_tokens=None):
    if "gpt-6-luna" in model_id:
        return (0.20, 0.75) if (input_tokens or 0) > 272000 else (0.10, 0.50)
    premium = 1.1 if model_id.startswith(("jp.", "apac.", "us.", "eu.")) else 1.0
    for marker, pin, pout in PRICE_TABLE:
        if marker in model_id:
            return pin * premium, pout * premium
    return None, None


def total_input_tokens(usage: dict) -> int | None:
    """通常入力・cache read・cache write を合算した入力 token 数。"""
    keys = ("inputTokens", "cacheReadInputTokens", "cacheWriteInputTokens")
    if not any(usage.get(key) is not None for key in keys):
        return None
    return sum(usage.get(key) or 0 for key in (
        "inputTokens", "cacheReadInputTokens", "cacheWriteInputTokens",
    ))


def cache_cost_status(model_id: str) -> str:
    if "sonnet-5" in model_id:
        return "未確認"
    if "gpt-6-luna" in model_id:
        return "AWS公式モデルカードの単価を適用"
    return "単価未設定"


def estimate_cost_usd(model_id: str, usage: dict) -> float | None:
    input_tokens = usage.get("inputTokens")
    output_tokens = usage.get("outputTokens")
    if input_tokens is None or output_tokens is None:
        return None

    cache_read = usage.get("cacheReadInputTokens") or 0
    cache_write = usage.get("cacheWriteInputTokens") or 0
    if "gpt-6-luna" in model_id:
        total_input = total_input_tokens(usage)
        if total_input > 272000:
            input_rate, cache_write_rate, cache_read_rate, output_rate = (0.20, 0.25, 0.02, 0.75)
        else:
            input_rate, cache_write_rate, cache_read_rate, output_rate = (0.10, 0.125, 0.01, 0.50)
        cost = (
            input_tokens * input_rate
            + cache_write * cache_write_rate
            + cache_read * cache_read_rate
            + output_tokens * output_rate
        ) / 1e6
        return cost

    input_rate, output_rate = price_for(model_id, input_tokens=input_tokens)
    if input_rate is None:
        return None
    # Bedrock の Sonnet 5 cache 単価は未確認のため、cache 分を含めない。
    return (input_tokens * input_rate + output_tokens * output_rate) / 1e6


def price_note(model_id: str) -> str:
    if "sonnet-5" in model_id:
        return ("Anthropic公式では input/output $2/$10、5分 cache write $2.50、"
                "1時間 cache write $4、cache read $0.20 / MTok。Bedrock の cache 単価は未確認のため、"
                "cache料金は金額に含めない（Bedrock 請求額とは未照合）。")
    if "gpt-6-luna" in model_id:
        return "Global: 入力 $0.10/$0.50、cache write/read $0.125/$0.01 per 1M tokens。272K超は入力/出力 $0.20/$0.75、cache write/read $0.25/$0.02。"
    return "Anthropic 公式単価の概算。請求額は AWS 料金表が正"


def save_retrieval(path, rows):
    """生成回答を除いた共通 Retrieve 結果を JSON 保存する。"""
    retrieval_rows = [{key: value for key, value in row.items() if key != "answers"}
                      for row in rows]
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(retrieval_rows, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )


def load_retrieval(path):
    """Retrieve キャッシュを質問 ID キーの辞書で読み込む。"""
    rows = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError("Retrieve キャッシュは JSON 配列である必要があります")
    return {str(row.get("id")): row for row in rows if isinstance(row, dict)}


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


class GenerationRecorder:
    """共通呼び出し関数を包み、API 共通で応答 usage とレイテンシを計測する。"""

    def __init__(self, mod):
        self.mod = mod
        self.real = mod.invoke_generation
        self.last = None

    def __enter__(self):
        self.mod.invoke_generation = self._patched
        return self

    def __exit__(self, *exc):
        self.mod.invoke_generation = self.real

    def _patched(self, client, model_id, *args, **kwargs):
        started = time.time()
        text, usage, stop_reason = self.real(client, model_id, *args, **kwargs)
        elapsed = time.time() - started
        self.last = {
            "modelId": model_id,
            "latencySec": round(elapsed, 2),
            "inputTokens": usage.get("inputTokens"),
            "outputTokens": usage.get("outputTokens"),
            "cacheReadInputTokens": usage.get("cacheReadInputTokens"),
            "cacheWriteInputTokens": usage.get("cacheWriteInputTokens"),
            "stopReason": stop_reason,
        }
        return text, usage, stop_reason


def run_question(mod, helpers, item: dict, models: list, retrieval_cache=None) -> dict:
    query = item["query"]
    filters = dict(item.get("filters") or {})
    _, filters = mod.normalize_mode_and_filters("normal", filters)
    row = {"id": item.get("id"), "query": query, "filters": filters, "note": item.get("note")}

    clarify, questions = mod.needs_clarify(query, filters, None)
    if clarify:
        row["gate"] = "clarify"
        row["clarifyQuestions"] = questions
        return row

    cached = (retrieval_cache or {}).get(str(item.get("id")))
    if retrieval_cache is not None and cached is None:
        raise ValueError("Retrieve キャッシュに質問 ID がありません")
    if cached:
        if cached.get("query") != query or cached.get("filters") != filters:
            raise ValueError("Retrieve キャッシュの質問またはフィルタが一致しません")
        if cached.get("gate") != "pages":
            return dict(cached)
        row.update({key: value for key, value in cached.items() if key != "answers"})
        merged = cached.get("retrievalResults") or []
        priority_expanded = cached.get("priorityExpanded", False)
        used_abbrev = cached.get("usedAbbrevExpansion", False)
    else:
        merged, priority_expanded, used_abbrev = helpers.run_normal_retrieve(mod, query, filters)
    kb_results = {"retrievalResults": merged}
    row["retrieveCount"] = len(merged)
    row["priorityExpanded"] = priority_expanded
    row["usedAbbrevExpansion"] = used_abbrev

    if mod.is_weak_retrieval(merged, mode="normal"):
        row["gate"] = "not_found"
        return row

    row["gate"] = "pages"
    row["retrievalResults"] = merged
    selected = mod.select_retrieval_results(merged, mode="normal")
    row["pageCandidates"] = [
        {k: v for k, v in c.items() if k in ("documentName", "pageNumber", "relevance", "modelType", "category")}
        for c in mod.build_page_candidates(selected, max_items=5)
    ]

    row["answers"] = {}
    for label, model_id in models:
        mod.BEDROCK_MODEL_ID = model_id
        with GenerationRecorder(mod) as rec:
            try:
                text = mod.generate_response_with_claude(query, kb_results, None, "normal", search_query=query)
                stats = dict(rec.last or {})
            except Exception as e:  # noqa: BLE001 - 比較レポートに残す
                text = f"[生成エラー] {type(e).__name__}: {e}"
                stats = {"modelId": model_id, "error": str(e)}
        est_cost = estimate_cost_usd(model_id, stats)
        stats["totalInputTokens"] = total_input_tokens(stats)
        for key in (
            "inputTokens", "cacheReadInputTokens", "cacheWriteInputTokens", "outputTokens",
        ):
            stats.setdefault(key, None)
        stats["cacheCostStatus"] = cache_cost_status(model_id)
        if est_cost is not None:
            stats["estCostUsd"] = est_cost
        row["answers"][label] = {"text": text, **stats}
    return row


def summarize(rows: list, models: list) -> dict:
    summary = {}
    for label, model_id in models:
        lat, input_tokens, cache_read, cache_write, total_input, tout, cost, n = (
            [], [], [], [], [], [], [], 0
        )
        usage_count = 0
        for r in rows:
            a = (r.get("answers") or {}).get(label)
            if not a or "error" in a:
                continue
            n += 1
            lat.append(a.get("latencySec") or 0)
            answer_total_input = a.get("totalInputTokens")
            if answer_total_input is None and "totalInputTokens" not in a:
                answer_total_input = total_input_tokens(a)
            if answer_total_input is not None:
                usage_count += 1
                input_tokens.append(a.get("inputTokens"))
                cache_read.append(a.get("cacheReadInputTokens"))
                cache_write.append(a.get("cacheWriteInputTokens"))
                total_input.append(answer_total_input)
                tout.append(a.get("outputTokens"))
            if answer_total_input is not None and a.get("estCostUsd") is not None:
                cost.append(a["estCostUsd"])

        def average(values):
            available = [value for value in values if value is not None]
            return sum(available) / len(available) if available else None

        summary[label] = {
            "modelId": model_id,
            "answered": n,
            "usageCount": usage_count,
            "avgLatencySec": round(sum(lat) / n, 2) if n else None,
            "maxLatencySec": max(lat) if lat else None,
            "avgInputTokens": average(input_tokens),
            "avgCacheReadInputTokens": average(cache_read),
            "avgCacheWriteInputTokens": average(cache_write),
            "avgTotalInputTokens": average(total_input),
            "avgOutputTokens": average(tout),
            "totalEstCostUsd": sum(cost),
            "avgEstCostUsd": sum(cost) / len(cost) if cost else None,
            "cacheCostStatus": cache_cost_status(model_id),
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
    L.append("| ラベル | 回答数 | usage対象 | 平均レイテンシ(秒) | 最大(秒) | 平均通常入力 | 平均 cache read | 平均 cache write | 平均総入力 | 平均出力 | 1問あたり参考概算(USD) | 合計参考概算(USD) |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for label, _ in models:
        s = summary[label]
        avg_tokens = lambda key: "-" if s[key] is None else str(round(s[key]))
        avg_cost = "-" if s["avgEstCostUsd"] is None else f"{s['avgEstCostUsd']:.8f}"
        L.append(f"| {label} | {s['answered']} | {s['usageCount']}/{len(rows)} | {s['avgLatencySec']} | {s['maxLatencySec']} | {avg_tokens('avgInputTokens')} | {avg_tokens('avgCacheReadInputTokens')} | {avg_tokens('avgCacheWriteInputTokens')} | {avg_tokens('avgTotalInputTokens')} | {avg_tokens('avgOutputTokens')} | {avg_cost} | {s['totalEstCostUsd']:.8f} |")
    L.append("\n※ 金額は参考概算（実請求とは未照合）。単価の根拠・注記:")
    for label, model_id in models:
        L.append(f"- {label}: {price_note(model_id)}")
    L.append("総入力トークンは通常入力 + cache read + cache write。料金は表示時に丸め、集計は丸め前の値で計算。請求額は AWS 料金表が正です。\n")

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
            tokens = [a.get(key) for key in (
                "inputTokens", "cacheReadInputTokens", "cacheWriteInputTokens",
            )]
            total_input = a.get("totalInputTokens")
            if total_input is None and "totalInputTokens" not in a:
                total_input = total_input_tokens(a)
            token_text = lambda value: "-" if value is None else str(value)
            cost = a.get("estCostUsd")
            cost_text = "未算出" if cost is None else f"{cost:.8f} USD"
            cache_note = ""
            if a.get("cacheCostStatus") == "未確認":
                cache_note = "（cache料金未確認・金額に含めず）"
            L.append(f"\n#### {label} — {a.get('latencySec', '-')} 秒 / 通常入力 {token_text(tokens[0])} / cache read {token_text(tokens[1])} / cache write {token_text(tokens[2])} / 総入力 {token_text(total_input)} / 出力 {token_text(a.get('outputTokens'))} / 停止理由 {a.get('stopReason', '-')} / 参考概算 {cost_text}{cache_note}\n")
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
    retrieval_cache = load_retrieval(args.load_retrieval) if args.load_retrieval else None

    rows = []
    for i, item in enumerate(questions, 1):
        print(f"[{i}/{len(questions)}] {item.get('id')} {item['query'][:40]}", file=sys.stderr)
        rows.append(run_question(mod, helpers, item, models, retrieval_cache=retrieval_cache))

    if args.save_retrieval:
        save_retrieval(args.save_retrieval, rows)

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
