"""Common candidate, exact-version review, publication and guarded read service."""
import copy
import re
import time
import uuid

from storage import digest, encode


ID = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$')
STATES = {'unconfirmed', 'in_review', 'awaiting_review', 'reflected', 'held', 'rejected'}
KINDS = {'case_summary', 'practice_guide', 'term_foundation'}
BUNDLE_KEYS = ('candidateId', 'candidateRevision', 'kind', 'applicability', 'sourceRefs',
               'audience', 'domain', 'expiresAt', 'unknowns', 'knowledgeId', 'workingRevision',
               'hashContractVersion', 'rawSha256')
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


def to_git(value):
    """Explicit API camelCase → canonical/audit snake_case boundary."""
    if isinstance(value, list):
        return [to_git(item) for item in value]
    if isinstance(value, dict):
        return {re.sub(r'[A-Z]', lambda match: '_' + match[0].lower(), key): to_git(item)
                for key, item in value.items()}
    return value


class Service:
    def __init__(self, store, git, distribution, policy, *, enabled=False,
                 clock=time.time, fault=lambda stage: None):
        self.store, self.git, self.distribution = store, git, distribution
        self.policy, self.enabled, self.clock, self.fault = policy, enabled, clock, fault

    def principal(self, claims):
        require(self.enabled, 403, 'FeatureUnavailable')
        require(isinstance(claims, dict) and isinstance(claims.get('sub'), str)
                and bool(claims['sub']), 401, 'Unauthorized')
        return claims['sub']

    def authorize(self, claims, permission, domain, audience):
        actor = self.principal(claims)
        groups = claims.get('cognito:groups', [])
        if isinstance(groups, str):
            groups = groups.split(',')
        require(permission == 'read' or 'admin' in groups, 403, 'Forbidden')
        assignment = self.policy.get('actors', {}).get(actor, {})
        require(assignment.get('expiresAt', 0) > self.clock()
                and domain in assignment.get('domains', [])
                and audience in assignment.get('audiences', [])
                and permission in assignment.get('permissions', []), 403, 'Forbidden')
        return actor

    def alive(self, item):
        require(item is not None and item['expiresAt'] > self.clock(), 404, 'NotFound')
        return item

    def candidate(self, db, identifier, claims, permission='view'):
        item = self.alive(self.store.get(db, 'candidate', identifier))
        self.authorize(claims, permission, item['domain'], item['audience'])
        return item

    def card(self, db, identifier, claims, permission):
        card = self.store.get(db, 'card', identifier)
        require(card is not None, 404, 'NotFound')
        self.candidate(db, card['candidateId'], claims, permission)
        return card

    def mutate(self, claims, key, target, request, execute):
        actor = self.principal(claims)
        require(isinstance(key, str) and ID.fullmatch(key))
        request_hash = digest({'target': target, 'request': request})
        with self.store.transaction() as db:
            row = db.execute('SELECT * FROM operations WHERE actor=? AND key=?',
                             (actor, key)).fetchone()
            if row:
                require(row['request_hash'] == request_hash, 409, 'IdempotencyConflict')
                if row['status'] == 'rejected':
                    saved = __import__('json').loads(row['result'])
                    raise Failure(saved['status'], saved['code'])
                if row['status'] == 'completed':
                    return __import__('json').loads(row['result'])
                operation = row['id']
            else:
                require(not db.execute('SELECT 1 FROM operations WHERE target=? '
                                       "AND status IN ('accepted','git_written')", (target,)).fetchone(),
                        409, 'OperationPending')
                operation = str(uuid.uuid4())
                db.execute('INSERT INTO operations VALUES (?,?,?,?,?,?,NULL)',
                           (operation, actor, key, request_hash, target, 'accepted'))
                self.store.put(db, 'operation-intent', operation, {'at': int(self.clock()), 'request': request})
        # Acceptance survives Git failures and process death. All projections, events,
        # manifest CAS and completion commit together, after the external Git write.
        try:
            with self.store.transaction() as db:
                row = db.execute('SELECT * FROM operations WHERE id=?', (operation,)).fetchone()
                if row['status'] == 'completed':
                    return __import__('json').loads(row['result'])
                if row['status'] == 'rejected':
                    saved = __import__('json').loads(row['result'])
                    raise Failure(saved['status'], saved['code'])
                result = execute(db, operation)
                self.fault('before_projection_commit')
                action = request[0] if isinstance(request, list) else 'contribute'
                role = {'decision': 'approve', 'publish': 'publish', 'withdraw': 'publish',
                        'contribute': 'contribute'}.get(action, 'edit')
                detail = request[-1] if isinstance(request, list) and isinstance(request[-1], dict) else {}
                self.store.put(db, 'event', operation, {
                    'operationId': operation, 'actor': actor, 'target': target,
                    'requestHash': request_hash, 'at': int(self.clock()), 'result': result,
                    'role': role, 'reason': detail.get('reason')})
                db.execute("UPDATE operations SET status='completed', result=? WHERE id=?",
                           (encode(result), operation))
                intent = self.store.get(db, 'operation-intent', operation)
                self.store.put(db, 'operation-intent', operation, {'at': intent['at']})
                return result
        except Failure as error:
            with self.store.transaction() as db:
                db.execute("UPDATE operations SET status='rejected',result=? WHERE id=?",
                           (encode({'status': error.status, 'code': error.code}), operation))
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
            with self.store.transaction() as db:
                target = self.store.get(db, 'card', data['targetKnowledgeId'])
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
            previous = self.store.get(db, 'origin', origin_key)
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
            self.store.put(db, 'candidate', identifier, item)
            result = {'candidateId': identifier, 'candidateRevision': 1, 'state': 'unconfirmed'}
            self.store.put(db, 'origin', origin_key, {'hash': digest(confirmed), 'result': result})
            return result
        return self.mutate(claims, key, 'origin:' + origin_key, data, create)

    def list_candidates(self, claims, scope, state, offset=0, limit=20):
        actor = self.principal(claims)
        require(scope in {'mine', 'inbox'} and state in STATES)
        require(type(offset) is int and offset >= 0 and type(limit) is int and 1 <= limit <= 50)
        with self.store.transaction() as db:
            groups = claims.get('cognito:groups', [])
            if isinstance(groups, str):
                groups = groups.split(',')
            if scope == 'inbox':
                require('admin' in groups, 403, 'Forbidden')
            sql = "SELECT value FROM records WHERE kind='candidate' AND json_extract(value,'$.state')=? AND json_extract(value,'$.expiresAt')>?"
            params = [state, self.clock()]
            if scope == 'mine':
                sql += " AND json_extract(value,'$.submittedBy')=?"
                params.append(actor)
            else:
                assignment = self.policy.get('actors', {}).get(actor, {})
                domains, audiences = assignment.get('domains', []), assignment.get('audiences', [])
                require(domains and audiences and 'view' in assignment.get('permissions', [])
                        and assignment.get('expiresAt', 0) > self.clock(), 403, 'Forbidden')
                sql += " AND json_extract(value,'$.domain') IN (" + ','.join('?' for _ in domains) + ')'
                sql += " AND json_extract(value,'$.audience') IN (" + ','.join('?' for _ in audiences) + ')'
                params += domains + audiences
            sql += " ORDER BY json_extract(value,'$.submittedAt'),id LIMIT ? OFFSET ?"
            params += [limit + 1, offset]
            raw_rows = db.execute(sql, params).fetchall()
            rows = []
            for row in raw_rows[:limit]:
                item = __import__('json').loads(row[0])
                if scope == 'inbox':
                    try:
                        self.authorize(claims, 'view', item['domain'], item['audience'])
                    except Failure:
                        continue
                rows.append({k: item[k] for k in ('candidateId', 'candidateRevision',
                             'candidateType', 'state', 'submittedAt')})
            return {'items': rows, 'nextOffset': offset + limit if len(raw_rows) > limit else None}

    def detail(self, claims, identifier):
        actor = self.principal(claims)
        with self.store.transaction() as db:
            item = self.alive(self.store.get(db, 'candidate', identifier))
            if item['submittedBy'] == actor:
                return {k: item[k] for k in ('candidateId', 'candidateRevision', 'state',
                                             'summary', 'context', 'candidateType', 'expiresAt')}
            self.authorize(claims, 'view', item['domain'], item['audience'])
            return item

    def transition(self, claims, key, identifier, revision, data):
        exact(data, ('state', 'reason'), ('resumeCondition',))
        text(data['reason'])
        if data['state'] == 'held':
            text(data.get('resumeCondition'))
        with self.store.transaction() as db:
            self.candidate(db, identifier, claims, 'edit')
        def change(db, operation):
            item = self.candidate(db, identifier, claims, 'edit')
            require(item['candidateRevision'] == revision, 409, 'VersionConflict')
            require(data['state'] in TRANSITIONS[item['state']], 409, 'InvalidTransition')
            item.update(data)
            item['candidateRevision'] += 1
            item['assignee'] = claims['sub']
            self.store.put(db, 'candidate', identifier, item)
            return {'candidateId': identifier, 'candidateRevision': item['candidateRevision'],
                    'state': item['state']}
        return self.mutate(claims, key, 'candidate:' + identifier, [revision, data], change)

    def validate_draft(self, data):
        exact(data, ('candidateId', 'candidateRevision', 'kind', 'markdown', 'applicability',
                     'sourceRefs', 'audience', 'domain', 'expiresAt', 'unknowns'))
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
        require(digest(to_git({k: version[k] for k in BUNDLE_KEYS})) == version['bundleHash'],
                409, 'BundleHashMismatch')
        self.evidence_authorized(version)

    def save_draft(self, claims, key, identifier, working_revision, data):
        require(ID.fullmatch(identifier))
        self.validate_draft(data)
        with self.store.transaction() as db:
            self.candidate(db, data['candidateId'], claims, 'edit')
        def save(db, operation):
            item = self.candidate(db, data['candidateId'], claims, 'edit')
            require(item['candidateRevision'] == data['candidateRevision'], 409, 'VersionConflict')
            require(item['state'] in {'in_review', 'awaiting_review'}, 409, 'InvalidTransition')
            require(data['domain'] == item['domain'] and data['audience'] == item['audience']
                    and data['expiresAt'] <= item['expiresAt'], 403, 'ScopeDenied')
            card = self.store.get(db, 'card', identifier) or {
                'knowledgeId': identifier, 'workingRevision': 0, 'candidateId': item['candidateId'],
                'versions': {}, 'review': None}
            correction = (item['candidateType'] == 'correction'
                          and item['targetKnowledgeId'] == identifier
                          and item['targetRevision'] == working_revision)
            require((card['candidateId'] == item['candidateId'] or correction)
                    and card['workingRevision'] == working_revision, 409, 'VersionConflict')
            if correction:
                previous = card['versions'].get(str(working_revision))
                require(previous and previous['status'] == 'approved'
                        and previous['domain'] == item['domain'] and previous['audience'] == item['audience'],
                        409, 'VersionConflict')
                card['candidateId'] = item['candidateId']
            version = working_revision + 1
            raw = data['markdown'].encode('utf-8')
            metadata = {k: v for k, v in data.items() if k != 'markdown'}
            metadata.update({'knowledgeId': identifier, 'workingRevision': version,
                             'hashContractVersion': 'i1-json-lf-v1', 'rawSha256': digest(raw)})
            bundle_hash = digest(to_git(metadata))
            path = f'proposals/{identifier}/{version}.md'
            commit = self.git.write(operation, {path: raw,
                f'proposals/{identifier}/{version}.json': encode(to_git(metadata)).encode('utf-8')})
            self.fault('after_git')
            card['versions'][str(version)] = {**metadata, 'bundleHash': bundle_hash,
                'draftCommit': commit, 'draftPath': path, 'editor': claims['sub'], 'status': 'draft'}
            card.update({'workingRevision': version, 'review': None})
            item.update({'state': 'in_review', 'candidateRevision': item['candidateRevision'] + 1})
            item['targetLinks'] = sorted(set([*item['targetLinks'], identifier]))
            self.store.put(db, 'candidate', item['candidateId'], item)
            self.store.put(db, 'card', identifier, card)
            return {'knowledgeId': identifier, 'workingRevision': version,
                    'candidateRevision': item['candidateRevision'], 'bundleHash': bundle_hash,
                    'rawSha256': digest(raw), 'gitCommit': commit}
        return self.mutate(claims, key, 'candidate:' + data['candidateId'],
                           ['draft', identifier, working_revision, data], save)

    def review(self, claims, key, identifier, revision, data):
        exact(data, ('bundleHash', 'reason'))
        text(data['reason'])
        with self.store.transaction() as db:
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
            current_raw = self.git.read('HEAD', version['draftPath'])
            require(digest(current_raw) == version['rawSha256'], 409, 'GitVersionConflict')
            current_metadata = self.git.read('HEAD', f'proposals/{identifier}/{revision}.json')
            require(digest(__import__('json').loads(current_metadata)) == version['bundleHash'],
                    409, 'GitVersionConflict')
            card['review'] = {'reviewRequestId': operation, 'revision': revision,
                              'bundleHash': version['bundleHash'], 'reason': data['reason'],
                              'baseTree': self.git.proposal_tree(identifier)}
            item = self.candidate(db, card['candidateId'], claims, 'edit')
            require(item['state'] == 'in_review', 409, 'InvalidTransition')
            item.update({'state': 'awaiting_review', 'candidateRevision': item['candidateRevision'] + 1})
            self.store.put(db, 'candidate', card['candidateId'], item)
            self.store.put(db, 'card', identifier, card)
            return card['review']
        return self.mutate(claims, key, 'candidate:' + self._candidate_id(identifier),
                           ['review', identifier, revision, data], request)

    def _candidate_id(self, identifier):
        with self.store.transaction() as db:
            card = self.store.get(db, 'card', identifier)
            require(card is not None, 404, 'NotFound')
            return card['candidateId']

    def decide(self, claims, key, identifier, revision, data):
        exact(data, ('reviewRequestId', 'bundleHash', 'reason', 'decision'))
        require(data['decision'] in {'approve', 'return'})
        text(data['reason'])
        with self.store.transaction() as db:
            self.card(db, identifier, claims, 'approve')
        def decide(db, operation):
            card = self.card(db, identifier, claims, 'approve')
            item = self.candidate(db, card['candidateId'], claims, 'approve')
            version = card['versions'].get(str(revision))
            require(version is not None and card['workingRevision'] == revision and card['review']
                    and card['review']['reviewRequestId'] == data['reviewRequestId']
                    and version['bundleHash'] == data['bundleHash']
                    and item['state'] == 'awaiting_review', 409, 'ReviewStale')
            require(version['editor'] != claims['sub'] and item['submittedBy'] != claims['sub'],
                    403, 'SelfApprovalDenied')
            require(version['expiresAt'] > self.clock(), 409, 'Expired')
            self.verify_bundle(version)
            require(self.git.proposal_tree(identifier) == card['review']['baseTree'],
                    409, 'GitVersionConflict')
            if data['decision'] == 'approve':
                raw = self.git.read(version['draftCommit'], version['draftPath'])
                require(digest(raw) == version['rawSha256'], 409, 'HashMismatch')
                approval = {**card['review'], 'approvalId': operation, 'actor': claims['sub'],
                            'role': 'approve', 'reason': data['reason'], 'at': int(self.clock()),
                            'versionBundle': version}
                canonical = f'cards/{identifier}/{revision}.md'
                # Approval time must survive retries after Git succeeds but DB does not.
                # Use the durable acceptance timestamp stored in the operation metadata.
                stamp = self.store.get(db, 'operation-intent', operation)
                if stamp:
                    approval['at'] = stamp['at']
                commit = self.git.write(operation, {canonical: raw,
                    f'approvals/{identifier}/{revision}.json': encode(to_git(approval)).encode('utf-8')})
                self.fault('after_git')
                version.update({'status': 'approved', 'approvalId': operation,
                                'canonicalCommit': commit, 'canonicalPath': canonical})
                item['state'] = 'reflected'
            else:
                item['state'] = 'in_review'
            card['review'] = None
            item['candidateRevision'] += 1
            self.store.put(db, 'candidate', card['candidateId'], item)
            self.store.put(db, 'card', identifier, card)
            return {'knowledgeId': identifier, 'revision': revision, 'state': item['state'],
                    'approvalId': version.get('approvalId'), 'gitCommit': version.get('canonicalCommit')}
        # Pin server time durably before the external Git write.
        # It is derived from the idempotency request, not from client supplied approval data.
        return self.mutate(claims, key, 'candidate:' + self._candidate_id(identifier),
                           ['decision', identifier, revision, data], decide)

    def publish(self, claims, key, identifier, generation, data, withdraw=False):
        exact(data, ('reason',) if withdraw else ('reason', 'revision', 'approvalId'))
        text(data['reason'])
        with self.store.transaction() as db:
            self.card(db, identifier, claims, 'publish')
        def change(db, operation):
            card = self.card(db, identifier, claims, 'publish')
            active = None
            if not withdraw:
                version = card['versions'].get(str(data['revision']))
                require(version and version['status'] == 'approved'
                        and version['approvalId'] == data['approvalId']
                        and version['expiresAt'] > self.clock(), 409, 'ApprovalRequired')
                self.verify_bundle(version)
                raw = self.git.read(version['canonicalCommit'], version['canonicalPath'])
                require(digest(raw) == version['rawSha256'], 409, 'HashMismatch')
                artifact = {**version, 'markdown': raw.decode('utf-8'), 'knowledgeId': identifier}
                active = f'{identifier}/{data["revision"]}/{version["bundleHash"]}'
                self.distribution.artifact(db, self.store, active, artifact)
                self.fault('after_artifact')
            manifest = self.distribution.compare_swap(db, self.store, identifier, generation, active, operation)
            require(manifest is not None, 409, 'ManifestConflict')
            self.fault('after_manifest')
            return {'knowledgeId': identifier, **manifest}
        return self.mutate(claims, key, ('withdrawal:' if withdraw else 'publication:') + identifier,
                           ['withdraw' if withdraw else 'publish', generation, data], change)

    def published(self, claims, identifier):
        self.principal(claims)
        with self.store.transaction() as db:
            manifest = self.distribution.manifest(db, self.store, identifier)
            require(manifest['active'] is not None, 404, 'NotPublished')
            artifact = self.distribution.read_artifact(manifest['active'])
            require(artifact is not None, 503, 'ArtifactUnavailable')
            self.authorize(claims, 'read', artifact['domain'], artifact['audience'])
            self.verify_bundle(artifact)
            require(artifact['expiresAt'] > self.clock(), 404, 'Expired')
            require(digest(artifact['markdown'].encode()) == artifact['rawSha256'], 503, 'HashMismatch')
            require(self.distribution.manifest(db, self.store, identifier) == manifest,
                    409, 'PublicationChanged')
            return {k: artifact[k] for k in ('knowledgeId', 'workingRevision', 'bundleHash',
                    'rawSha256', 'markdown', 'kind', 'applicability', 'sourceRefs', 'expiresAt')} | {
                        'generation': manifest['generation']}

    def guarded_use(self, claims, identifier, consumer):
        """Both AI adapters revalidate before input and before returning/citing output."""
        before = self.published(claims, identifier)
        result = consumer(copy.deepcopy(before))
        after = self.published(claims, identifier)
        require(all(before[k] == after[k] for k in ('generation', 'bundleHash', 'rawSha256')),
                409, 'PublicationChanged')
        return result

    def card_detail(self, claims, identifier):
        with self.store.transaction() as db:
            card = self.card(db, identifier, claims, 'view')
            version = card['versions'][str(card['workingRevision'])]
            raw = self.git.read(version['draftCommit'], version['draftPath'])
            return {**card, 'markdown': raw.decode('utf-8')}

    def operation(self, claims, identifier):
        actor = self.principal(claims)
        with self.store.transaction() as db:
            row = db.execute('SELECT * FROM operations WHERE id=? AND actor=?',
                             (identifier, actor)).fetchone()
            require(row is not None, 404, 'NotFound')
            return {'operationId': identifier, 'status': row['status'],
                    'retrySameKey': row['status'] == 'accepted'}

    def pending_operations(self, claims):
        actor = self.principal(claims)
        with self.store.transaction() as db:
            return {'items': [{'operationId': row['id'], 'status': row['status']} for row in
                    db.execute("SELECT id,status FROM operations WHERE actor=? AND status='accepted' LIMIT 50",
                               (actor,))]}

    def resume(self, claims, identifier):
        actor = self.principal(claims)
        with self.store.transaction() as db:
            row = db.execute('SELECT * FROM operations WHERE id=? AND actor=?', (identifier, actor)).fetchone()
            require(row is not None, 404, 'NotFound')
            if row['status'] == 'completed':
                return {'operationId': identifier, 'status': 'completed'}
            require(row['status'] == 'accepted', 409, 'OperationNotPending')
            request = self.store.get(db, 'operation-intent', identifier)['request']
            target, key = row['target'], row['key']
        # Original action revalidates live grants, ownership, versions and publication CAS.
        if isinstance(request, dict):
            return self.contribute(claims, key, request)
        if type(request[0]) is int:
            return self.transition(claims, key, target.split(':', 1)[1], *request)
        action = request[0]
        if action == 'draft':
            return self.save_draft(claims, key, *request[1:])
        if action in {'review', 'decision'}:
            return (self.review if action == 'review' else self.decide)(claims, key, *request[1:])
        return self.publish(claims, key, target.split(':', 1)[1], *request[1:], withdraw=action == 'withdraw')
