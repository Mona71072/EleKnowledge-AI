// 画面の DOM 操作のうち、判断だけを取り出した小さな補助関数（テストしやすいように分けている）。

/**
 * 入力欄が「入力できない」から「入力できる」に戻ったとき、入力欄へフォーカスを戻すか。
 * 無効化の間にフォーカスが外れた（body など）ときだけ戻し、利用者が別の場所に移したフォーカスは奪わない。
 *
 * @param {{wasDisabled: boolean, disabled: boolean, activeElement: unknown, body: unknown}} state
 */
export function shouldRestoreComposerFocus({ wasDisabled, disabled, activeElement, body }) {
  return Boolean(wasDisabled) && !disabled && (!activeElement || activeElement === body);
}

/**
 * 要素の祖先の <details> を開く。閉じた <details> の中にある出典へ、アンカーで移動できるようにする。
 *
 * @param {{parentElement?: any} | null | undefined} element
 */
export function openAncestorDetails(element) {
  let opened = 0;
  let details = element?.parentElement?.closest?.('details') ?? null;
  while (details) {
    if (!details.open) { details.open = true; opened += 1; }
    details = details.parentElement?.closest?.('details') ?? null;
  }
  return opened;
}
