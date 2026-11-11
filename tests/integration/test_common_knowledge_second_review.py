"""ノウハウ管理の見直し WP2: 自己承認の禁止を §4.3 の例外だけに絞り、自己承認した版を抜き取り確認する。

設計: docs/design-2026-11-11-knowledge-governance.md §4.2・§4.3（確信度・資格は今回の範囲外）。
合成データだけを使う。I1 の合成受入（公開・停止・再開・競合）は test_common_knowledge_i1.py が引き続き確かめる。
"""
import pytest

from test_common_knowledge_i1 import (  # noqa: F401  (env is a fixture)
    SAFETY_MARKDOWN, approved, call, draft, env, restart, saved,
)


def own_review(service, card, version, revision=1, suffix='own'):
    """編集担当に承認権限を足し、自分の版の確認依頼を出す（当面 itai・mona が全資格を持つ想定）。"""
    service.policy['actors']['synthetic-editor']['permissions'].append('approve')
    status, review = call(service, 'editor', 'POST', 'cards/' + card + '/review-requests',
                          {'bundleHash': version['bundleHash'], 'reason': '確認依頼'}, revision, 'review-' + suffix)
    assert status == 200, review
    return {'reviewRequestId': review['reviewRequestId'], 'bundleHash': version['bundleHash'],
            'decision': 'approve', 'reason': '本人が特定版を確認'}


def test_normal_version_can_be_self_approved_and_waits_for_a_sample_check(env):
    service, now = env
    _, card, version = saved(service, now[0])
    assert version['secondReview'] == {'required': False, 'declared': [], 'detected': [], 'terms': []}
    status, result = call(service, 'editor', 'POST', 'cards/' + card + '/decisions',
                          own_review(service, card, version), 1, 'self')
    assert status == 200, result
    assert result['selfApproved'] is True and result['sampleCheck'] == 'pending'
    approval = service.canonical.read_approved(result['approvedKey'])
    assert approval is not None
    # Publication is unchanged: the approved version can be published while the sample check is pending.
    assert call(service, 'publisher', 'POST', 'cards/' + card + '/publish',
                {'revision': 1, 'approvalId': result['approvalId'], 'reason': '公開'}, 0, 'publish')[0] == 200

    check = {'approvalId': result['approvalId'], 'result': 'confirmed', 'reason': '抜き取りで内容を確認'}
    status, denied = call(service, 'editor', 'POST', 'cards/' + card + '/sample-checks', check, 1, 'own-check')
    assert (status, denied['code']) == (403, 'SelfCheckDenied')
    status, recorded = call(service, 'reviewer', 'POST', 'cards/' + card + '/sample-checks', check, 1, 'check')
    assert status == 200, recorded
    assert recorded['status'] == 'confirmed' and recorded['actor'] == 'synthetic-reviewer'
    # Idempotent retry returns the same record; a second check with another key is refused.
    assert call(service, 'reviewer', 'POST', 'cards/' + card + '/sample-checks', check, 1, 'check')[1] == recorded
    status, again = call(service, 'reviewer', 'POST', 'cards/' + card + '/sample-checks', check, 1, 'again')
    assert (status, again['code']) == (409, 'SampleCheckNotPending')
    stored = call(restart(service, now), 'editor', 'GET', 'cards/' + card)[1]['versions']['1']
    assert stored['sampleCheck'] == {k: recorded[k] for k in ('status', 'checkId', 'actor', 'reason', 'at')}
    assert stored['approvedBy'] == 'synthetic-editor' and stored['selfApproved'] is True


def test_sample_check_records_needs_fix_without_withdrawing(env):
    service, now = env
    _, card, version = saved(service, now[0])
    result = call(service, 'editor', 'POST', 'cards/' + card + '/decisions',
                  own_review(service, card, version), 1, 'self')[1]
    assert call(service, 'publisher', 'POST', 'cards/' + card + '/publish',
                {'revision': 1, 'approvalId': result['approvalId'], 'reason': '公開'}, 0, 'publish')[0] == 200
    status, recorded = call(service, 'reviewer', 'POST', 'cards/' + card + '/sample-checks',
                            {'approvalId': result['approvalId'], 'result': 'needs_fix', 'reason': '適用範囲の記述を直す'},
                            1, 'check')
    assert status == 200 and recorded['status'] == 'needs_fix'
    assert call(service, 'reader', 'GET', 'published/' + card)[0] == 200


