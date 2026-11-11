"""Vocabulary shared by the field report Lambda, the frontend and the queue generator.

SYNC: REACTIONS / REVIEW_STATES must equal FIELD_REPORT_REACTIONS / FIELD_REPORT_REVIEW_STATES in
frontend/src/lib/knowledge-senpai-field-report.mjs and scripts/knowledge/build_scope_review_queue.py;
MODEL_TYPES must equal the keys of MODEL_ALIASES in rag-function/knowhow_retrieval.py and the values
of KB_MODEL_TYPES in frontend/src/data/kb-model-types.generated.mjs, generated from
knowledge/registry/applicability-vocabulary.json (tests/unit/test_senpai_field_report_sync.py).
This Lambda has its own CodeUri, so it keeps a hand-written copy checked by that test.
"""

# この条件で当てはまった / 当てはまらなかった / 分からない
REACTIONS = ("matched", "not_matched", "unsure")
# 未確認 / 確認待ち / 反映済み / 保留・不採用 (this Lambda only creates "unconfirmed")
REVIEW_STATES = ("unconfirmed", "awaiting_review", "reflected", "held_or_rejected")
INITIAL_REVIEW_STATE = "unconfirmed"
MODEL_TYPES = ("AXIEZ", "AXIEZ-LINKs", "NEXCUBE", "メルシティ", "メルワイド", "エスカレーター")

FINDING_MAX_CHARS = 500
CONDITION_MAX_CHARS = 300
MAX_CARD_REACTIONS = 10
