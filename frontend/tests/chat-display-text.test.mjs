import test from 'node:test';
import assert from 'node:assert/strict';
import { resolveAssistantDisplayText } from '../src/lib/chat-display-text.mjs';

const FULL = 'KE-LGの終点スイッチについて。資料から分かることは次のとおりです。';

test('タイプライター表示中のメッセージは途中の文字を返す', () => {
  assert.equal(resolveAssistantDisplayText('ai-1', FULL, 'ai-1', { 'ai-1': 'KE-LG' }), 'KE-LG');
});

test('表示開始直後（途中の文字なし）は空文字を返す', () => {
  assert.equal(resolveAssistantDisplayText('ai-1', FULL, 'ai-1', {}), '');
});

test('D8: 表示中でなければ、途中の文字が残っていても全文を返す', () => {
  // 会話の再読込で全文に置き換えた後、残っていたタイマーが途中の文字で上書きした状態
  assert.equal(resolveAssistantDisplayText('ai-1', FULL, null, { 'ai-1': 'KE-LGの終点' }), FULL);
});

test('別のメッセージを表示中なら、前の回答は途中の文字が残っていても全文を返す', () => {
  // 表示途中に次の質問を送った場合
  assert.equal(resolveAssistantDisplayText('ai-1', FULL, 'ai-2', { 'ai-1': 'KE-LG', 'ai-2': '' }), FULL);
});

test('全文が空・未定義でも例外にならない', () => {
  assert.equal(resolveAssistantDisplayText('ai-1', '', null, {}), '');
  assert.equal(resolveAssistantDisplayText('ai-1', undefined, null, undefined), '');
});
