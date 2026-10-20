"""出典の番号付け（[T#] [L#] [K#]）、回答中の参照の照合、結果の sources 組み立て。純粋関数のみ。"""
import re

MAX_TECH_REFS = 10
MAX_LAW_REFS = 6
TECH_TEXT_MAX_CHARS = 1500
LAW_TEXT_MAX_CHARS = 4000
KNOWHOW_BODY_MAX_CHARS = 4000
REF_PATTERN = re.compile(r'\[([TLK])([0-9]{1,3})\]')


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


def verify_refs(text: str, sources: dict) -> dict:
    """実在する参照だけを残す。実在しない参照は本文から外し、unverifiedRefs に記録する。"""
    known = valid_refs(sources)
    unverified, cited = [], set()

    def replace(match):
        ref = f'{match.group(1)}{match.group(2)}'
        if ref in known:
            cited.add(ref)
            return match.group(0)
        if ref not in unverified:
            unverified.append(ref)
        return ''

    return {'text': REF_PATTERN.sub(replace, text or ''), 'unverifiedRefs': unverified, 'cited': cited}


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
