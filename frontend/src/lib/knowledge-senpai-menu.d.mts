export type MenuDismissReason = 'outside' | 'focus' | 'escape';
export function attachMenuDismissal(
  target: Pick<Document, 'addEventListener' | 'removeEventListener'>,
  close: (reason: MenuDismissReason) => void,
): () => void;
