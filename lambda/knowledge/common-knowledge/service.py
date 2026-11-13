"""Common candidate, exact-version review, publication and guarded read service."""
import copy
import json
import re
import time
import uuid

import second_review
from storage import digest


ID = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$')
POSITION = re.compile(r'^[0-9]{12}#[A-Za-z0-9][A-Za-z0-9_-]{0,79}$')
STATES = {'unconfirmed', 'in_review', 'awaiting_review', 'reflected', 'held', 'rejected'}
KINDS = {'case_summary', 'practice_guide', 'term_foundation'}
BUNDLE_KEYS = ('candidateId', 'candidateRevision', 'kind', 'applicability', 'sourceRefs',
               'audience', 'domain', 'expiresAt', 'unknowns', 'knowledgeId', 'workingRevision',
               'hashContractVersion', 'rawSha256')
SAMPLE_RESULTS = {'confirmed', 'needs_fix'}
TRANSITIONS = {'unconfirmed': {'in_review', 'held'}, 'in_review': {'held', 'rejected'},
               'held': {'in_review'}, 'awaiting_review': {'in_review', 'held'},
               'reflected': {'in_review'}, 'rejected': set()}


class Failure(Exception):
    def __init__(self, status, code):
        self.status, self.code = status, code
        super().__init__(code)


def require(condition, status=400, code='ValidationError'):
    if not condition:
        raise Failure(status, code)


def text(value, maximum=2000):
    require(isinstance(value, str) and bool(value.strip()) and len(value) <= maximum
            and not any(ord(char) < 32 and char not in '\n\t' for char in value))
    return value


def exact(data, required, optional=()):
    require(isinstance(data, dict) and set(required) <= data.keys()
            and data.keys() <= set(required) | set(optional))


def to_canonical(value):
    """Explicit API camelCase → canonical/audit snake_case boundary (the bundle hash input)."""
    if isinstance(value, list):
        return [to_canonical(item) for item in value]
    if isinstance(value, dict):
        return {re.sub(r'[A-Z]', lambda match: '_' + match[0].lower(), key): to_canonical(item)
                for key, item in value.items()}
    return value


