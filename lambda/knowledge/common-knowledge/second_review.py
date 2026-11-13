"""§4.3 の例外（必ず 2 人目の確認が要る変更）の印を、作業版を保存するときに付ける。

ノウハウ管理の見直し WP2（設計 docs/design-2026-11-11-knowledge-governance.md §4.2・§4.3）。
印は作成者の申告と、次のコードの規則で付ける。判定に迷うものは例外として扱う（キーワードは広めに取る）。

- safety_legal       本文・適用範囲に、安全・法令・作業可否に関わる語がある
- nonstandard        本文・適用範囲に、標準手順・正式資料と異なることを示す語がある
- scope_expansion    訂正で、承認済みの前版から適用範囲（applicability）が変わった。広げたか狭めたかは
                     自由記述からは決められないため、変わったら付ける
- audience_expansion 訂正で、承認済みの前版から読者（audience）が変わった

印は台帳（作業版の記録）にだけ持ち、承認束の hash（i1-json-lf-v1）には入れない。
既存の版の hash と照合を変えないため。印の無い古い版は、例外として扱う（service.decide）。
"""
import unicodedata

REASONS = ('safety_legal', 'nonstandard', 'scope_expansion', 'audience_expansion')
# 安全・法令・作業可否。誤って付いても 2 人目の確認が要るだけなので、取りこぼしを避けて広めにする。
SAFETY_LEGAL_TERMS = (
    '安全', '危険', '感電', '墜落', '転落', '落下', '挟まれ', '巻き込まれ', '負傷', '事故',
    '法令', '建築基準法', '労働安全衛生', '告示', '届出', '確認申請', '定期検査', '検査済',
    '資格', '作業可否', '作業禁止', '禁止', 'してはならない', 'しないこと', '活線', '停電作業',
    'ロックアウト', '立入禁止', '保護具', '安全帯', 'ハーネス',
)
NONSTANDARD_TERMS = (
    '標準と異なる', '標準手順と異なる', '正式資料と異なる', '資料と異なる', 'マニュアルと異なる',
    '手順書と異なる', '標準外', '規定外', '独自の手順', '独自手順', '現場判断',
)
MAX_TERMS = 10


def _normalize(value):
    return unicodedata.normalize('NFKC', value or '')


def _matches(text, terms):
    found = [term for term in terms if _normalize(term) in text]
    return found[:MAX_TERMS]


def assess(markdown, fields, declared, previous=None):
    """作業版 1 つの例外の印を返す。previous は訂正の元になった承認済みの前版（新規は None）。"""
    text = _normalize(markdown) + '\n' + _normalize(fields.get('applicability'))
    detected, terms = [], []
    safety = _matches(text, SAFETY_LEGAL_TERMS)
    if safety:
        detected.append('safety_legal')
        terms += safety
    nonstandard = _matches(text, NONSTANDARD_TERMS)
    if nonstandard:
        detected.append('nonstandard')
        terms += nonstandard
    if previous is not None:
        if _normalize(previous.get('applicability')).strip() != _normalize(fields.get('applicability')).strip():
            detected.append('scope_expansion')
        if previous.get('audience') != fields.get('audience'):
            detected.append('audience_expansion')
    declared = sorted(set(declared))
    return {
        'required': bool(declared or detected),
        'declared': declared,
        'detected': detected,
        'terms': terms[:MAX_TERMS],
    }


def legacy():
    """印が付く前（WP2 より前）に保存された版。迷ったら例外として扱う。"""
    return {'required': True, 'declared': [], 'detected': ['unmarked'], 'terms': []}
