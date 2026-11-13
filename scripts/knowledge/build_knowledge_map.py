"""知識マップ（生成物）を、カードと項目台帳から作る。段階 1: 関係の種類 C1（適用）・C2（根拠）・R1（構成・対応）。

設計: docs/design-2026-11-12-knowledge-map.md §4.5・§4.8・§5 段階 1。読み取りのみ（AWS へ書かない）。

  python scripts/knowledge/build_knowledge_map.py                      # Git のカード（凍結版）から作り、要約を表示
  python scripts/knowledge/build_knowledge_map.py --cards DIR --out F  # 公開版の写し（snapshot_published_cards.py の DIR/cards）から作る

人は生成物を編集しない。直すときはカードか項目台帳（knowledge/registry/applicability-vocabulary.json）を直して作り直す。
次のどれかがあれば失敗する（§4.5 ルール 3）: 存在しない項目 ID への関係、出典の無い項目同士の関係、カード ID の重複。
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import re
import sys

import yaml

ROOT = Path(__file__).resolve().parents[2]
VOCAB = ROOT / 'knowledge/registry/applicability-vocabulary.json'
KB_REF_RESOLUTION = ROOT / 'knowledge/registry/kb-ref-resolution.jsonl'
SCOPE_AXES = ('product_lines', 'machine_room', 'control_methods', 'model_abbreviations',
              'guide_systems', 'door_families', 'door_types')
QUALIFIED = {'observed_on': 'observed', 'may_apply_to': 'may_apply', 'excludes': 'excludes'}
FRONTMATTER = re.compile(r'---\r?\n(.*?)\r?\n---', re.DOTALL)


class KnowledgeMapError(Exception):
    pass


def _items(vocab):
    return [e for entries in vocab['axes'].values() for e in entries] + [
        e for entries in vocab['items'].values() for e in entries]


def _terms(entry):
    ui = entry.get('ui_filter') or {}
    return [entry['value'], *entry.get('admitted', []), *entry.get('deprecated', []),
            *ui.get('kb_model_types', []), *ui.get('extra_card_aliases', [])]


def read_cards(cards_dir):
    """frontmatter に knowledge_id を持つ Markdown だけを読む（README・TEMPLATE などは除く）。"""
    cards = {}
    for path in sorted(Path(cards_dir).rglob('*.md')):
        match = FRONTMATTER.match(path.read_text(encoding='utf-8'))
        meta = yaml.safe_load(match.group(1)) if match else None
        if not isinstance(meta, dict) or 'knowledge_id' not in meta:
            continue
        identifier = meta['knowledge_id']
        if identifier in cards:
            raise KnowledgeMapError(f'カード ID が重複: {identifier}')
        cards[identifier] = meta
    return cards


def build(cards, vocab, kb_resolution):
    """カード（knowledge_id → frontmatter）と項目台帳から、点・線・未解決の一覧を作る。"""
    items = _items(vocab)
    ids = {e['id'] for e in items}
    by_axis = {axis: {t: e['id'] for e in entries for t in _terms(e)} for axis, entries in vocab['axes'].items()}
    any_axis = {t: i for axis in SCOPE_AXES for t, i in by_axis[axis].items()}
    misplaced = {(m['axis'], m['value']) for m in vocab['misplaced']}
    resolved_kb = {(r['knowledge_id'], r['document_number']): r.get('kb_filename')
                   for r in kb_resolution if r.get('kb_filename')}

    nodes = [{'id': e['id'], 'kind': e['id'].split(':', 1)[0], 'label': e['value']} for e in items]
    edges, unresolved = [], collections.Counter()

    for entry in items:
        for relation in entry.get('relations', []):
            if relation['target'] not in ids:
                raise KnowledgeMapError(f"{entry['id']} → 存在しない ID {relation['target']}")
            if not relation.get('source'):
                raise KnowledgeMapError(f"{entry['id']} → {relation['target']} に出典が無い")
            edges.append({'type': 'R1' if relation['type'] == 'related' else 'R2', 'from': entry['id'],
                          'to': relation['target'], 'origin': {'registry_schema': vocab['schema_version']},
                          'source': relation['source']})

    for identifier, meta in sorted(cards.items()):
        card = f'card:{identifier}'
        origin = {'knowledge_id': identifier, 'card_version': meta.get('card_version')}
        nodes.append({'id': card, 'kind': 'card', 'label': meta.get('title', ''), 'card_kind': meta.get('kind')})
        scope = meta.get('model_scope') or {}
        targets = set()
        for axis in SCOPE_AXES:
            for value in scope.get(axis) or []:
                target = by_axis[axis].get(str(value))
                if target:
                    targets.add((target, None))
                elif (axis, str(value)) not in misplaced:
                    raise KnowledgeMapError(f'{identifier}: {axis}={value} が項目台帳に無い')
        for key, qualifier in QUALIFIED.items():
            for value in scope.get(key) or []:
                target = any_axis.get(str(value))
                if target:
                    targets.add((target, qualifier))
                else:
                    unresolved[f'C1.{key}'] += 1  # 自由記述の要約。項目に当たらない値は数えるだけ
        for target, qualifier in sorted(targets, key=lambda t: (t[0], t[1] or '')):
            edge = {'type': 'C1', 'from': card, 'to': target, 'origin': origin}
            if qualifier:
                edge['qualifier'] = qualifier
            edges.append(edge)

        for ref in meta.get('source_refs') or []:
            kind = ref.get('ref_type')
            if kind == 'law_rag':
                target = 'law:' + str(ref.get('law_id', '')).split('_')[0]
                if target not in ids:
                    raise KnowledgeMapError(f"{identifier}: 法令の項目に無い law_id {ref.get('law_id')}")
                edges.append({'type': 'C2', 'from': card, 'to': target, 'origin': origin,
                              'law_folder': ref.get('law_id')})
            elif kind == 'kb_document':
                filename = resolved_kb.get((identifier, ref.get('document_number'))) or ref.get('kb_filename')
                if filename:
                    edges.append({'type': 'C2', 'from': card, 'to': f'kb:{filename}', 'origin': origin})
                else:
                    unresolved['C2.kb_document'] += 1
            elif kind == 'lists_item':
                edges.append({'type': 'C2', 'from': card, 'to': f"lists:{ref.get('list_item_id')}", 'origin': origin})
            elif kind == 'onenote_page':
                edges.append({'type': 'C2', 'from': card, 'to': f"onenote:{ref.get('onenote_id')}", 'origin': origin})
            elif kind == 'knowhow':
                edges.append({'type': 'C2', 'from': card, 'to': f"knowhow:{ref.get('knowhow_id')}", 'origin': origin})
            # draft_record は原情報ではない（CONTRACT.md）ため線にしない

    edges.sort(key=lambda e: (e['type'], e['from'], e['to'], e.get('qualifier', '')))
    nodes.sort(key=lambda n: n['id'])
    body = {'nodes': nodes, 'edges': edges}
    digest = hashlib.sha256(json.dumps(body, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()
    return {
        'generated': '生成物。直接編集しない。元: カードと knowledge/registry/applicability-vocabulary.json。'
                     '再生成: python scripts/knowledge/build_knowledge_map.py',
        'registry_schema': vocab['schema_version'],
        'sha256': digest,
        'counts': {'cards': len(cards), 'items': len(items),
                   'edges': dict(sorted(collections.Counter(e['type'] for e in edges).items()))},
        'unresolved': dict(sorted(unresolved.items())),
        **body,
    }


def orphans(knowledge_map):
    """関係を 1 本も持たないカードと項目（見直しの列の材料。§6）。"""
    linked = {e['from'] for e in knowledge_map['edges']} | {e['to'] for e in knowledge_map['edges']}
    return collections.Counter(n['kind'] for n in knowledge_map['nodes'] if n['id'] not in linked)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--cards', default=str(ROOT / 'knowledge/cards'))
    parser.add_argument('--out')
    args = parser.parse_args(argv)
    vocab = json.loads(VOCAB.read_text(encoding='utf-8'))
    resolution = [json.loads(line) for line in KB_REF_RESOLUTION.read_text(encoding='utf-8').splitlines() if line.strip()]
    try:
        knowledge_map = build(read_cards(args.cards), vocab, resolution)
    except KnowledgeMapError as error:
        print(f'失敗: {error}', file=sys.stderr)
        return 1
    if args.out:
        Path(args.out).write_text(json.dumps(knowledge_map, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    summary = {key: knowledge_map[key] for key in ('sha256', 'counts', 'unresolved')}
    summary['orphans'] = dict(sorted(orphans(knowledge_map).items()))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