class Service:
    def __init__(self, store, work, canonical, policy, *, enabled=False,
                 clock=time.time, fault=lambda stage: None, policy_source=None):
        self.store, self.work, self.canonical = store, work, canonical
        self.policy, self.enabled, self.clock, self.fault = policy, enabled, clock, fault
        self.policy_source = policy_source

    def begin_request(self):
        """Deployed grants are re-read per request so revocation applies without redeploying."""
        if self.policy_source is not None:
            self.policy = self.policy_source()

    def principal(self, claims):
        require(self.enabled, 403, 'FeatureUnavailable')
        require(isinstance(claims, dict) and isinstance(claims.get('sub'), str)
                and bool(claims['sub']), 401, 'Unauthorized')
        return claims['sub']

    def authorize(self, claims, permission, domain, audience):
        """Only the protected grant table decides. Cognito groups (admin included) grant nothing."""
        actor = self.principal(claims)
        assignment = self.policy.get('actors', {}).get(actor, {})
        require(assignment.get('expiresAt', 0) > self.clock()
                and domain in assignment.get('domains', [])
                and audience in assignment.get('audiences', [])
                and permission in assignment.get('permissions', []), 403, 'Forbidden')
        return actor

    def me(self, claims):
        """The caller's own live grants, so the screen can show and gate what the API will allow."""
        actor = self.principal(claims)
        now = self.clock()
        assignment = self.policy.get('actors', {}).get(actor, {})
        live = assignment.get('expiresAt', 0) > now
        scopes = {(domain, audience) for domain in assignment.get('domains', [])
                  for audience in assignment.get('audiences', [])} if live else set()
        return {
            'actor': actor,
            'assignment': {k: assignment.get(k) for k in ('permissions', 'domains', 'audiences', 'expiresAt')}
            if live else None,
            'contributions': [{'permissionId': name, **{k: value[k] for k in ('domain', 'audience', 'expiresAt')}}
                              for name, value in sorted(self.policy.get('contributions', {}).items())
                              if value.get('actor') == actor and value.get('expiresAt', 0) > now],
            'evidence': [{'id': name, **{k: value.get(k) for k in ('version', 'sha256', 'domain', 'audience',
                                                                    'expiresAt', 'sourceVerified')}}
                         for name, value in sorted(self.policy.get('evidence', {}).items())
                         if 'edit' in assignment.get('permissions', [])
                         and (value.get('domain'), value.get('audience')) in scopes
                         and value.get('expiresAt', 0) > now]}

    def alive(self, item):
        require(item is not None and item['expiresAt'] > self.clock(), 404, 'NotFound')
        return item

    def candidate(self, db, identifier, claims, permission='view'):
        item = self.alive(db.get('candidate', identifier))
        self.authorize(claims, permission, item['domain'], item['audience'])
        return item

    def card(self, db, identifier, claims, permission):
        card = db.get('card', identifier)
        require(card is not None, 404, 'NotFound')
        self.candidate(db, card['candidateId'], claims, permission)
        return card

    def mutate(self, claims, key, target, request, execute):
        actor = self.principal(claims)
        require(isinstance(key, str) and ID.fullmatch(key))
        request_hash = digest({'target': target, 'request': request})
        with self.store.unit() as db:
            row = db.operation_by_key(actor, key)
            if row:
                require(row['requestHash'] == request_hash, 409, 'IdempotencyConflict')
                if row['status'] == 'rejected':
                    raise Failure(row['result']['status'], row['result']['code'])
                if row['status'] == 'completed':
                    return row['result']
                operation = row['id']
            else:
                require(not db.target_pending(target), 409, 'OperationPending')
                operation = str(uuid.uuid4())
                db.accept_operation(operation, actor, key, request_hash, target)
                db.put('operation-intent', operation, {'at': int(self.clock()), 'request': request})
        # Acceptance survives S3 failures and process death. Ledger projections, events and
        # completion commit together, after the external working/canonical S3 writes.
        # A lost ledger race (Contention) is not a Failure: the operation stays accepted.
        try:
            with self.store.unit() as db:
                row = db.operation(operation)
                if row['status'] == 'completed':
                    return row['result']
                if row['status'] == 'rejected':
                    raise Failure(row['result']['status'], row['result']['code'])
                result = execute(db, operation)
                self.fault('before_projection_commit')
                action = request[0] if isinstance(request, list) else 'contribute'
                role = {'decision': 'approve', 'sample': 'approve', 'publish': 'publish',
                        'withdraw': 'publish', 'contribute': 'contribute',
                        'migrate': 'migrate'}.get(action, 'edit')
                detail = request[-1] if isinstance(request, list) and isinstance(request[-1], dict) else {}
                db.put('event', operation, {
                    'operationId': operation, 'actor': actor, 'target': target,
                    'requestHash': request_hash, 'at': int(self.clock()), 'result': result,
                    'role': role, 'reason': detail.get('reason')})
                db.finish_operation(operation, 'completed', result)
                intent = db.get('operation-intent', operation)
                db.put('operation-intent', operation, {'at': intent['at']})
            return result
        except Failure as error:
            with self.store.unit() as db:
                db.finish_operation(operation, 'rejected', {'status': error.status, 'code': error.code})
            raise

    def contribute(self, claims, key, data):
        actor = self.principal(claims)
        exact(data, ('candidateType', 'originRef', 'summary', 'context', 'domain', 'audience',
                     'permissionId', 'confirmedHash'), ('term', 'targetKnowledgeId', 'targetRevision'))
        require(data['candidateType'] in {'field_report', 'unknown_term', 'correction', 'request'})
        for name in ('summary', 'context', 'domain', 'audience', 'permissionId'):
            text(data[name], 200 if name != 'context' else 2000)
        exact(data['originRef'], ('id', 'revision'))
        text(data['originRef']['id'], 200)
        require(type(data['originRef']['revision']) is int and data['originRef']['revision'] > 0)
        if data['candidateType'] == 'unknown_term':
            text(data.get('term'), 200)
        if data['candidateType'] == 'correction':
            require(isinstance(data.get('targetKnowledgeId'), str)
                    and ID.fullmatch(data['targetKnowledgeId']))
            require(type(data.get('targetRevision')) is int and data['targetRevision'] > 0)
            with self.store.unit() as db:
                target = db.get('card', data['targetKnowledgeId'])
                require(target is not None, 404, 'NotFound')
                version = target['versions'].get(str(data['targetRevision']))
                require(version and version['status'] == 'approved', 409, 'VersionConflict')
                self.authorize(claims, 'read', version['domain'], version['audience'])
                require(version['domain'] == data['domain'] and version['audience'] == data['audience'],
                        403, 'ScopeDenied')
        confirmed = {k: v for k, v in data.items() if k != 'confirmedHash'}
        require(data['confirmedHash'] == digest(confirmed), 409, 'ConfirmationStale')
        permission = self.policy.get('contributions', {}).get(data['permissionId'], {})
        require(permission.get('actor') == actor and permission.get('expiresAt', 0) > self.clock()
                and permission.get('domain') == data['domain']
                and permission.get('audience') == data['audience']
                and permission.get('allowDerived') is True
                and permission.get('retentionPolicyId'), 403, 'SharingNotPermitted')
        origin_key = digest([actor, data['candidateType'], data['originRef']])
        def create(db, operation):
            previous = db.get('origin', origin_key)
            if previous:
                require(previous['hash'] == digest(confirmed), 409, 'OriginConflict')
                return previous['result']
            identifier = operation
            item = {**copy.deepcopy(confirmed), 'candidateId': identifier, 'candidateRevision': 1,
                    'schemaVersion': 1, 'submittedBy': actor, 'submittedAt': int(self.clock()),
                    'expiresAt': permission['expiresAt'], 'state': 'unconfirmed',
                    'retentionPolicyId': permission['retentionPolicyId'],
                    'revisions': [{'revision': 1, 'context': data['context'], 'actor': actor}],
                    'targetLinks': []}
            db.put('candidate', identifier, item)
            result = {'candidateId': identifier, 'candidateRevision': 1, 'state': 'unconfirmed'}
            db.put('origin', origin_key, {'hash': digest(confirmed), 'result': result})
            return result
        return self.mutate(claims, key, 'origin:' + origin_key, data, create)

    def list_candidates(self, claims, scope, state, after=None, limit=20):
        actor = self.principal(claims)
        require(scope in {'mine', 'inbox'} and state in STATES)
        require((after is None or (isinstance(after, str) and POSITION.fullmatch(after)))
                and type(limit) is int and 1 <= limit <= 50)
        if scope == 'inbox':
            assignment = self.policy.get('actors', {}).get(actor, {})
            require(assignment.get('domains') and assignment.get('audiences')
                    and 'view' in assignment.get('permissions', [])
                    and assignment.get('expiresAt', 0) > self.clock(), 403, 'Forbidden')
        # One bounded index page. Index order is not authority: every row was re-read from the
        # base records and is re-checked here, so a short page plus cursor is expected.
        page, following = self.store.candidates(state, actor if scope == 'mine' else None, after, limit)
        rows = []
        for item in page:
            if item['state'] != state or item['expiresAt'] <= self.clock():
                continue
            if scope == 'mine' and item['submittedBy'] != actor:
                continue
            if scope == 'inbox':
                try:
                    self.authorize(claims, 'view', item['domain'], item['audience'])
                except Failure:
                    continue
            rows.append({k: item[k] for k in ('candidateId', 'candidateRevision',
                         'candidateType', 'state', 'submittedAt')})
        return {'items': rows, 'next': following}

    def detail(self, claims, identifier):
        actor = self.principal(claims)
        with self.store.unit() as db:
            item = self.alive(db.get('candidate', identifier))
            try:
                # A submitter who also holds the view grant (e.g. edits their own report) sees all of it.
                self.authorize(claims, 'view', item['domain'], item['audience'])
                return item
            except Failure:
                require(item['submittedBy'] == actor, 403, 'Forbidden')
            return {k: item[k] for k in ('candidateId', 'candidateRevision', 'state',
                                         'summary', 'context', 'candidateType', 'expiresAt')}

    def transition(self, claims, key, identifier, revision, data):
        exact(data, ('state', 'reason'), ('resumeCondition',))
        text(data['reason'])
        if data['state'] == 'held':
            text(data.get('resumeCondition'))
        with self.store.unit() as db:
            self.candidate(db, identifier, claims, 'edit')
        def change(db, operation):
            item = self.candidate(db, identifier, claims, 'edit')
            require(item['candidateRevision'] == revision, 409, 'VersionConflict')
            require(data['state'] in TRANSITIONS[item['state']], 409, 'InvalidTransition')
            item.update(data)
            item['candidateRevision'] += 1
            item['assignee'] = claims['sub']
            db.put('candidate', identifier, item)
            return {'candidateId': identifier, 'candidateRevision': item['candidateRevision'],
                    'state': item['state']}
        return self.mutate(claims, key, 'candidate:' + identifier, [revision, data], change)

    def validate_draft(self, data):
        exact(data, ('candidateId', 'candidateRevision', 'kind', 'markdown', 'applicability',
                     'sourceRefs', 'audience', 'domain', 'expiresAt', 'unknowns'), ('secondReview',))
        self.validate_declaration(data.get('secondReview', []))
        require(data['kind'] in KINDS)
        text(data['markdown'], 256 * 1024)
        require(len(data['markdown'].encode('utf-8')) <= 256 * 1024)
        require('\r' not in data['markdown'], 400, 'LfRequired')
        text(data['applicability'])
        require(isinstance(data['unknowns'], list) and len(data['unknowns']) <= 20)
        for unknown in data['unknowns']:
            text(unknown)
        require(isinstance(data['sourceRefs'], list) and 1 <= len(data['sourceRefs']) <= 20)
        for source in data['sourceRefs']:
            exact(source, ('id', 'version', 'locator', 'sha256', 'claimType', 'verified'))
            for field in ('id', 'version', 'locator'):
                text(source[field], 200)
            require(isinstance(source['sha256'], str) and re.fullmatch('[0-9a-f]{64}', source['sha256']))
            require(source['claimType'] in {'ai_hypothesis', 'technician_statement', 'source_verified'}
                    and type(source['verified']) is bool)
        require(type(data['expiresAt']) is int and data['expiresAt'] > self.clock())

    def validate_declaration(self, declared):
        """作成者が申告する §4.3 の例外。空なら申告なし（コードの規則による印は別に付く）。"""
        require(isinstance(declared, list) and len(declared) <= len(second_review.REASONS)
                and len(set(declared)) == len(declared)
                and all(reason in second_review.REASONS for reason in declared))

    def evidence_authorized(self, version):
        """A client verified flag is insufficient: require the protected evidence registry."""
        for source in version['sourceRefs']:
            permission = self.policy.get('evidence', {}).get(source['id'], {})
            require(permission.get('version') == source['version']
                    and permission.get('sha256') == source['sha256']
                    and permission.get('domain') == version['domain']
                    and permission.get('audience') == version['audience']
                    and permission.get('expiresAt', 0) > self.clock()
                    and permission.get('independent') is True
                    and (source['claimType'] != 'source_verified'
                         or permission.get('sourceVerified') is True), 403, 'EvidenceNotPermitted')

    def verify_bundle(self, version):
        require(digest(to_canonical({k: version[k] for k in BUNDLE_KEYS})) == version['bundleHash'],
                409, 'BundleHashMismatch')
        self.evidence_authorized(version)

    def save_draft(self, claims, key, identifier, working_revision, data):
        """Screen/API edit: the server writes the body to the working bucket and pins that version."""
        require(ID.fullmatch(identifier))
        self.validate_draft(data)
        raw = data['markdown'].encode('utf-8')
        # The declaration is a ledger mark, not part of the bundle hash contract (i1-json-lf-v1).
        fields = {k: v for k, v in data.items() if k not in {'markdown', 'secondReview'}}
        return self._draft(claims, key, identifier, working_revision, fields, raw,
                           data.get('secondReview', []),
                           ['draft', identifier, working_revision, data],
                           lambda operation: self.work.put(identifier, raw, operation))

    def register_draft(self, claims, key, identifier, working_revision, data):
        """CLI: pin a version already written to the working bucket (e.g. by the development agent)."""
        require(ID.fullmatch(identifier))
        exact(data, ('candidateId', 'candidateRevision', 'kind', 'applicability', 'sourceRefs',
                     'audience', 'domain', 'expiresAt', 'unknowns', 'workVersionId'), ('secondReview',))
        require(isinstance(data['workVersionId'], str) and 0 < len(data['workVersionId']) <= 1024)
        raw = self.work.read(identifier, data['workVersionId'])
        require(raw is not None, 409, 'WorkVersionMissing')
        fields = {k: v for k, v in data.items() if k not in {'workVersionId', 'secondReview'}}
        self.validate_draft({**fields, 'markdown': raw.decode('utf-8'),
                             'secondReview': data.get('secondReview', [])})
        return self._draft(claims, key, identifier, working_revision, fields, raw,
                           data.get('secondReview', []),
                           ['register', identifier, working_revision, data],
                           lambda operation: data['workVersionId'])

    def _draft(self, claims, key, identifier, working_revision, fields, raw, declared, request, write):
        with self.store.unit() as db:
            self.candidate(db, fields['candidateId'], claims, 'edit')
        def save(db, operation):
            item = self.candidate(db, fields['candidateId'], claims, 'edit')
            require(item['candidateRevision'] == fields['candidateRevision'], 409, 'VersionConflict')
            require(item['state'] in {'in_review', 'awaiting_review'}, 409, 'InvalidTransition')
            require(fields['domain'] == item['domain'] and fields['audience'] == item['audience']
                    and fields['expiresAt'] <= item['expiresAt'], 403, 'ScopeDenied')
            card = db.get('card', identifier) or {
                'knowledgeId': identifier, 'workingRevision': 0, 'candidateId': item['candidateId'],
                'versions': {}, 'review': None}
            correction = (item['candidateType'] == 'correction'
                          and item['targetKnowledgeId'] == identifier
                          and item['targetRevision'] == working_revision)
            require((card['candidateId'] == item['candidateId'] or correction)
                    and card['workingRevision'] == working_revision, 409, 'VersionConflict')
            previous = None
            if correction:
                previous = card['versions'].get(str(working_revision))
                require(previous and previous['status'] == 'approved'
                        and previous['domain'] == item['domain'] and previous['audience'] == item['audience'],
                        409, 'VersionConflict')
                card['candidateId'] = item['candidateId']
            version = working_revision + 1
            metadata = {**fields, 'knowledgeId': identifier, 'workingRevision': version,
                        'hashContractVersion': 'i1-json-lf-v1', 'rawSha256': digest(raw)}
            bundle_hash = digest(to_canonical(metadata))
            work_version = write(operation)
            self.fault('after_work')
            marks = second_review.assess(raw.decode('utf-8'), fields, declared, previous)
            card['versions'][str(version)] = {**metadata, 'bundleHash': bundle_hash,
                'workVersionId': work_version, 'editor': claims['sub'], 'status': 'draft',
                'secondReview': marks}
            card.update({'workingRevision': version, 'review': None})
            item.update({'state': 'in_review', 'candidateRevision': item['candidateRevision'] + 1})
            item['targetLinks'] = sorted(set([*item['targetLinks'], identifier]))
            db.put('candidate', item['candidateId'], item)
            db.put('card', identifier, card)
            return {'knowledgeId': identifier, 'workingRevision': version,
                    'candidateRevision': item['candidateRevision'], 'bundleHash': bundle_hash,
                    'rawSha256': digest(raw), 'workVersionId': work_version, 'secondReview': marks}
        return self.mutate(claims, key, 'candidate:' + fields['candidateId'], request, save)

    def pinned(self, identifier, version):
        """The exact working version the ledger recorded; later edits of drafts/ never substitute."""
        raw = self.work.read(identifier, version['workVersionId'])
        require(raw is not None and digest(raw) == version['rawSha256'], 409, 'WorkVersionConflict')
        return raw

    def review(self, claims, key, identifier, revision, data):
        exact(data, ('bundleHash', 'reason'))
        text(data['reason'])
        with self.store.unit() as db:
            self.card(db, identifier, claims, 'edit')
        def request(db, operation):
            card = self.card(db, identifier, claims, 'edit')
            require(card['workingRevision'] == revision, 409, 'VersionConflict')
            version = card['versions'][str(revision)]
            require(version['status'] == 'draft' and version['bundleHash'] == data['bundleHash'],
                    409, 'VersionConflict')
            require(not version['unknowns'] and all(s['verified'] and s['claimType'] != 'ai_hypothesis'
                    for s in version['sourceRefs']) and all(s['id'] != identifier for s in version['sourceRefs']),
                    409, 'EvidenceUnresolved')
            self.verify_bundle(version)
            self.pinned(identifier, version)
            card['review'] = {'reviewRequestId': operation, 'revision': revision,
                              'bundleHash': version['bundleHash'], 'reason': data['reason'],
                              'workVersionId': version['workVersionId']}
            item = self.candidate(db, card['candidateId'], claims, 'edit')
            require(item['state'] == 'in_review', 409, 'InvalidTransition')
            item.update({'state': 'awaiting_review', 'candidateRevision': item['candidateRevision'] + 1})
            db.put('candidate', card['candidateId'], item)
            db.put('card', identifier, card)
            return card['review']
        return self.mutate(claims, key, 'candidate:' + self._candidate_id(identifier),
                           ['review', identifier, revision, data], request)

    def _candidate_id(self, identifier):
        with self.store.unit() as db:
            card = db.get('card', identifier)
            require(card is not None, 404, 'NotFound')
            return card['candidateId']

    def decide(self, claims, key, identifier, revision, data):
        exact(data, ('reviewRequestId', 'bundleHash', 'reason', 'decision'))
        require(data['decision'] in {'approve', 'return'})
        text(data['reason'])
        with self.store.unit() as db:
            self.card(db, identifier, claims, 'approve')
        def decide(db, operation):
            card = self.card(db, identifier, claims, 'approve')
            item = self.candidate(db, card['candidateId'], claims, 'approve')
            version = card['versions'].get(str(revision))
            require(version is not None and card['workingRevision'] == revision and card['review']
                    and card['review']['reviewRequestId'] == data['reviewRequestId']
                    and card['review']['workVersionId'] == version['workVersionId']
                    and version['bundleHash'] == data['bundleHash']
                    and item['state'] == 'awaiting_review', 409, 'ReviewStale')
            # Design 2026-11-11 §4.3: self-approval stays denied only for versions marked as exceptions;
            # versions saved before the mark existed count as exceptions. Other self-approvals become
            # sample-check targets (§4.2).
            marks = version.get('secondReview') or second_review.legacy()
            own = version['editor'] == claims['sub'] or item['submittedBy'] == claims['sub']
            require(not (own and marks['required']), 403, 'SelfApprovalDenied')
            require(version['expiresAt'] > self.clock(), 409, 'Expired')
            self.verify_bundle(version)
            if data['decision'] == 'approve':
                raw = self.pinned(identifier, version)
                approval = {**card['review'], 'approvalId': operation, 'actor': claims['sub'],
                            'role': 'approve', 'reason': data['reason'], 'at': int(self.clock()),
                            'selfApproved': own, 'secondReview': marks, 'versionBundle': version}
                # Approval time must survive retries after the canonical copy succeeds but the
                # ledger does not: use the durable acceptance timestamp of this operation.
                stamp = db.get('operation-intent', operation)
                if stamp:
                    approval['at'] = stamp['at']
                approved_key = f'{identifier}/{revision}/{version["bundleHash"]}'
                self.canonical.approve(approved_key, raw, to_canonical(approval))
                self.fault('after_approved')
                version.update({'status': 'approved', 'approvalId': operation, 'approvedKey': approved_key,
                                'approvedBy': claims['sub'], 'selfApproved': own})
                if own:
                    version['sampleCheck'] = {'status': 'pending'}
                item['state'] = 'reflected'
            else:
                item['state'] = 'in_review'
            card['review'] = None
            item['candidateRevision'] += 1
            db.put('candidate', card['candidateId'], item)
            db.put('card', identifier, card)
            return {'knowledgeId': identifier, 'revision': revision, 'state': item['state'],
                    'approvalId': version.get('approvalId'), 'approvedKey': version.get('approvedKey'),
                    'selfApproved': version.get('selfApproved', False),
                    'sampleCheck': (version.get('sampleCheck') or {}).get('status')}
        return self.mutate(claims, key, 'candidate:' + self._candidate_id(identifier),
                           ['decision', identifier, revision, data], decide)

    def sample_check(self, claims, key, identifier, revision, data):
        """Record another person's sample check of a self-approved version (design 2026-11-11 §4.2).
        Publication is unchanged: needs_fix is a record for the correction flow, not a withdrawal."""
        exact(data, ('approvalId', 'result', 'reason'))
        require(data['result'] in SAMPLE_RESULTS)
        text(data['reason'])
        require(isinstance(data['approvalId'], str) and 0 < len(data['approvalId']) <= 80)
        with self.store.unit() as db:
            self.card(db, identifier, claims, 'approve')
        def check(db, operation):
            card = self.card(db, identifier, claims, 'approve')
            version = card['versions'].get(str(revision))
            require(version is not None and version['status'] == 'approved'
                    and version.get('approvalId') == data['approvalId'], 409, 'VersionConflict')
            require((version.get('sampleCheck') or {}).get('status') == 'pending',
                    409, 'SampleCheckNotPending')
            require(claims['sub'] not in {version.get('approvedBy'), version['editor']},
                    403, 'SelfCheckDenied')
            stamp = db.get('operation-intent', operation)
            version['sampleCheck'] = {'status': data['result'], 'checkId': operation,
                                      'actor': claims['sub'], 'reason': data['reason'],
                                      'at': stamp['at'] if stamp else int(self.clock())}
            db.put('card', identifier, card)
            return {'knowledgeId': identifier, 'revision': revision, **version['sampleCheck']}
        return self.mutate(claims, key, 'sample:' + identifier,
                           ['sample', identifier, revision, data], check)

    def migrate(self, claims, key, identifier, data):
        """WP3 (design 2026-11-11 §4.11): register one Git card as approved and published, in one
        idempotent operation. The caller already wrote the converted card to drafts/ (workVersionId).

        This bypasses the review request on purpose (decided 2026-11-12): the evidence is one
        registry entry for the Git migration inventory, not per-source entries. Everything else is
        the normal contract: the caller needs edit, approve and publish grants, the working version
        is pinned by sha256, approved/ is an immutable copy, the manifest CAS starts at generation 0.
        Versions with a §4.3 exception mark are published and wait for another person's sample check.
        """
        exact(data, ('workVersionId', 'rawSha256', 'kind', 'applicability', 'domain', 'audience',
                     'expiresAt', 'evidence', 'cardVersion', 'reason'))
        require(isinstance(identifier, str) and ID.fullmatch(identifier))
        require(isinstance(data['workVersionId'], str) and 0 < len(data['workVersionId']) <= 1024)
        require(isinstance(data['rawSha256'], str) and re.fullmatch('[0-9a-f]{64}', data['rawSha256']))
        require(data['kind'] in {'case_summary', 'practice_guide'})
        text(data['applicability'])
        text(data['domain'], 200)
        text(data['audience'], 200)
        text(data['reason'])
        require(type(data['expiresAt']) is int and data['expiresAt'] > self.clock())
        require(type(data['cardVersion']) is int and data['cardVersion'] > 0)
        exact(data['evidence'], ('id', 'version', 'locator', 'sha256'))
        for field in ('id', 'version', 'locator'):
            text(data['evidence'][field], 200)
        require(isinstance(data['evidence']['sha256'], str)
                and re.fullmatch('[0-9a-f]{64}', data['evidence']['sha256']))
        for permission in ('edit', 'approve', 'publish'):
            self.authorize(claims, permission, data['domain'], data['audience'])
        actor = claims['sub']

        def run(db, operation):
            for permission in ('edit', 'approve', 'publish'):
                self.authorize(claims, permission, data['domain'], data['audience'])
            require(db.get('card', identifier) is None, 409, 'AlreadyExists')
            raw = self.work.read(identifier, data['workVersionId'])
            require(raw is not None and digest(raw) == data['rawSha256'], 409, 'WorkVersionConflict')
            markdown = raw.decode('utf-8')
            require('\r' not in markdown, 400, 'LfRequired')
            text(markdown, 256 * 1024)
            require(len(raw) <= 256 * 1024)
            frontmatter = markdown.split('\n---\n', 1)[0]
            require(markdown.startswith('---\n')
                    and f'\nknowledge_id: {identifier}\n' in frontmatter + '\n', 400, 'IdentifierMismatch')
            stamp = db.get('operation-intent', operation)
            at = stamp['at'] if stamp else int(self.clock())
            evidence = data['evidence']
            fields = {'candidateId': operation, 'candidateRevision': 1, 'kind': data['kind'],
                      'applicability': data['applicability'],
                      'sourceRefs': [{**evidence, 'claimType': 'technician_statement', 'verified': True}],
                      'audience': data['audience'], 'domain': data['domain'],
                      'expiresAt': data['expiresAt'], 'unknowns': []}
            metadata = {**fields, 'knowledgeId': identifier, 'workingRevision': 1,
                        'hashContractVersion': 'i1-json-lf-v1', 'rawSha256': data['rawSha256']}
            self.evidence_authorized(metadata)
            bundle_hash = digest(to_canonical(metadata))
            marks = second_review.assess(markdown, fields, [], None)
            migration = {'cardVersion': data['cardVersion'], 'evidenceId': evidence['id'],
                         'evidenceVersion': evidence['version'], 'locator': evidence['locator']}
            version = {**metadata, 'bundleHash': bundle_hash, 'workVersionId': data['workVersionId'],
                       'editor': actor, 'secondReview': marks, 'migration': migration}
            approved_key = f'{identifier}/1/{bundle_hash}'
            approval = {'reviewRequestId': None, 'revision': 1, 'bundleHash': bundle_hash,
                        'workVersionId': data['workVersionId'], 'approvalId': operation, 'actor': actor,
                        'role': 'approve', 'reason': data['reason'], 'at': at, 'selfApproved': True,
                        'secondReview': marks, 'migration': migration, 'versionBundle': version}
            self.canonical.approve(approved_key, raw, to_canonical(approval))
            self.fault('after_approved')
            bundle = {**{k: metadata[k] for k in BUNDLE_KEYS}, 'bundleHash': bundle_hash}
            manifest = self.canonical.compare_swap(identifier, 0, approved_key, operation, bundle)
            require(manifest is not None, 409, 'ManifestConflict')
            self.fault('after_manifest')
            self.canonical.project(identifier)
            version.update({'status': 'approved', 'approvalId': operation, 'approvedKey': approved_key,
                            'approvedBy': actor, 'selfApproved': True})
            if marks['required']:
                version['sampleCheck'] = {'status': 'pending'}
            db.put('candidate', operation, {
                'candidateId': operation, 'candidateRevision': 1, 'candidateType': 'migration',
                'schemaVersion': 1, 'submittedBy': actor, 'submittedAt': at,
                'expiresAt': data['expiresAt'], 'state': 'reflected', 'domain': data['domain'],
                'audience': data['audience'], 'summary': identifier + ' の移行',
                'context': data['reason'], 'originRef': {'id': evidence['locator'],
                                                         'revision': data['cardVersion']},
                'retentionPolicyId': 'migration', 'targetLinks': [identifier],
                'revisions': [{'revision': 1, 'context': data['reason'], 'actor': actor}]})
            db.put('card', identifier, {'knowledgeId': identifier, 'workingRevision': 1,
                                        'candidateId': operation, 'versions': {'1': version},
                                        'review': None})
            return {'knowledgeId': identifier, 'workingRevision': 1, 'bundleHash': bundle_hash,
                    'rawSha256': data['rawSha256'], 'approvalId': operation,
                    'approvedKey': approved_key, 'generation': manifest['generation'],
                    'secondReview': marks['required'],
                    'sampleCheck': (version.get('sampleCheck') or {}).get('status')}
        return self.mutate(claims, key, 'migration:' + identifier, ['migrate', identifier, data], run)

    def publish(self, claims, key, identifier, generation, data, withdraw=False):
        exact(data, ('reason',) if withdraw else ('reason', 'revision', 'approvalId'))
        text(data['reason'])
        with self.store.unit() as db:
            self.card(db, identifier, claims, 'publish')
        def change(db, operation):
            card = self.card(db, identifier, claims, 'publish')
            active = bundle = None
            if not withdraw:
                version = card['versions'].get(str(data['revision']))
                require(version and version['status'] == 'approved'
                        and version['approvalId'] == data['approvalId']
                        and version['expiresAt'] > self.clock(), 409, 'ApprovalRequired')
                self.verify_bundle(version)
                raw = self.canonical.read_approved(version['approvedKey'])
                require(raw is not None and digest(raw) == version['rawSha256'], 409, 'HashMismatch')
                active = version['approvedKey']
                bundle = {**{k: version[k] for k in BUNDLE_KEYS}, 'bundleHash': version['bundleHash']}
            # Manifest first, then published/ follows the latest manifest: a stop always wins.
            manifest = self.canonical.compare_swap(identifier, generation, active, operation, bundle)
            require(manifest is not None, 409, 'ManifestConflict')
            self.fault('after_manifest')
            self.canonical.project(identifier)
            return {'knowledgeId': identifier, **manifest}
        return self.mutate(claims, key, ('withdrawal:' if withdraw else 'publication:') + identifier,
                           ['withdraw' if withdraw else 'publish', generation, data], change)

    def published(self, claims, identifier):
        # Reads touch only the manifest, published/ and the protected policy, never the ledger.
        self.principal(claims)
        manifest = self.canonical.manifest(identifier)
        require(manifest['active'] is not None, 404, 'NotPublished')
        bundle = manifest['bundle']
        self.authorize(claims, 'read', bundle['domain'], bundle['audience'])
        self.verify_bundle(bundle)
        require(bundle['expiresAt'] > self.clock(), 404, 'Expired')
        raw = self.canonical.read_published(identifier)
        require(raw is not None and digest(raw) == bundle['rawSha256'], 503, 'ProjectionPending')
        require(self.canonical.manifest(identifier) == manifest, 409, 'PublicationChanged')
        return {k: bundle[k] for k in ('knowledgeId', 'workingRevision', 'bundleHash', 'rawSha256',
                                       'kind', 'applicability', 'sourceRefs', 'expiresAt')} | {
                    'markdown': raw.decode('utf-8'), 'generation': manifest['generation']}

    def guarded_use(self, claims, identifier, consumer):
        """Both AI adapters revalidate before input and before returning/citing output."""
        before = self.published(claims, identifier)
        result = consumer(copy.deepcopy(before))
        after = self.published(claims, identifier)
        require(all(before[k] == after[k] for k in ('generation', 'bundleHash', 'rawSha256')),
                409, 'PublicationChanged')
        return result

    def card_detail(self, claims, identifier):
        with self.store.unit() as db:
            card = self.card(db, identifier, claims, 'view')
        version = card['versions'][str(card['workingRevision'])]
        return {**card, 'markdown': self.pinned(identifier, version).decode('utf-8')}

    def operation(self, claims, identifier):
        actor = self.principal(claims)
        with self.store.unit() as db:
            row = db.operation(identifier)
            require(row is not None and row['actor'] == actor, 404, 'NotFound')
            return {'operationId': identifier, 'status': row['status'],
                    'retrySameKey': row['status'] == 'accepted'}

    def pending_operations(self, claims):
        actor = self.principal(claims)
        return {'items': [{'operationId': row['id'], 'status': row['status']}
                          for row in self.store.pending_operations(actor, 50)
                          if row['actor'] == actor and row['status'] == 'accepted']}

    def resume(self, claims, identifier):
        actor = self.principal(claims)
        with self.store.unit() as db:
            row = db.operation(identifier)
            require(row is not None and row['actor'] == actor, 404, 'NotFound')
            if row['status'] == 'completed':
                return {'operationId': identifier, 'status': 'completed'}
            require(row['status'] == 'accepted', 409, 'OperationNotPending')
            request = db.get('operation-intent', identifier)['request']
            target, key = row['target'], row['key']
        # Original action revalidates live grants, ownership, versions and publication CAS.
        if isinstance(request, dict):
            return self.contribute(claims, key, request)
        if type(request[0]) is int:
            return self.transition(claims, key, target.split(':', 1)[1], *request)
        action = request[0]
        if action == 'draft':
            return self.save_draft(claims, key, *request[1:])
        if action == 'register':
            return self.register_draft(claims, key, *request[1:])
        if action in {'review', 'decision'}:
            return (self.review if action == 'review' else self.decide)(claims, key, *request[1:])
        if action == 'sample':
            return self.sample_check(claims, key, *request[1:])
        if action == 'migrate':
            return self.migrate(claims, key, *request[1:])
        return self.publish(claims, key, target.split(':', 1)[1], *request[1:], withdraw=action == 'withdraw')
