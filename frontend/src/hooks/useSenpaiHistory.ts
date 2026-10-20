'use client';

import { useEffect, useRef, useState } from 'react';
import { getIdToken } from '@/lib/auth-helpers';
import { getSenpaiConversations, readSenpaiConversation, type SenpaiConversationSummary } from '@/lib/knowledge-senpai-history.mjs';
import type { SenpaiChatController, SenpaiChatSnapshot } from '@/lib/knowledge-senpai-chat.mjs';

type ControllerRef = { current: SenpaiChatController | null };
export type SenpaiHistoryEntry = SenpaiConversationSummary & { pending?: boolean };

function safeMessage(error: unknown, fallback: string) {
  const known = error as { code?: string; message?: string } | null;
  return known?.code && known.message ? known.message : fallback;
}

/** Server-owned histories; only the active consultation remains in browser memory. */
export function useSenpaiHistory(snapshot: SenpaiChatSnapshot, controllerRef: ControllerRef) {
  const [sessions, setSessions] = useState<SenpaiConversationSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [complete, setComplete] = useState(true);
  const [opening, setOpening] = useState(false);
  const [openError, setOpenError] = useState('');
  const [revision, setRevision] = useState(0);
  const mounted = useRef(false);
  const sequence = useRef(0);
  const detailRequest = useRef<AbortController | null>(null);
  const wasRunning = useRef(false);
  const openRef = useRef<(id: string) => Promise<void>>(async () => {});

  function resetSelection() {
    sequence.current += 1;
    detailRequest.current?.abort();
    detailRequest.current = null;
    setOpening(false);
    setOpenError('');
    window.history.replaceState(null, '', '/knowledge/chat');
  }

  async function openConversation(conversationId: string) {
    const current = ++sequence.current;
    detailRequest.current?.abort();
    const request = new AbortController();
    detailRequest.current = request;
    controllerRef.current?.cancel();
    setOpening(true);
    setOpenError('');
    try {
      const saved = await readSenpaiConversation({
        baseUrl: process.env.NEXT_PUBLIC_CHAT_API_URL || '', getToken: getIdToken,
        conversationId, signal: request.signal,
      });
      if (!mounted.current || current !== sequence.current || request.signal.aborted) return;
      if (!controllerRef.current) throw new Error('Controller unavailable');
      controllerRef.current.restore(saved);
      window.history.replaceState(null, '', `/knowledge/chat?conversation=${encodeURIComponent(conversationId)}`);
    } catch (cause) {
      if (mounted.current && current === sequence.current && !request.signal.aborted) {
        setOpenError(safeMessage(cause, '相談履歴を開けませんでした。もう一度選択してください。'));
      }
    } finally {
      if (mounted.current && current === sequence.current) setOpening(false);
    }
  }
  useEffect(() => { openRef.current = openConversation; });

  useEffect(() => {
    mounted.current = true;
    const conversationId = new URLSearchParams(window.location.search).get('conversation');
    if (conversationId) void openRef.current(conversationId);
    return () => {
      mounted.current = false;
      sequence.current += 1;
      detailRequest.current?.abort();
    };
  }, []);

  useEffect(() => {
    const request = new AbortController();
    let current = true;
    setLoading(true);
    setError('');
    getSenpaiConversations({
      baseUrl: process.env.NEXT_PUBLIC_CHAT_API_URL || '', getToken: getIdToken, signal: request.signal,
    }).then((result) => {
      if (!current) return;
      setSessions(result.sessions);
      setComplete(result.complete);
    }).catch((cause) => {
      if (current) setError(safeMessage(cause, '相談履歴を取得できませんでした。再試行してください。'));
    }).finally(() => {
      if (current) setLoading(false);
    });
    return () => { current = false; request.abort(); };
  }, [revision]);

  useEffect(() => {
    if (wasRunning.current && !snapshot.running) setRevision((value) => value + 1);
    wasRunning.current = snapshot.running;
    if (snapshot.conversationId && snapshot.running) {
      window.history.replaceState(null, '', `/knowledge/chat?conversation=${encodeURIComponent(snapshot.conversationId)}`);
    }
  }, [snapshot.running, snapshot.conversationId]);

  const active = snapshot.conversationId;
  const stored = sessions.find((session) => session.conversationId === active);
  const entries: SenpaiHistoryEntry[] = [...sessions];
  if (active && snapshot.turns.length > 0 && (snapshot.running || !stored)) {
    const now = new Date().toISOString();
    const current: SenpaiHistoryEntry = {
      conversationId: active, title: snapshot.turns[0].query.slice(0, 50),
      createdAt: stored?.createdAt || now, lastMessageTime: now,
      messageCount: snapshot.turns.length, daysUntilDeletion: stored?.daysUntilDeletion ?? 60,
      pending: true,
    };
    entries.splice(0, entries.length, current, ...entries.filter((entry) => entry.conversationId !== active));
  }

  return {
    entries, loading, error, complete, opening, openError,
    openConversation, resetSelection, refresh: () => setRevision((value) => value + 1),
  };
}
