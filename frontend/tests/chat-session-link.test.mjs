import test from 'node:test';
import assert from 'node:assert/strict';
import { buildChatSessionHref, resolveInitialChatMode } from '../src/lib/chat-session-link.mjs';

test('法令モードのセッションには mode=law を付ける', () => {
  assert.equal(buildChatSessionHref('s1', 'law'), '/chat?session=s1&mode=law');
});

test('通常モード・未指定では mode を付けない', () => {
  assert.equal(buildChatSessionHref('s1', 'normal'), '/chat?session=s1');
  assert.equal(buildChatSessionHref('s1', 'spec'), '/chat?session=s1');
  assert.equal(buildChatSessionHref('s1'), '/chat?session=s1');
  assert.equal(buildChatSessionHref('s1', null), '/chat?session=s1');
});

test('セッション ID は URL エンコードする', () => {
  assert.equal(buildChatSessionHref('a b&c', 'law'), '/chat?session=a%20b%26c&mode=law');
});

test('URL の mode=law から初期モードを law にする', () => {
  assert.equal(resolveInitialChatMode('?session=s1&mode=law'), 'law');
  assert.equal(resolveInitialChatMode('?mode=law'), 'law');
});

test('mode が無い・law 以外は normal', () => {
  assert.equal(resolveInitialChatMode(''), 'normal');
  assert.equal(resolveInitialChatMode(null), 'normal');
  assert.equal(resolveInitialChatMode('?session=s1'), 'normal');
  assert.equal(resolveInitialChatMode('?mode=spec'), 'normal');
});
