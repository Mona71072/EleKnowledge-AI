// チャット回答の表示本文を決める（純粋関数）。
// タイプライター表示の途中の文字は、そのメッセージを表示中のときだけ使う。
// 表示中でなければ常に全文を返す。初回送信後の会話再読込とタイプライターのタイマーが
// 競合して途中の文字が残っても、全文が表示されるようにするため（管理者向け確認表 D8）。

/**
 * アシスタント回答として画面に出す本文を返す。
 * @param {string} messageId 表示するメッセージの ID
 * @param {string} fullText 回答の全文
 * @param {string | null} streamingMessageId タイプライター表示中のメッセージ ID（なければ null）
 * @param {Record<string, string>} streamingMessages タイプライターで表示済みの途中の文字
 * @returns {string}
 */
export function resolveAssistantDisplayText(messageId, fullText, streamingMessageId, streamingMessages) {
  if (streamingMessageId && streamingMessageId === messageId) {
    return (streamingMessages && streamingMessages[messageId]) || '';
  }
  return fullText || '';
}
