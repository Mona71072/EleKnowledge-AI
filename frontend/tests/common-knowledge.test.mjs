import assert from 'node:assert/strict';
import test from 'node:test';
import { canonicalJson, inputHash, requestKnowledge, validateConnection, validationGrant } from '../src/lib/common-knowledge.mjs';

test('confirmation and retry keys hash stable UTF-8 with nested sorted keys', async () => {
  const value = { z: '日本語\n', a: { v: 2, b: 1 } };
  assert.equal(canonicalJson(value), '{"a":{"b":1,"v":2},"z":"日本語\\n"}');
  assert.equal(await inputHash(value), await inputHash({ a: { b: 1, v: 2 }, z: '日本語\n' }));
  assert.notEqual(await inputHash(value), await inputHash({ ...value, z: '日本語\r\n' }));
});

test('synthetic claims cannot travel to production or non-loopback endpoints', () => {
  const local = { baseUrl: 'http://127.0.0.1:8765', synthetic: true, development: true, hostname: 'localhost' };
  assert.equal(validateConnection(local), local.baseUrl);
  for (const change of [{ development: false }, { hostname: 'app.example.com' },
    { baseUrl: 'https://api.example.com' }, { baseUrl: 'http://127.0.0.1:8765/other' },
    { baseUrl: 'http://user:password@127.0.0.1:8765' }]) {
    assert.throws(() => validateConnection({ ...local, ...change }));
  }
});

test('authenticated API keeps one HTTPS stage segment and rejects anything wider', () => {
  const remote = { synthetic: false, development: false, hostname: 'itai.example.com' };
  assert.equal(validateConnection({ ...remote, baseUrl: 'https://api.example.com/dev' }), 'https://api.example.com/dev');
  assert.equal(validateConnection({ ...remote, baseUrl: 'https://api.example.com/dev/' }), 'https://api.example.com/dev');
  assert.equal(validateConnection({ ...remote, baseUrl: 'https://api.example.com' }), 'https://api.example.com');
  for (const baseUrl of ['http://api.example.com/dev', 'https://api.example.com/dev/knowledge',
    'https://api.example.com//dev', 'https://api.example.com/dev?x=1', 'https://api.example.com/d%20v']) {
    assert.throws(() => validateConnection({ ...remote, baseUrl }), baseUrl);
  }
});

test('retries preserve actor-bound request key; publication CAS and no-store are explicit', async () => {
  const sent = [];
  const options = { baseUrl: 'http://127.0.0.1:8765', token: 'synthetic-publisher', actor: 'publisher',
    path: '/cards/KH-SYN/publish', method: 'POST', revision: 2, body: { reason: '合成', revision: 1 },
    fetchImpl: async (url, init) => { sent.push({ url, init }); return { ok: true, json: async () => ({ generation: 3 }) }; } };
  assert.deepEqual(await requestKnowledge(options), { generation: 3 });
  await requestKnowledge(options);
  assert.equal(sent[0].init.headers['Idempotency-Key'], sent[1].init.headers['Idempotency-Key']);
  assert.equal(sent[0].init.headers['If-Match'], '2');
  assert.equal(sent[0].init.cache, 'no-store');
  await requestKnowledge({ ...options, revision: 3 });
  assert.notEqual(sent[0].init.headers['Idempotency-Key'], sent[2].init.headers['Idempotency-Key']);
  await assert.rejects(requestKnowledge({ ...options, fetchImpl: async () => ({ ok: false,
    status: 409, json: async () => ({ code: 'ManifestConflict', message: '版が変わりました' }) }) }), /ManifestConflict/u);
});

test("real input is limited to the validation scope and the caller's own live grants", async () => {
  const me = {
    actor: 'sub-1',
    assignment: { permissions: ['view', 'edit'], domains: ['itai-validation'], audiences: ['itai-validation'], expiresAt: 1 },
    contributions: [{ permissionId: 'other', domain: 'x', audience: 'x', expiresAt: 1 },
      { permissionId: 'itai-validation-sharing', domain: 'itai-validation', audience: 'itai-validation', expiresAt: 1 }],
    evidence: [{ id: 'E1', version: '1', sha256: 'b'.repeat(64), domain: 'itai-validation', audience: 'itai-validation', expiresAt: 1 },
      { id: 'E2', version: '1', sha256: 'c'.repeat(64), domain: 'x', audience: 'x', expiresAt: 1 }],
  };
  const grant = validationGrant(me, 'itai-validation');
  assert.deepEqual(grant.permissions, ['view', 'edit']);
  assert.equal(grant.contribution.permissionId, 'itai-validation-sharing');
  assert.deepEqual(grant.evidence.map((item) => item.id), ['E1']);
  assert.deepEqual(validationGrant(me, 'another'), { scope: 'another', permissions: [], contribution: null, evidence: [] });
  assert.deepEqual(validationGrant({ ...me, assignment: null }, 'itai-validation').permissions, []);
  for (const scope of ['', 'Itai Validation', '*']) assert.throws(() => validationGrant(me, scope));
  const sent = [];
  await requestKnowledge({ baseUrl: 'https://api.example.com/dev', token: 't', actor: 'a', path: '/me',
    fetchImpl: async (url) => { sent.push(url); return { ok: true, json: async () => ({}) }; } });
  assert.deepEqual(sent, ['https://api.example.com/dev/knowledge/me']);
  await assert.rejects(requestKnowledge({ baseUrl: 'https://api.example.com/dev', token: 't', actor: 'a', path: '/meta' }));
});
