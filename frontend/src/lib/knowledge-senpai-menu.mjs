/**
 * ⋯メニューを、メニューの外側の押下と Escape キーで閉じる。
 * 返す関数でリスナーを外す。メニューの要素には `data-senpai-menu` を付けておく。
 *
 * @param {{addEventListener: Function, removeEventListener: Function}} target 通常は document
 * @param {() => void} close
 * @returns {() => void}
 */
export function attachMenuDismissal(target, close) {
  const onPointerDown = (event) => {
    const element = event?.target;
    if (!element || typeof element.closest !== 'function' || !element.closest('[data-senpai-menu]')) close();
  };
  const onKeyDown = (event) => { if (event?.key === 'Escape') close(); };
  target.addEventListener('pointerdown', onPointerDown);
  target.addEventListener('keydown', onKeyDown);
  return () => {
    target.removeEventListener('pointerdown', onPointerDown);
    target.removeEventListener('keydown', onKeyDown);
  };
}