def test_version_approved_by_another_person_has_no_sample_check(env):
    service, now = env
    _, card, result = approved(service, now[0])
    assert result['selfApproved'] is False and result['sampleCheck'] is None
    status, refused = call(service, 'publisher', 'POST', 'cards/' + card + '/sample-checks',
                           {'approvalId': result['approvalId'], 'result': 'confirmed', 'reason': '確認'}, 1, 'check')
    assert status == 403  # the sample check needs the approve grant
    service.policy['actors']['synthetic-viewer']['permissions'].append('approve')
    status, refused = call(service, 'viewer', 'POST', 'cards/' + card + '/sample-checks',
                           {'approvalId': result['approvalId'], 'result': 'confirmed', 'reason': '確認'}, 1, 'check')
    assert (status, refused['code']) == (409, 'SampleCheckNotPending')


@pytest.mark.parametrize('overrides, reasons', [
    ({'secondReview': ['nonstandard']}, ([], ['nonstandard'])),
    ({'markdown': SAFETY_MARKDOWN}, (['safety_legal'], [])),
    ({'markdown': '# 合成\n\n正式資料と異なる手順で締め付ける。\n'}, (['nonstandard'], [])),
    ({'applicability': '架空機種A。法令上の届出が要る作業。'}, (['safety_legal'], [])),
])
def test_exception_marks_from_declaration_and_rules_deny_self_approval(env, overrides, reasons):
    service, now = env
    _, card, version = saved(service, now[0], **overrides)
    detected, declared = reasons
    assert version['secondReview']['required'] is True
    assert version['secondReview']['detected'] == detected
    assert version['secondReview']['declared'] == declared
    status, denied = call(service, 'editor', 'POST', 'cards/' + card + '/decisions',
                          own_review(service, card, version), 1, 'self')
    assert (status, denied['code']) == (403, 'SelfApprovalDenied')
    status, result = call(service, 'reviewer', 'POST', 'cards/' + card + '/decisions',
                          _decision(service, card), 1, 'other')
    assert status == 200 and result['selfApproved'] is False and result['sampleCheck'] is None


def _decision(service, card):
    review = call(service, 'editor', 'GET', 'cards/' + card)[1]['review']
    return {'reviewRequestId': review['reviewRequestId'], 'bundleHash': review['bundleHash'],
            'decision': 'approve', 'reason': '別の確認者が特定版を確認'}


def test_declaration_is_a_ledger_mark_outside_the_bundle_hash(env):
    """The mark is not hashed, so bundles saved before WP2 keep verifying and publishing unchanged."""
    from service import BUNDLE_KEYS
    service, now = env
    identifier, card, _ = saved(service, now[0])
    marked = call(service, 'editor', 'PUT', 'cards/' + card + '/draft',
                  {**draft(identifier, now[0], 3), 'secondReview': ['scope_expansion']}, 1, 'marked')[1]
    assert marked['secondReview']['declared'] == ['scope_expansion']
    assert 'secondReview' not in BUNDLE_KEYS
    stored = call(service, 'editor', 'GET', 'cards/' + card)[1]['versions']['2']
    assert stored['bundleHash'] == marked['bundleHash']
    service.verify_bundle(stored)


@pytest.mark.parametrize('declared', [['unknown'], ['safety_legal', 'safety_legal'], 'safety_legal', [1]])
def test_invalid_declarations_are_rejected(env, declared):
    service, now = env
    identifier, card, _ = saved(service, now[0])
    status, _ = call(service, 'editor', 'PUT', 'cards/' + card + '/draft',
                     {**draft(identifier, now[0], 3), 'secondReview': declared}, 1, 'bad')
    assert status == 400


def test_correction_that_changes_applicability_is_marked(env):
    service, now = env
    _, card, version = saved(service, now[0], kind='correction',
                             applicability='架空機種A・改訂1と改訂2。他の機種には適用しない。')
    assert version['secondReview']['detected'] == ['scope_expansion']


def test_correction_with_the_same_applicability_is_not_marked(env):
    service, now = env
    _, _, version = saved(service, now[0], kind='correction')
    assert version['secondReview']['required'] is False


def test_versions_saved_before_the_mark_are_treated_as_exceptions(env):
    service, now = env
    _, card, version = saved(service, now[0])
    with service.store.unit() as db:
        stored = db.get('card', card)
        del stored['versions']['1']['secondReview']
        db.put('card', card, stored)
    status, denied = call(service, 'editor', 'POST', 'cards/' + card + '/decisions',
                          own_review(service, card, version), 1, 'self')
    assert (status, denied['code']) == (403, 'SelfApprovalDenied')


def test_submitter_self_approval_follows_the_same_rule(env):
    service, now = env
    identifier, card, version = saved(service, now[0])
    service.policy['actors']['synthetic-contributor']['permissions'] += ['view', 'approve']
    decision = own_review(service, card, version)
    result = service.decide({'sub': 'synthetic-contributor'}, 'own-submission', card, 1, decision)
    assert result['selfApproved'] is True and result['sampleCheck'] == 'pending'
