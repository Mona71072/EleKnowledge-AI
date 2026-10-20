"""出典の番号付け（[T#] [L#] [K#]）、回答中の参照の照合、結果の sources 組み立て。純粋関数のみ。"""
import re
import unicodedata

MAX_TECH_REFS = 10
MAX_LAW_REFS = 6
TECH_TEXT_MAX_CHARS = 1500
LAW_TEXT_MAX_CHARS = 4000
KNOWHOW_BODY_MAX_CHARS = 4000
REF_PATTERN = re.compile(r'\[([TLK])([0-9]{1,3})\]')
# 括弧（半角・全角・隅付き）で囲まれた短い塊。中身がすべて参照（カンマ区切り可）のときだけ参照として扱う。
BRACKET_GROUP = re.compile(r'[\[［【]([^\[\]［］【】\n]{1,60})[\]］】]')
REF_TOKEN = re.compile(r'^([TLK])\s*([0-9]{1,3})$')
REF_SEPARATORS = re.compile(r'[,;\s]+')


def _by_score(evidence: list) -> list:
    return sorted(evidence, key=lambda item: item.get('score') or 0.0, reverse=True)


def _group(evidence: list, key_fn, limit: int) -> list:
    """スコア順に、同じ出典（キー）の断片を1つにまとめる。先頭 limit 件まで。"""
    groups = {}
    for item in _by_score(evidence):
        key = key_fn(item)
        if key not in groups and len(groups) >= limit:
            continue
        groups.setdefault(key, []).append(item)
    return list(groups.values())


def _joined_text(items: list, limit: int) -> str:
    seen = []
    for item in items:
        text = (item.get('text') or '').strip()
        if text and text not in seen:
            seen.append(text)
    return '\n'.join(seen)[:limit]


def _tech_source(index: int, items: list) -> dict:
    head = items[0]
    return {
        'ref': f'T{index}', 'docKey': head['docKey'], 'title': head.get('title') or head['documentName'],
        'documentName': head['documentName'], 'pageNumber': head.get('pageNumber'),
        'sourceUri': head['sourceUri'], 'score': head.get('score') or 0.0,
        'text': _joined_text(items, TECH_TEXT_MAX_CHARS),
    }


def _law_source(index: int, items: list) -> dict:
    head = items[0]
    return {
        'ref': f'L{index}', 'docKey': head['docKey'], 'lawTitle': head.get('lawTitle'),
        'lawNumber': head.get('lawNumber'), 'provision': head.get('provision'),
        'effectiveDate': head.get('effectiveDate'), 'sourceUrl': head['sourceUrl'],
        'score': head.get('score') or 0.0, 'text': _joined_text(items, LAW_TEXT_MAX_CHARS),
    }


def _knowhow_source(index: int, card: dict) -> dict:
    return {
        'ref': f'K{index}', 'knowledgeId': card['knowledgeId'], 'cardVersion': card['cardVersion'],
        'title': card['title'], 'status': card['status'], 'modelFit': card.get('modelFit') or 'unknown',
        'body': (card.get('body') or '')[:KNOWHOW_BODY_MAX_CHARS],
    }


def build_sources(tech_evidence: list, law_evidence: list, cards: list) -> dict:
    """検索結果に番号を振る。同じ資料・同じページの断片は1つの参照にまとめる。"""
    tech_groups = _group(tech_evidence, lambda e: (e['docKey'], e.get('pageNumber')), MAX_TECH_REFS)
    law_groups = _group(law_evidence, lambda e: e['docKey'], MAX_LAW_REFS)
    return {
        'tech': [_tech_source(i, items) for i, items in enumerate(tech_groups, start=1)],
        'law': [_law_source(i, items) for i, items in enumerate(law_groups, start=1)],
        'knowhow': [_knowhow_source(i, card) for i, card in enumerate(cards, start=1)],
    }


def valid_refs(sources: dict) -> set:
    return {source['ref'] for kind in ('tech', 'law', 'knowhow') for source in sources[kind]}


