"""生成物。直接編集しない。元: knowledge/registry/applicability-vocabulary.json。
再生成: python scripts/knowledge/generate_vocabulary.py

rag-function と同じ CodeUri で配る。値の意味は APPLICABILITY-TAXONOMY.md を参照。
"""

# 画面の機種キー → 共有 KB の model_type（要素完全一致で listContains に展開する）。
UI_MODEL_FILTERS = {
    "AXIEZ": ("AXIEZ", "AXIEZ(KE-WF・KE-HF)", "駅舎エレ"),
    "AXIEZ-LINKs": ("AXIEZ-LINKs",),
    "NEXCUBE": ("NEXCUBE", "NEXCUBE Limited", "特注機械室レスエレベーター"),
    "メルシティ": ("メルシティ",),
    "メルワイド": ("メルワイド",),
    "エスカレーター": ("エスカレーター",),
}

# 機種キー → カードの model_scope に書かれた値の別名（NFKC・小文字化済み）。
MODEL_ALIASES = {
    "AXIEZ": frozenset({"axiez", "axiez(ke-wf・ke-hf)", "駅舎エレ"}),
    "AXIEZ-LINKs": frozenset({"axiez-links"}),
    "NEXCUBE": frozenset({"nexcube", "nexcube limited", "特注機械室レスエレベーター"}),
    "メルシティ": frozenset({"メルシティ"}),
    "メルワイド": frozenset({"メルワイド"}),
    "エスカレーター": frozenset({"エスカレーター", "escalator"}),
}

# 機種キー → 質問中の呼び名（調査ジョブが質問から機種を判定するときに使う）。
QUESTION_MODEL_ALIASES = {
    "AXIEZ": ("axiez", "アクシーズ"),
    "AXIEZ-LINKs": ("links", "リンクス"),
    "NEXCUBE": ("nexcube", "ネクスキューブ"),
    "メルシティ": ("メルシティ", "melcity"),
    "メルワイド": ("メルワイド", "melwide"),
    "エスカレーター": ("エスカレーター", "escalator", "エスカ"),
}

GENERIC_ELEVATOR_LABEL = "全エレ機種"
GENERIC_ESCALATOR_LABEL = "全エス機種"
