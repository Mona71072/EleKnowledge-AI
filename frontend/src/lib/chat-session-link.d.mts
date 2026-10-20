export type ChatSessionMode = 'normal' | 'law';

export declare function resolveInitialChatMode(search: string | null | undefined): ChatSessionMode;

export declare function buildChatSessionHref(
  sessionId: string,
  ragMode?: 'normal' | 'spec' | 'law' | null,
): string;
