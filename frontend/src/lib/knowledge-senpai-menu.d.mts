export function attachMenuDismissal(
  target: Pick<Document, 'addEventListener' | 'removeEventListener'>,
  close: () => void,
): () => void;
