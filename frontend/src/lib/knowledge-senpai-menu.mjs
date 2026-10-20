
/**
 * ⋯メニューを、メニューの外側の押下・外側へのフォーカス移動・Escape キーで閉じる。
 * 返す関数でリスナーを外す。メニューの要素には `data-senpai-menu` を付けておく。
 * `close` には閉じた理由（'outside' | 'focus' | 'escape'）が渡る。
 *
 * @param {{addEventListener: Function, removeEventListener: Function}} target 通常は document
 * @param {(reason: 'outside' | 'focus' | 'escape') => void} close
 * @returns {() => void}
 */
export function attachMenuDismissal(target, close) {
  const outside = (event) => {
    const element = event?.target;
    return !element || typeof element.closest !== 'function' || !element.closest('[data-senpai-menu]');
  };
  const onPointerDown = (event) => { if (outside(event)) close('outside'); };
  const onFocusIn = (event) => { if (outside(event)) close('focus'); };
  const onKeyDown = (event) => { if (event?.key === 'Escape') close('escape'); };
  target.addEventListener('pointerdown', onPointerDown);
  target.addEventListener('focusin', onFocusIn);
  target.addEventListener('keydown', onKeyDown);
  return () => {
    target.removeEventListener('pointerdown', onPointerDown);
    target.removeEventListener('focusin', onFocusIn);
    target.removeEventListener('keydown', onKeyDown);
  };
}
