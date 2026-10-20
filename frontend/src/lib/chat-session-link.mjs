// チャット画面へのセッションリンクと、URL からの初期モード判定（純粋関数）。
// 法令モードのセッションは mode=law を付けないと API が 409 SessionModeMismatch を返すため、
// リンク生成側と受け取り側で同じ規則を使う。

/** URL クエリの mode から初期モードを決める。law 以外は normal。 */
export function resolveInitialChatMode(search) {
  const params = new URLSearchParams(search || '');
  return params.get('mode') === 'law' ? 'law' : 'normal';
}

/** 管理画面からチャットでセッションを開くリンク。法令モードのときだけ mode=law を付ける。 */
export function buildChatSessionHref(sessionId, ragMode) {
  const base = `/chat?session=${encodeURIComponent(sessionId)}`;
  return ragMode === 'law' ? `${base}&mode=law` : base;
}
