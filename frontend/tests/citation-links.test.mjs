import assert from 'node:assert/strict';
import test from 'node:test';
import { knowhowCardAnchor, linkCitedNames } from '../src/lib/citation-links.mjs';

const DOC = { names: ['TI-1158.pdf', 'テクニカルインフォメーション'], href: '/doc?uri=s3%3A%2F%2Fb%2FTI-1158.pdf' };

test('links only names of documents that the answer actually returned', () => {
  const out = linkCitedNames('**TI-1158.pdf** と TI-1158 と TI-9999.pdf を参照', [DOC]);
  assert.equal(out, '**[TI-1158.pdf](</doc?uri=s3%3A%2F%2Fb%2FTI-1158.pdf>)** と [TI-1158](</doc?uri=s3%3A%2F%2Fb%2FTI-1158.pdf>) と TI-9999.pdf を参照');
});

test('does not match inside longer words, code or existing links', () => {
  const text = 'TI-11580 / `TI-1158.pdf` / [TI-1158.pdf](https://x) / xTI-1158';
  assert.equal(linkCitedNames(text, [DOC]), text);
});

test('prefers the longest name and ignores unsafe or short names and hrefs', () => {
  const targets = [
    { names: ['C-8-S438'], href: '/doc?a' },
    { names: ['C-8-S438-K21-J-_.pdf'], href: '/doc?b' },
    { names: ['abc', 'x(y)z1'], href: '/doc?c' },
    { names: ['SAFE-NAME'], href: 'javascript:alert(1) x' },
  ];
  assert.equal(linkCitedNames('C-8-S438-K21-J-_.pdf と C-8-S438 と abc と SAFE-NAME', targets),
    '[C-8-S438-K21-J-_.pdf](</doc?b>) と [C-8-S438](</doc?a>) と abc と SAFE-NAME');
});

test('returns the input unchanged without targets', () => {
  assert.equal(linkCitedNames('本文', []), '本文');
  assert.equal(linkCitedNames('', [DOC]), '');
});

test('card anchors are stable and safe', () => {
  assert.equal(knowhowCardAnchor('senpai-turn-1', 'KH-ALL-1D2G_PAD.324'), 'senpai-turn-1-card-KH-ALL-1D2G-PAD-324');
});