def _tokens(inner: str):
    """括弧の中身がすべて参照なら [(種別, 番号文字列)]、そうでなければ None。"""
    normalized = unicodedata.normalize('NFKC', inner).upper().replace('、', ',')
    parts = [part for part in REF_SEPARATORS.split(normalized) if part]
    if not parts:
        return None
    # 「T 1」のように空白で割れた場合を戻す（種別だけの塊と番号だけの塊を結合）
    merged, index = [], 0
    while index < len(parts):
        part = parts[index]
        if part in ('T', 'L', 'K') and index + 1 < len(parts):
            part, index = part + parts[index + 1], index + 1
        merged.append(part)
        index += 1
    tokens = []
    for part in merged:
        match = REF_TOKEN.match(part)
        if not match:
            return None
        tokens.append((match.group(1), match.group(2)))
    return tokens


def verify_refs(text: str, sources: dict) -> dict:
    """実在する参照だけを残す。実在しない参照は本文から外し、unverifiedRefs に記録する。

    `[T1, T2]`・全角・隅付き括弧は個別に検証し、`[T1][T2]` の標準形に直す。
    番号の先頭ゼロ（`T01`）は別物として未検証にする。
    """
    known = valid_refs(sources)
    unverified, cited = [], set()

    def replace(match):
        tokens = _tokens(match.group(1))
        if tokens is None:
            return match.group(0)
        kept = []
        for kind, number in tokens:
            ref = f'{kind}{number}'
            if ref in known:
                cited.add(ref)
                kept.append(f'[{ref}]')
            elif ref not in unverified:
                unverified.append(ref)
        return ''.join(kept)

    return {'text': BRACKET_GROUP.sub(replace, text or ''), 'unverifiedRefs': unverified, 'cited': cited}


MARKDOWN_IMAGE = re.compile(r'!\[[^\]]*\]\([^)]*\)')
MARKDOWN_LINK = re.compile(r'\[([^\]]*)\]\([^)]*\)')
AUTOLINK = re.compile(r'<(?:https?|ftp)://[^>\s]*>', re.IGNORECASE)
RAW_URL = re.compile(r'(?:(?:https?|ftp)://|www\.)[^\s)\]>"\u3000]+', re.IGNORECASE)
BARE_REF = re.compile(r'^[TLK][0-9]{1,3}$')


def _link_text(match) -> str:
    label = match.group(1).strip()
    # `[T1](url)` は参照として残し、URL だけを落とす。
    return f'[{label}]' if BARE_REF.match(label) else label


def strip_links(text: str) -> str:
    """回答からリンク・画像・生の URL を除く（出典は [T#] [L#] [K#] の参照でのみ示す）。

    取得した資料の中の命令文が、外部へ送信するリンクや画像をモデルに書かせても、画面に出ない。
    """
    cleaned = MARKDOWN_IMAGE.sub('', text or '')
    cleaned = MARKDOWN_LINK.sub(_link_text, cleaned)
    cleaned = AUTOLINK.sub('', cleaned)
    return RAW_URL.sub('', cleaned)


def _drop_none(mapping: dict) -> dict:
    return {key: value for key, value in mapping.items() if value is not None}


def public_sources(sources: dict, *, cited: set) -> dict:
    """結果の sources（契約どおり）。引用された技術・法令だけ。ノウハウは used / candidates に分ける。"""
    tech = [
        _drop_none({'ref': s['ref'], 'title': s['title'], 'documentName': s['documentName'],
                    'pageNumber': s['pageNumber'], 'sourceUri': s['sourceUri']})
        for s in sources['tech'] if s['ref'] in cited
    ]
    law = [
        _drop_none({'ref': s['ref'], 'lawTitle': s['lawTitle'], 'provision': s['provision'],
                    'effectiveDate': s['effectiveDate'], 'sourceUrl': s['sourceUrl']})
        for s in sources['law'] if s['ref'] in cited
    ]
    used = [
        {'ref': c['ref'], 'knowledgeId': c['knowledgeId'], 'cardVersion': c['cardVersion'],
         'title': c['title'], 'status': c['status'], 'modelFit': c['modelFit']}
        for c in sources['knowhow'] if c['ref'] in cited
    ]
    candidates = [
        {'knowledgeId': c['knowledgeId'], 'cardVersion': c['cardVersion'], 'title': c['title']}
        for c in sources['knowhow'] if c['ref'] not in cited
    ]
    return {'tech': tech, 'law': law, 'knowhow': {'used': used, 'candidates': candidates}}
