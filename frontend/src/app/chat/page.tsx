'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { getCurrentUser, fetchAuthSession } from 'aws-amplify/auth';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { Components } from 'react-markdown';
import { Chip } from '@/components/ui';
import { Toast } from '@/components/ui/Toast';
import { ChatMessageFeedback } from '@/components/chat/ChatMessageFeedback';
import { ProductWishModal } from '@/components/chat/ProductWishModal';
import { ALL_MODEL_TYPES } from '@/data/kbModelTypes';
import { documentHref, documentHrefWithPage } from '@/lib/documents';
import {
  BadFeedbackReasonId,
  FEEDBACK_COMMENT_MAX,
  PRODUCT_WISH_TEXT_MAX,
  submitProductWish,
} from '@/lib/chat-failures';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  citations?: string[];
  responseType?: 'clarify' | 'pages' | 'not_found';
  clarifyQuestions?: string[];
  pageCandidates?: Array<{
    documentName: string;
    category?: string;
    modelType?: string;
    pageNumber?: number;
    sourceUri: string;
    relevance: number;
    snippet?: string | null;
    lowConfidence?: boolean;
  }>;
  sourceDocuments?: Array<{
    documentName: string;
    title?: string;  // メタデータタイトル（オプション）
    sourceUri: string;
    category: string;    // Knowledge Base の実メタデータ category（例: C資料 / 据付場用図）
    modelType: string;   // 同 model_type（カンマ連結の多値文字列）
    hasImage?: boolean;  // 該当チャンクが図面などの画像だった場合 true
    pageNumber?: number;
    relevance: number;
    lawCitation?: {
      lawId: string;
      lawTitle: string;
      lawNumber: string;
      effectiveDate: string;
      provisionType: string;
      provisionReference?: string;
      sourceUrl: string;
    };
  }>;
  feedback?: 'good' | 'bad' | null;
  /** 新規: wrong_doc | unresolved | bad_answer | other。wrong_page は旧データ表示用 */
  feedbackReason?: 'wrong_doc' | 'unresolved' | 'bad_answer' | 'other' | 'wrong_page' | null;
  feedbackComment?: string | null;
}

interface ToastState {
  message: string;
  variant: 'success' | 'error' | 'info';
}

interface Session {
  sessionId: string;
  title: string;
  createdAt: string;
  lastMessageTime: string;
  messageCount: number;
  daysUntilDeletion: number;
  ragMode?: ChatMode;
}

type ChatMode = 'normal' | 'law';

export default function ChatPage() {
  const router = useRouter();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [ragMode, setRagMode] = useState<ChatMode>('normal');
  const [currentSession, setCurrentSession] = useState<string | null>(null);
  // admin が失敗一覧から他ユーザーのセッションを開いたとき true（閲覧のみ・送信不可）
  const [readOnlySession, setReadOnlySession] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [streamingMessages, setStreamingMessages] = useState<Record<string, string>>({});
  const [streamingMessageId, setStreamingMessageId] = useState<string | null>(null);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [userId, setUserId] = useState<string | null>(null);
  const [isLoadingSessions, setIsLoadingSessions] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [showScrollButton, setShowScrollButton] = useState(false);
  const [showAllCitations, setShowAllCitations] = useState<Record<string, boolean>>({});
  // 資料カテゴリは複数選択。未選択＝全資料検索。
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  // 機種は UI_MODEL_FILTERS の項目を単一選択（サーバー側で要素完全一致に展開）。
  const [selectedModel, setSelectedModel] = useState('');
  const [filtersOpen, setFiltersOpen] = useState(false);
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null);
  // 👎 直後に理由ワンタップを出す対象（必須にしない＝スキップ可）
  const [pendingBadMessageId, setPendingBadMessageId] = useState<string | null>(null);
  const [pendingBadComment, setPendingBadComment] = useState('');
  const [feedbackBusyIds, setFeedbackBusyIds] = useState<Record<string, true>>({});
  const [toast, setToast] = useState<ToastState | null>(null);
  const [wishOpen, setWishOpen] = useState(false);
  const [wishText, setWishText] = useState('');
  const [wishSubmitting, setWishSubmitting] = useState(false);
  const [wishSent, setWishSent] = useState(false);
  const [wishError, setWishError] = useState<string | null>(null);
  const isLawMode = ragMode === 'law';

  // value は Knowledge Base の実 category 値に対応する安定キー
  // 並び: 本命（C / TI / 据付基準）を先に、その他は後。
  const categoryOptions = [
    { value: 'spec', label: 'C資料' },
    { value: 'tech_info', label: 'TI' },
    { value: 'std', label: '据付基準' },
    { value: 'drawing', label: '据付場用図' },
    { value: 'incident', label: '災害事例集' },
    { value: 'qsheet', label: 'Qシート' },
    { value: 'note', label: '据付ノート' },
    { value: 'site_agent', label: '現場代理人業務マニュアル' },
    { value: 'quality_mgmt', label: '品質管理業務マニュアル' },
    // w_doc(W資料) は実機確認 2026-08-26 で選択時0件（全5件が取扱機種スコープ対象外）のため
    // 業務判断（HANDLED追加 or スコープ例外化）が出るまで非掲載。API上は有効なキー。
  ];

  const selectedModelOption =
    ALL_MODEL_TYPES.find((o) => o.value === selectedModel) || null;
  const selectedModelLabel = selectedModelOption?.label || selectedModel;

  const API_URL = process.env.NEXT_PUBLIC_RAG_API_URL || '';
  const CHAT_API_URL = process.env.NEXT_PUBLIC_CHAT_API_URL || '';

  // 空状態のクリック可能な質問サジェスト（ホーム画面のチップと同一）
const SUGGESTED_QUESTIONS = [
  'KE-LG の据付で注意すべきポイントは？',
  '異音が出るときに最初に確認する項目は？',
  'エラーコードの原因と対処を手順で教えて',
];

const LAW_SUGGESTED_QUESTIONS = [
  '昇降機の設置に関係する現行法令を教えて',
  '建築基準法で昇降機の定期検査について定めている条文は？',
  '工事で確認が必要な消防法令の根拠を教えて',
];

const getUniqueDocs = (docs: Message['sourceDocuments'] = []) => {
    const seen = new Set<string>();
    return docs.filter((doc) => {
      const key = doc.lawCitation
        ? `${doc.lawCitation.lawId}:${doc.lawCitation.provisionReference || doc.lawCitation.provisionType}`
        : doc.sourceUri || doc.documentName || '';
      if (!key) return true;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  };

  const markdownComponents: Components = {
    p: ({ children }: any) => <p className="mb-3 last:mb-0 leading-relaxed">{children}</p>,
    h1: ({ children }: any) => <h1 className="text-xl font-bold mb-3 mt-3 first:mt-0">{children}</h1>,
    h2: ({ children }: any) => <h2 className="text-lg font-bold mb-2 mt-3 first:mt-0">{children}</h2>,
    h3: ({ children }: any) => <h3 className="text-base font-semibold mb-2 mt-2 first:mt-0">{children}</h3>,
    ul: ({ children }: any) => <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>,
    ol: ({ children }: any) => <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>,
    li: ({ children }: any) => <li className="ml-2">{children}</li>,
    code: ({ children, className, ...props }: any) => {
      const isInline = !className;
      if (isInline) {
        return <code className="bg-gray-100 px-1.5 py-0.5 rounded text-sm font-mono text-blue-600" {...props}>{children}</code>;
      }
      return <code className="block bg-gray-900 text-gray-100 p-3 rounded-lg text-sm font-mono overflow-x-auto mb-3" {...props}>{children}</code>;
    },
    pre: ({ children }: any) => {
      const child = children as any;
      if (child?.props?.className?.includes('language-')) {
        return <pre className="bg-gray-900 text-gray-100 p-3 rounded-lg overflow-x-auto mb-3">{children}</pre>;
      }
      return <pre className="bg-gray-100 p-3 rounded-lg overflow-x-auto mb-3">{children}</pre>;
    },
    blockquote: ({ children }: any) => <blockquote className="border-l-4 border-blue-500 pl-4 italic my-3 text-gray-600">{children}</blockquote>,
    a: ({ href, children }: any) => <a href={href} className="text-blue-600 hover:text-blue-700 underline" target="_blank" rel="noopener noreferrer">{children}</a>,
    strong: ({ children }: any) => <strong className="font-semibold">{children}</strong>,
    em: ({ children }: any) => <em className="italic">{children}</em>,
    // テーブル関連コンポーネント（グラフ・図表を綺麗に表示）
    table: ({ children }: any) => (
      <div className="overflow-x-auto my-6 rounded-xl border border-gray-200 shadow-lg bg-white">
        <table className="min-w-full border-collapse">
          {children}
        </table>
      </div>
    ),
    thead: ({ children }: any) => (
      <thead className="bg-gradient-to-r from-blue-50 to-indigo-50 border-b-2 border-blue-200">{children}</thead>
    ),
    tbody: ({ children }: any) => (
      <tbody className="bg-white [&>tr:nth-child(even)]:bg-gray-50">{children}</tbody>
    ),
    tr: ({ children }: any) => (
      <tr className="hover:bg-blue-100 hover:shadow-sm transition-all duration-150 border-b border-gray-200 last:border-b-0">{children}</tr>
    ),
    th: ({ children }: any) => (
      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-800 uppercase tracking-wider bg-gradient-to-r from-blue-50 to-indigo-50 border-r border-blue-200 last:border-r-0 whitespace-nowrap">{children}</th>
    ),
    td: ({ children }: any) => (
      <td className="px-6 py-4 text-sm text-gray-700 border-r border-gray-200 last:border-r-0 align-top leading-relaxed">{children}</td>
    ),
    // 画像コンポーネント
    img: ({ src, alt, ...props }: any) => (
      <img 
        src={src} 
        alt={alt || ''} 
        className="max-w-full h-auto rounded-lg shadow-md my-4 border border-gray-200" 
        {...props} 
      />
    ),
  };

// Markdownテーブルの崩れを自動補正するユーティリティ
const normalizeTableMarkdown = (text: string): string => {
  if (!text) return text;

  let normalized = text;

  // パターン1: ヘッダー行と区切り行が同一行にある場合
  // 例: | A | B | C | |---|---| -> | A | B | C |\n|---|---|---|
  normalized = normalized.replace(
    /(\|(?:[^\n|]+\|)+)\s*\|\s*(-{2,}[^|]*\|(?:\s*-{2,}[^|]*\|)*)/g,
    (_match, header) => {
      const cols = header.split("|").filter((c: string) => c.trim()).length;
      const separator = Array(cols).fill("---").join(" | ");
      return `${header.trim()}\n| ${separator} |`;
    }
  );

  // パターン2: 区切り行とデータ行が同一行にある場合
  // 例: |---|---| | データ1 | 値1 | 値2 | -> |---|---|\n| データ1 | 値1 | 値2 |
  normalized = normalized.replace(
    /(\|\s*-{2,}[^|]*\|(?:\s*-{2,}[^|]*\|)*)\s+(\|(?:[^\n|]+\|)+)/g,
    (_match, sep, dataRow) => `${sep.trim()}\n${dataRow.trim()}`
  );

  // パターン3: データ行が同一行に詰まっている場合
  // 例: | A | B | C | | D | E | F | -> | A | B | C |\n| D | E | F |
  normalized = normalized.replace(
    /(\|(?:[^\n|]+\|)+)\s+(?=\|(?:[^\n|]+\|)+)/g,
    (_match, row) => `${row.trim()}\n`
  );

  // 余分な連続改行を整理
  normalized = normalized.replace(/\n{3,}/g, "\n\n");

  return normalized;
};

  // 認可トークン取得関数
  const getAuthToken = async (): Promise<string | null> => {
    try {
      const session = await fetchAuthSession();
      return session.tokens?.idToken?.toString() || null;
    } catch (err) {
      console.error('Error fetching auth token:', err);
      return null;
    }
  };

  // 初期化：ユーザー情報取得とセッション読み込み
  useEffect(() => {
    const initializeChat = async () => {
      const requestedMode = new URLSearchParams(window.location.search).get('mode');
      const initialMode: ChatMode = requestedMode === 'law' ? 'law' : 'normal';
      setRagMode(initialMode);

      // 開発モード: 認証をスキップする場合
      const skipAuth = process.env.NEXT_PUBLIC_SKIP_AUTH === 'true';
      const canBypassAuth = skipAuth && process.env.NODE_ENV !== 'production';

      if (skipAuth && !canBypassAuth) {
        console.warn('[ChatPage] NEXT_PUBLIC_SKIP_AUTH is enabled, but bypass is disabled in production.');
      }

      if (canBypassAuth) {
        // モックユーザーIDを設定
        const mockUserId = 'dev-user-123';
        setUserId(mockUserId);
        // セッション取得はスキップ（APIが利用できないため）
        setIsLoadingSessions(false);
        setSessions([]);
        return;
      }

      try {
        const user = await getCurrentUser();
        const subId = user.userId;
        setUserId(subId);

        // セッション一覧を取得
        await fetchSessions(initialMode);
      } catch (err) {
        console.error('Initialize error:', err);
        router.push('/login');
      }
    };

    initializeChat();
  }, [router]);

  // ホームのクイック質問 (?q=...) と失敗一覧からのセッション (?session=...)
  useEffect(() => {
    if (!userId) return;
    const params = new URLSearchParams(window.location.search);
    const initialMode: ChatMode = params.get('mode') === 'law' ? 'law' : 'normal';
    setRagMode(initialMode);
    const q = params.get('q');
    const sessionId = params.get('session');
    let dirty = false;
    if (q) {
      setInput(q);
      dirty = true;
      setTimeout(() => textareaRef.current?.focus(), 100);
    }
    if (sessionId) {
      dirty = true;
      fetchSessionMessages(sessionId).catch((err) => {
        console.error('Failed to open session from URL:', err);
        setError('指定されたセッションを開けませんでした');
      });
    }
    if (dirty) {
      // URL からクエリを除去してリロード時の再適用を防ぐ
      window.history.replaceState(
        {},
        '',
        initialMode === 'law' ? `${window.location.pathname}?mode=law` : window.location.pathname,
      );
    }
  }, [userId]);

  // タイプライター効果の実装
  useEffect(() => {
    if (!streamingMessageId) return;

    const message = messages.find(m => m.id === streamingMessageId);
    if (!message || message.role !== 'assistant') return;

    const fullText = message.content;
    const currentText = streamingMessages[streamingMessageId] || '';

    if (currentText.length >= fullText.length) {
      // タイプライター効果完了
      setStreamingMessageId(null);
      return;
    }

    // 文字を追加（日本語の場合は2文字ずつ、英語の場合は5文字ずつ）
    const isJapanese = /[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]/.test(fullText[currentText.length] || '');
    const chunkSize = isJapanese ? 2 : 5;
    const nextText = fullText.slice(0, currentText.length + chunkSize);

    const timer = setTimeout(() => {
      setStreamingMessages(prev => ({
        ...prev,
        [streamingMessageId]: nextText
      }));
    }, isJapanese ? 30 : 20); // 日本語は少し遅めに

    return () => clearTimeout(timer);
  }, [streamingMessages, streamingMessageId, messages]);

  // メッセージ自動スクロール（最適化）
  useEffect(() => {
    if (messagesEndRef.current && messagesContainerRef.current) {
      const timer = setTimeout(() => {
        const container = messagesContainerRef.current;
        if (container) {
          const isNearBottom = container.scrollHeight - container.scrollTop - container.clientHeight < 200;
          if (isNearBottom || loading) {
            messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
            setShowScrollButton(false);
          }
        }
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [messages, loading, streamingMessages]);

  // スクロール位置を監視してスクロールボタンの表示を制御
  useEffect(() => {
    const container = messagesContainerRef.current;
    if (!container) return;

    const handleScroll = () => {
      const isNearBottom = container.scrollHeight - container.scrollTop - container.clientHeight < 200;
      setShowScrollButton(!isNearBottom && messages.length > 0);
    };

    container.addEventListener('scroll', handleScroll);
    handleScroll(); // 初期状態をチェック

    return () => container.removeEventListener('scroll', handleScroll);
  }, [messages.length]);

  // 最新の会話にスクロール
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
    setShowScrollButton(false);
  };

  const fetchSessions = async (mode: ChatMode = ragMode) => {
    try {
      setIsLoadingSessions(true);
      const token = await getAuthToken();
      
      // userId はサーバー側で ID トークンのクレームから決まるため送らない
      const response = await axios.get(`${CHAT_API_URL}/chat/sessions`, {
        params: { mode },
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      setSessions(response.data.sessions || []);
    } catch (err: any) {
      // err.config は headers.Authorization（ID トークン）を含むためログに出さない
      console.error('Error fetching sessions:', {
        message: err.message,
        status: err.response?.status,
        statusText: err.response?.statusText,
        data: err.response?.data
      });
      setError(`セッション取得に失敗しました: ${err.response?.status || err.message}`);
    } finally {
      setIsLoadingSessions(false);
    }
  };

  const fetchSessionMessages = async (sessionId: string, mode: ChatMode = ragMode) => {
    try {
      const token = await getAuthToken();
      const response = await axios.get(`${CHAT_API_URL}/chat/sessions/${sessionId}/messages`, {
        params: { mode },
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      const fetchedMessages = response.data.messages || [];
      const normalizedMessages = fetchedMessages.map((msg: any, idx: number) => ({
        ...msg,
        id: msg.id || msg.messageId || `msg-${sessionId}-${idx}-${Date.now()}`
      }));
      setMessages(normalizedMessages);
      
      // 既存のメッセージはタイプライター効果なしで表示
      const completedMessages: Record<string, string> = {};
      normalizedMessages.forEach((msg: Message) => {
        if (msg.role === 'assistant') {
          completedMessages[msg.id] = msg.content;
        }
      });
      setStreamingMessages(completedMessages);
      setStreamingMessageId(null);

      setCurrentSession(sessionId);
      setReadOnlySession(Boolean(response.data.readOnly));
    } catch (err) {
      console.error('Error fetching messages:', err);
      setError('メッセージ取得に失敗しました');
    }
  };

  const handleSendMessage = async () => {
    if (!input.trim() || loading || !userId || readOnlySession) return;

    const userMessage: Message = {
      id: `msg_${Date.now()}`,
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };

    // ローカル UI 更新
    setMessages([...messages, userMessage]);
    setInput('');
    // textareaの高さをリセット
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = '42px';
    }
    setLoading(true);
    setError('');

    try {
      const token = await getAuthToken();
      const effectiveFilters = isLawMode ? {} : {
        category: selectedCategories.length > 0 ? selectedCategories : undefined,
        modelType: selectedModel || undefined,
      };

      const payload = {
        sessionId: currentSession,
        userId: userId,
        query: input,
        mode: ragMode,
        filters: effectiveFilters
      };
      
      const response = await axios.post(`${API_URL}/rag/query`, payload, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      const aiId = response.data.aiMessageId || response.data.messageId || `msg-ai-${Date.now()}`;
      const aiMessage: Message = {
        id: aiId,
        role: 'assistant',
        content: response.data.content,
        timestamp: response.data.timestamp,
        citations: response.data.citations,
        responseType: response.data.responseType,
        clarifyQuestions: response.data.clarifyQuestions,
        pageCandidates: response.data.pageCandidates,
        sourceDocuments: response.data.sourceDocuments
      };

      setMessages(prev => [...prev, aiMessage]);

      // clarify / not_found は定型文なのでタイプライター不要（意図: 候補・聞き返しをすぐ読ませる）
      if (response.data.responseType === 'clarify' || response.data.responseType === 'not_found') {
        setStreamingMessageId(null);
      } else {
        setStreamingMessageId(aiId);
        setStreamingMessages(prev => ({
          ...prev,
          [aiId]: ''
        }));
      }

      // 新規セッションの場合はセッション一覧を更新
      if (!currentSession && response.data.sessionId) {
        setCurrentSession(response.data.sessionId);
        await fetchSessions(ragMode);
        await fetchSessionMessages(response.data.sessionId, ragMode);
      }
    } catch (err: any) {
      // err.config は headers.Authorization（ID トークン）を含むためログに出さない
      console.error('Error sending RAG query:', {
        message: err.message,
        status: err.response?.status,
        statusText: err.response?.statusText,
        data: err.response?.data,
        url: err.config?.url
      });
      setError(`エラーが発生しました: ${err.response?.data?.message || err.message || 'Unknown error'}`);
      // ユーザーメッセージは残す
    } finally {
      setLoading(false);
    }
  };

  const handleNewSession = () => {
    setCurrentSession(null);
    setReadOnlySession(false);
    setMessages([]);
    setStreamingMessages({});
    setStreamingMessageId(null);
    setInput('');
    setError('');
  };

  const handleDeleteSession = async (sessionId: string) => {
    if (!window.confirm('このセッションを削除しますか？')) return;

    try {
      const token = await getAuthToken();
      await axios.delete(`${CHAT_API_URL}/chat/sessions/${sessionId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      setSessions(sessions.filter(s => s.sessionId !== sessionId));
      if (currentSession === sessionId) {
        handleNewSession();
      }
    } catch (err) {
      setError('セッション削除に失敗しました');
    }
  };

  const handleCopyMessage = async (messageId: string, content: string) => {
    try {
      await navigator.clipboard.writeText(content);
      setCopiedMessageId(messageId);
      setTimeout(() => setCopiedMessageId(null), 2000);
    } catch (err) {
      console.error('Copy failed:', err);
    }
  };

  const handleSuggestedQuestion = (q: string) => {
    setInput(q);
    setTimeout(() => textareaRef.current?.focus(), 50);
  };

  const handleFeedback = async (
    messageId: string,
    feedback: 'good' | 'bad',
    reason?: BadFeedbackReasonId,
    comment?: string,
  ) => {
    if (!currentSession || feedbackBusyIds[messageId]) return;

    const previous = messages.find((m) => m.id === messageId);
    const trimmedComment = comment?.trim().slice(0, FEEDBACK_COMMENT_MAX);

    setFeedbackBusyIds((prev) => ({ ...prev, [messageId]: true }));
    setMessages((prev) => prev.map((m) =>
      m.id === messageId
        ? {
            ...m,
            feedback,
            feedbackReason: feedback === 'bad' ? (reason || m.feedbackReason || null) : null,
            feedbackComment:
              feedback === 'good'
                ? null
                : trimmedComment
                  ? trimmedComment
                  : m.feedbackComment,
          }
        : m
    ));

    if (feedback === 'good') {
      setPendingBadMessageId(null);
      setPendingBadComment('');
    } else if (!reason && !trimmedComment) {
      setPendingBadMessageId(messageId);
      setPendingBadComment('');
    } else if (trimmedComment) {
      setPendingBadMessageId(null);
      setPendingBadComment('');
    }

    try {
      const token = await getAuthToken();
      const body: Record<string, string> = {
        sessionId: currentSession,
        feedback,
      };
      if (feedback === 'bad' && reason) {
        body.reason = reason;
      }
      if (feedback === 'bad' && trimmedComment) {
        body.comment = trimmedComment;
      }
      await axios.put(`${CHAT_API_URL}/chat/messages/${messageId}/feedback`, body, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      // 👎 初回タップはパネル誘導だけでトーストしない（うるささ防止）
      if (feedback === 'good') {
        setToast({ message: 'ありがとうございます。評価を記録しました。', variant: 'success' });
      } else if (trimmedComment) {
        setToast({ message: '補足を記録しました。', variant: 'success' });
      } else if (reason) {
        setToast({ message: '理由を記録しました。補足があれば続けて書けます。', variant: 'info' });
      }
    } catch (err) {
      console.error('Error submitting feedback:', err);
      if (previous) {
        setMessages((prev) => prev.map((m) => (m.id === messageId ? previous : m)));
      }
      if (feedback === 'bad' && !reason && !trimmedComment) {
        setPendingBadMessageId(null);
      }
      setToast({ message: '評価の送信に失敗しました。もう一度お試しください。', variant: 'error' });
    } finally {
      setFeedbackBusyIds((prev) => {
        const next = { ...prev };
        delete next[messageId];
        return next;
      });
    }
  };

  const handleBadReason = async (messageId: string, reason: BadFeedbackReasonId) => {
    await handleFeedback(messageId, 'bad', reason, pendingBadComment);
  };

  const handleBadCommentOnly = async (messageId: string) => {
    if (!pendingBadComment.trim()) return;
    await handleFeedback(messageId, 'bad', undefined, pendingBadComment);
  };

  const openBadReasonPanel = (messageId: string, existingComment?: string | null) => {
    setPendingBadMessageId(messageId);
    setPendingBadComment(existingComment || '');
  };

  const handleSubmitWish = async () => {
    const text = wishText.trim();
    if (!text || wishSubmitting) return;
    if (text.length > PRODUCT_WISH_TEXT_MAX) {
      setWishError(`要望は ${PRODUCT_WISH_TEXT_MAX} 文字以内で入力してください`);
      return;
    }
    setWishSubmitting(true);
    setWishError(null);
    try {
      await submitProductWish(text, currentSession);
      setWishText('');
      setWishSent(true);
      setToast({ message: '要望を送信しました。ありがとうございます。', variant: 'success' });
      window.setTimeout(() => {
        setWishOpen(false);
        setWishSent(false);
      }, 1800);
    } catch (err) {
      console.error('wish submit failed', err);
      setWishError('要望の送信に失敗しました。もう一度お試しください。');
    } finally {
      setWishSubmitting(false);
    }
  };

  const openWishModal = () => {
    setWishError(null);
    setWishSent(false);
    setWishOpen(true);
  };

  return (
    <div className="h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-4 sm:px-6 py-2 flex justify-between items-center flex-shrink-0 shadow-sm backdrop-blur-sm bg-white/95">
        <div className="flex items-center gap-2.5">
          {/* Mobile Menu Button */}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="md:hidden p-1.5 rounded-lg text-gray-600 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
            aria-label="メニューを開く"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <div className="flex items-center gap-1.5">
            <div className="w-7 h-7 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
              <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
            <div>
              <h1 className="text-lg sm:text-xl font-bold text-gray-900 leading-tight">EleKnowledge</h1>
              <span className="hidden sm:inline-block text-[10px] text-gray-500 mt-0 leading-tight">
                {isLawMode ? '法令チャット' : 'RAGチャット'}
              </span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {isLawMode && (
            <span className="inline-flex items-center rounded-full border border-amber-300 bg-amber-50 px-2.5 py-1 text-xs font-semibold text-amber-900">
              プレリリース
            </span>
          )}
          <button
            type="button"
            onClick={openWishModal}
            className="inline-flex items-center gap-1 px-2.5 py-1.5 border border-violet-200 rounded-lg text-xs sm:text-sm font-medium text-violet-800 bg-violet-50 hover:bg-violet-100 transition-colors"
          >
            こうなってほしい
          </button>
          <Link
            href="/"
            className="inline-flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 border border-gray-300 rounded-lg text-xs sm:text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
          >
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
          <span className="hidden sm:inline">ホームへ戻る</span>
          <span className="sm:hidden">ホーム</span>
        </Link>
        </div>
      </div>

      <ProductWishModal
        open={wishOpen}
        text={wishText}
        submitting={wishSubmitting}
        sent={wishSent}
        error={wishError}
        onTextChange={setWishText}
        onSubmit={handleSubmitWish}
        onClose={() => {
          setWishOpen(false);
          setWishError(null);
          setWishSent(false);
        }}
      />

      {toast && (
        <Toast
          message={toast.message}
          variant={toast.variant}
          onDismiss={() => setToast(null)}
        />
      )}

      <div className="flex flex-1 overflow-hidden relative h-full">
        {/* Mobile Sidebar Overlay */}
        {sidebarOpen && (
          <div
            className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Sidebar - Session List */}
        <div className={`fixed md:static inset-y-0 left-0 z-50 md:z-auto w-64 bg-white border-r border-gray-200 flex flex-col h-full max-h-full transform transition-transform duration-300 ease-in-out ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}>
          {/* Mobile Sidebar Header */}
          <div className="md:hidden flex items-center justify-between p-4 border-b border-gray-200 flex-shrink-0">
            <h2 className="text-lg font-semibold text-gray-900">メニュー</h2>
            <button
              onClick={() => setSidebarOpen(false)}
              className="p-2 rounded-md text-gray-600 hover:bg-gray-100 focus:outline-none"
              aria-label="メニューを閉じる"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* New Session Button */}
          <div className="flex-shrink-0 p-4 border-b border-gray-200 bg-gradient-to-b from-white to-gray-50">
            <button
              onClick={() => {
                handleNewSession();
                setSidebarOpen(false);
              }}
              className="w-full px-4 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all font-medium text-sm shadow-md hover:shadow-lg transform hover:scale-[1.02] active:scale-[0.98] flex items-center justify-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              新規チャット
            </button>
          </div>

          {/* Session List */}
          <div className="flex-1 overflow-y-auto min-h-0 max-h-full scroll-smooth">
            {isLoadingSessions ? (
              <div className="p-4 text-center text-gray-500">
                読み込み中...
              </div>
            ) : sessions.length === 0 ? (
              <div className="p-4 text-center text-gray-500 text-sm">
                セッションはまだありません
              </div>
            ) : (
              <div className="space-y-0.5 p-1">
                {sessions.map((session, index) => (
                  <div
                    key={session.sessionId}
                    onClick={() => {
                      fetchSessionMessages(session.sessionId);
                      setSidebarOpen(false);
                    }}
                    className={`p-2 rounded-lg cursor-pointer transition-all duration-200 group ${
                      currentSession === session.sessionId
                        ? 'bg-gradient-to-r from-blue-50 to-blue-100/50 border-l-4 border-blue-600 shadow-sm'
                        : 'hover:bg-gray-50 hover:shadow-sm'
                    }`}
                    style={{ animationDelay: `${index * 50}ms` }}
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1 truncate min-w-0">
                        <p className="font-medium text-[13px] text-gray-900 truncate leading-tight">
                          {session.title}
                        </p>
                        <p className="text-[11px] text-gray-500 mt-0 flex items-center gap-1.5">
                          <span>{session.messageCount}件</span>
                          <span className="text-gray-400">・</span>
                          <span className="text-gray-500">残り {session.daysUntilDeletion} 日</span>
                        </p>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteSession(session.sessionId);
                        }}
                        className="opacity-0 group-hover:opacity-100 ml-1.5 text-gray-400 hover:text-red-600 flex-shrink-0 transition-all duration-200 hover:bg-red-50 rounded p-0.5"
                        title="削除"
                        aria-label="セッションを削除"
                      >
                        <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

        </div>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col bg-white relative min-h-0 overflow-hidden">
          {/* Messages Area */}
          <div 
            ref={messagesContainerRef}
            className="flex-1 overflow-y-auto p-2.5 sm:p-4 lg:p-5 min-h-0 max-h-full scroll-smooth"
            style={{ maxHeight: 'calc(100vh - 150px)' }}
          >
            {messages.length === 0 ? (
              <div className="flex items-center justify-center h-full w-full min-w-0">
                <div className="text-center w-full max-w-lg px-4 mx-auto">
                  <div className="mb-5">
                    <div className="w-16 h-16 mx-auto bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-lg">
                      <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                      </svg>
                    </div>
                  </div>
                  <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-2 leading-tight">
                    {isLawMode ? 'どの法令をお調べしますか？' : '何をお調べしますか？'}
                  </h2>
                  <p className="text-gray-500 text-sm sm:text-base mb-6 leading-relaxed">
                    {isLawMode
                      ? '現行法令を検索し、根拠条文とe-Gov原文へのリンクを表示します。'
                      : '技術資料を検索し、参考資料（根拠）つきで回答します'}
                  </p>
                  <div className="space-y-2 text-left">
                    {(isLawMode ? LAW_SUGGESTED_QUESTIONS : SUGGESTED_QUESTIONS).map((q) => (
                      <button
                        key={q}
                        type="button"
                        onClick={() => handleSuggestedQuestion(q)}
                        className="w-full flex items-center gap-3 px-4 py-3 rounded-xl border border-gray-200 bg-white text-sm text-gray-700 hover:border-blue-300 hover:bg-blue-50/50 hover:text-blue-700 transition-colors shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <svg className="w-4 h-4 text-blue-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden>
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                        </svg>
                        <span className="flex-1">{q}</span>
                        <svg className="w-4 h-4 text-gray-300 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden>
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </button>
                    ))}
                  </div>
                  {isLawMode ? (
                    <p className="mt-5 text-xs leading-relaxed text-gray-500">
                      条例・告示・通知や過去時点の適用は、この検索対象に含まれません。
                    </p>
                  ) : (
                    <p className="mt-5 text-xs text-gray-400 leading-relaxed">
                      下の「絞り込み」から資料タイプ・機種を指定すると精度が上がります。
                      <br />
                      回答の下で「解けた / 解けない」を押すと改善に活かせます（理由・補足は任意）。
                    </p>
                  )}
                </div>
              </div>
            ) : (
              <div className="space-y-2.5 max-w-4xl mx-auto w-full px-2 sm:px-3">
              <>
                {messages.map((message, index) => (
                  <div
                    key={message.id}
                    className={`flex min-w-0 animate-fade-in ${
                      message.role === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                    style={{ animationDelay: `${index * 40}ms` }}
                  >
                    <div
                      className={`break-words min-w-0 ${
                        message.role === 'user'
                          ? 'px-4 py-2.5 rounded-2xl rounded-br-md bg-gradient-to-br from-blue-600 to-blue-700 text-white shadow-sm max-w-[85%] sm:max-w-[70%]'
                          : 'px-4 py-3 rounded-2xl rounded-tl-md bg-white border border-gray-200 text-gray-900 shadow-sm max-w-full sm:max-w-[92%]'
                      }`}
                    >
                      {/* Role Indicator (assistant only) */}
                      {message.role === 'assistant' && (
                        <div className="flex items-center gap-1.5 mb-2">
                          <div className="w-6 h-6 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center" aria-hidden>
                            <svg className="w-3.5 h-3.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                            </svg>
                          </div>
                          <span className="text-xs font-semibold text-gray-500">EleKnowledge AI</span>
                        </div>
                      )}

                      <div className="w-full">
                        {message.role === 'assistant' ? (
                          <div className="space-y-3">
                            {/* WHY: 成功定義は該当頁到達。候補を本文より上に出す（design-2026-07-29） */}
                            {message.pageCandidates && message.pageCandidates.length > 0 && (
                              <div className={`rounded-lg border p-3 space-y-2 ${
                                message.responseType === 'not_found' || message.pageCandidates.some((c) => c.lowConfidence)
                                  ? 'border-amber-200 bg-amber-50/60'
                                  : 'border-blue-200 bg-blue-50/60'
                              }`}>
                                <p className={`text-xs font-semibold ${
                                  message.responseType === 'not_found' || message.pageCandidates.some((c) => c.lowConfidence)
                                    ? 'text-amber-900'
                                    : 'text-blue-900'
                                }`}>
                                  {message.responseType === 'not_found' || message.pageCandidates.some((c) => c.lowConfidence)
                                    ? '参考候補（低信頼）'
                                    : '該当頁候補'}
                                </p>
                                <ul className="space-y-2">
                                  {message.pageCandidates.map((c, idx) => (
                                    <li key={`${c.sourceUri}-${idx}`} className="text-sm">
                                      <a
                                        href={documentHrefWithPage(c.sourceUri, c.pageNumber)}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="font-medium text-blue-700 hover:underline"
                                      >
                                        {c.documentName}
                                      </a>
                                      <span className="text-gray-600 text-xs ml-2">
                                        {c.category ? `${c.category} · ` : ''}
                                        {typeof c.pageNumber === 'number' ? `p.${c.pageNumber}` : 'ページ不明'}
                                        {typeof c.relevance === 'number' ? ` · ${Math.round(c.relevance * 100)}%` : ''}
                                        {c.lowConfidence ? ' · 低信頼' : ''}
                                      </span>
                                      {c.snippet ? (
                                        <p className="text-xs text-gray-500 mt-0.5 line-clamp-2">{c.snippet}</p>
                                      ) : null}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {message.responseType === 'clarify' && message.clarifyQuestions && message.clarifyQuestions.length > 0 && (
                              <div className="rounded-lg border border-amber-200 bg-amber-50 p-3">
                                <p className="text-xs font-semibold text-amber-900 mb-1.5">追加で教えてください</p>
                                <div className="flex flex-col gap-1.5">
                                  {message.clarifyQuestions.map((q) => (
                                    <button
                                      key={q}
                                      type="button"
                                      onClick={() => {
                                        setInput((prev) => (prev.trim() ? `${prev.trim()}\n${q}` : q));
                                        setTimeout(() => textareaRef.current?.focus(), 50);
                                      }}
                                      className="text-left text-sm text-amber-950 rounded-md px-2 py-1.5 bg-white/70 hover:bg-white border border-amber-100"
                                    >
                                      {q}
                                    </button>
                                  ))}
                                </div>
                              </div>
                            )}

                            {message.responseType === 'not_found' && (
                              <div className="rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-xs text-gray-600 space-y-2">
                                <p>検索が弱いため断定回答はしていません</p>
                                {selectedCategories.length > 0 && (
                                  <button
                                    type="button"
                                    onClick={() => {
                                      setSelectedCategories([]);
                                      setFiltersOpen(true);
                                    }}
                                    className="text-blue-700 underline underline-offset-2"
                                  >
                                    資料カテゴリの絞り込みを外す
                                  </button>
                                )}
                              </div>
                            )}

                            <div className="chat-markdown text-gray-800 text-[13px] sm:text-[14px]">
                              {streamingMessageId === message.id ? (
                                <>
                                  <ReactMarkdown components={markdownComponents} remarkPlugins={[remarkGfm]}>
                                    {normalizeTableMarkdown(streamingMessages[message.id] || '')}
                                  </ReactMarkdown>
                                  <span className="inline-block w-2 h-5 bg-blue-500 ml-1 animate-pulse" />
                                </>
                              ) : (
                                <ReactMarkdown components={markdownComponents} remarkPlugins={[remarkGfm]}>
                                  {normalizeTableMarkdown(streamingMessages[message.id] || message.content)}
                                </ReactMarkdown>
                              )}
                            </div>
                          </div>
                        ) : (
                          <p className={`whitespace-pre-wrap break-words text-[13px] leading-relaxed font-normal text-white`}>
                            {message.content}
                          </p>
                        )}
                      </div>

                      {isLawMode && message.role === 'assistant' && (
                        <p className="mt-2 text-xs leading-relaxed text-gray-500">
                          法令情報の出典は{' '}
                          <a
                            href="https://laws.e-gov.go.jp/"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:underline"
                          >
                            e-Gov法令検索
                          </a>
                          です。e-Gov XMLをもとにEle-Knowledgeが検索・回答用に加工しています。法的判断の前にリンク先の原文をご確認ください。
                        </p>
                      )}

                      {/* Citations */}
                      {message.role === 'assistant' && message.sourceDocuments && message.sourceDocuments.length > 0 && 
                       (!streamingMessageId || streamingMessageId !== message.id || (streamingMessages[message.id] || '').length >= message.content.length) && (() => {
                        const uniqueDocs = getUniqueDocs(message.sourceDocuments);
                        if (!uniqueDocs.length) return null;
                        const primaryDocs = uniqueDocs.slice(0, 3);
                        const extraDocs = uniqueDocs.slice(3);
                        const isOpen = showAllCitations[message.id];

                        return (
                          <div className="mt-3 pt-2 border-t border-gray-200 space-y-1.5">
                            <p className="text-sm font-semibold text-gray-700 mb-2.5 flex items-center gap-1.5">
                              <svg className="w-4 h-4 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                              </svg>
                              参考資料
                            </p>
                            <div className="space-y-1.5">
                              {primaryDocs.map((doc, idx) => (
                                <a
                                  key={`${doc.sourceUri || doc.documentName}-${idx}`}
                                  href={doc.lawCitation?.sourceUrl || documentHref(doc.sourceUri)}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700 hover:underline transition-all duration-200 p-1.5 rounded-lg hover:bg-blue-50 group"
                                >
                                  <svg className="w-4 h-4 flex-shrink-0 group-hover:scale-110 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                  </svg>
                                  <span className="truncate flex-1">
                                    {doc.lawCitation
                                      ? `${doc.lawCitation.lawTitle}【${doc.lawCitation.lawNumber} ${doc.lawCitation.provisionReference || ''}】`
                                      : doc.title ? `${doc.title}【${doc.documentName}】` : `【${doc.documentName}】`}
                                  </span>
                                  {doc.lawCitation && (
                                    <span className="shrink-0 text-[11px] text-gray-500">施行 {doc.lawCitation.effectiveDate}</span>
                                  )}
                                  <span className="text-gray-500 text-xs bg-gray-100 px-2 py-0.5 rounded-full">{(doc.relevance * 100).toFixed(0)}%</span>
                                </a>
                              ))}

                              {extraDocs.length > 0 && (
                                <div className="space-y-1.5">
                                  <button
                                    onClick={() => setShowAllCitations(prev => ({ ...prev, [message.id]: !prev[message.id] }))}
                                    className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1.5"
                                    aria-expanded={isOpen}
                                  >
                                    <svg className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                    </svg>
                                    {isOpen ? '折りたたむ' : `さらに ${extraDocs.length} 件表示`}
                                  </button>
                                  {isOpen && (
                                    <div className="space-y-1.5">
                                      {extraDocs.map((doc, idx) => (
                                        <a
                                          key={`${doc.sourceUri || doc.documentName}-extra-${idx}`}
                                          href={doc.lawCitation?.sourceUrl || documentHref(doc.sourceUri)}
                                          target="_blank"
                                          rel="noopener noreferrer"
                                          className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700 hover:underline transition-all duration-200 p-1.5 rounded-lg hover:bg-blue-50 group"
                                        >
                                          <svg className="w-4 h-4 flex-shrink-0 group-hover:scale-110 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                          </svg>
                                          <span className="truncate flex-1">
                                            {doc.lawCitation
                                              ? `${doc.lawCitation.lawTitle}【${doc.lawCitation.lawNumber} ${doc.lawCitation.provisionReference || ''}】`
                                              : doc.title ? `${doc.title}【${doc.documentName}】` : `【${doc.documentName}】`}
                                          </span>
                                          {doc.lawCitation && (
                                            <span className="shrink-0 text-[11px] text-gray-500">施行 {doc.lawCitation.effectiveDate}</span>
                                          )}
                                          <span className="text-gray-500 text-xs bg-gray-100 px-2 py-0.5 rounded-full">{(doc.relevance * 100).toFixed(0)}%</span>
                                        </a>
                                      ))}
                                    </div>
                                  )}
                                </div>
                              )}
                            </div>
                          </div>
                        );
                      })()}

                      {message.role === 'assistant' && (
                        <ChatMessageFeedback
                          messageId={message.id}
                          timestamp={message.timestamp}
                          feedback={message.feedback}
                          feedbackReason={message.feedbackReason}
                          feedbackComment={message.feedbackComment}
                          copied={copiedMessageId === message.id}
                          panelOpen={pendingBadMessageId === message.id}
                          pendingComment={pendingBadComment}
                          busy={Boolean(feedbackBusyIds[message.id])}
                          onCopy={() => handleCopyMessage(message.id, message.content)}
                          onGood={() => handleFeedback(message.id, 'good')}
                          onBad={() => handleFeedback(message.id, 'bad')}
                          onReason={(reason) => handleBadReason(message.id, reason)}
                          onCommentChange={setPendingBadComment}
                          onCommentSubmit={() => handleBadCommentOnly(message.id)}
                          onOpenPanel={() => openBadReasonPanel(message.id, message.feedbackComment)}
                          onClosePanel={() => {
                            setPendingBadMessageId(null);
                            setPendingBadComment('');
                          }}
                        />
                      )}

                      {/* Timestamp (user) */}
                      {message.role === 'user' && (
                        <p className="text-[11px] mt-1.5 text-blue-100 text-right">
                          {new Date(message.timestamp).toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' })}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
                {/* Typing Indicator */}
                {loading && (
                  <div className="flex justify-start animate-fade-in">
                    <div className="px-4 py-3 rounded-2xl rounded-tl-md bg-white border border-gray-200 shadow-sm">
                      <div className="flex items-center gap-2.5">
                        <div className="w-6 h-6 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center animate-pulse" aria-hidden>
                          <svg className="w-3.5 h-3.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                          </svg>
                        </div>
                        <div className="flex gap-1.5">
                          <div className="w-2.5 h-2.5 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                          <div className="w-2.5 h-2.5 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                          <div className="w-2.5 h-2.5 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                        </div>
                        <span className="text-sm text-gray-500 ml-2">考え中...</span>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </>
              </div>
            )}
          </div>

          {/* Scroll to Bottom Button - ChatGPT style */}
          {showScrollButton && messages.length > 0 && (
            <div className="absolute bottom-20 right-4 sm:right-6 z-20">
              <button
                onClick={scrollToBottom}
                className="p-2.5 bg-white border border-gray-300 rounded-full shadow-lg hover:shadow-xl transition-all duration-200 hover:bg-gray-50 group animate-fade-in"
                aria-label="最新の会話にスクロール"
              >
                <svg className="w-5 h-5 text-gray-700 group-hover:text-blue-600 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                </svg>
              </button>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="border-t border-red-200 bg-red-50 px-4 sm:px-6 py-3 flex-shrink-0">
              <div className="flex items-start gap-2">
                <svg className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-sm text-red-800 flex-1">{error}</p>
                <button
                  onClick={() => setError('')}
                  className="text-red-600 hover:text-red-800 flex-shrink-0"
                  aria-label="エラーを閉じる"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          )}

          {/* Input Area - Fixed at bottom */}
          <div className="border-t border-gray-200 bg-white/95 backdrop-blur-sm sticky bottom-0 z-10 flex-shrink-0 shadow-lg">
            <div className="p-3 sm:p-4">
              {/* Filter bar: collapsible, active filters summarized when closed */}
              {!isLawMode && (
              <div className="mb-2.5">
                <div className="flex flex-wrap items-center gap-2">
                  <button
                    type="button"
                    onClick={() => setFiltersOpen((v) => !v)}
                    aria-expanded={filtersOpen}
                    className={`inline-flex items-center gap-1.5 rounded-lg border px-2.5 py-1.5 text-xs font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                      filtersOpen || selectedCategories.length > 0 || selectedModel
                        ? 'border-blue-300 bg-blue-50 text-blue-700'
                        : 'border-gray-300 bg-white text-gray-600 hover:bg-gray-50'
                    }`}
                  >
                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden>
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                    </svg>
                    絞り込み
                    {(selectedCategories.length > 0 || !!selectedModel) && (
                      <span className="inline-flex items-center justify-center rounded-full bg-blue-600 text-white text-[10px] font-bold min-w-[18px] h-[18px] px-1">
                        {selectedCategories.length + (selectedModel ? 1 : 0)}
                      </span>
                    )}
                    <svg className={`w-3 h-3 transition-transform ${filtersOpen ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden>
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>

                  {/* Selected filters shown as removable pills while collapsed */}
                  {!filtersOpen &&
                    selectedCategories.map((v) => (
                      <button
                        key={v}
                        type="button"
                        onClick={() => setSelectedCategories((prev) => prev.filter((x) => x !== v))}
                        className="inline-flex items-center gap-1 rounded-full bg-blue-100 text-blue-800 text-xs px-2.5 py-1 hover:bg-blue-200 transition-colors"
                        title="クリックで解除"
                      >
                        {categoryOptions.find((o) => o.value === v)?.label || v}
                        <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden>
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    ))}
                  {!filtersOpen && selectedModel && (
                    <button
                      type="button"
                      onClick={() => setSelectedModel('')}
                      className="inline-flex items-center gap-1 rounded-full bg-indigo-100 text-indigo-800 text-xs px-2.5 py-1 hover:bg-indigo-200 transition-colors"
                      title="クリックで解除"
                    >
                      {selectedModelLabel}
                      <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden>
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  )}

                  {(selectedCategories.length > 0 || selectedModel) && (
                    <button
                      type="button"
                      onClick={() => {
                        setSelectedCategories([]);
                        setSelectedModel('');
                      }}
                      className="inline-flex items-center gap-1 text-xs text-gray-500 transition-colors hover:text-gray-700"
                    >
                      <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                      すべてクリア
                    </button>
                  )}
                </div>

                {filtersOpen && (
                  <div className="mt-2 rounded-lg border border-gray-200 bg-gray-50 p-3 space-y-2.5">
                    <div className="flex items-start gap-2">
                      <span className="flex-shrink-0 text-xs font-medium text-gray-500 mt-1">資料</span>
                      <div className="flex flex-wrap items-center gap-1.5">
                        {categoryOptions.map((opt) => (
                          <Chip
                            key={opt.value}
                            active={selectedCategories.includes(opt.value)}
                            onClick={() =>
                              setSelectedCategories((prev) =>
                                prev.includes(opt.value)
                                  ? prev.filter((v) => v !== opt.value)
                                  : [...prev, opt.value]
                              )
                            }
                          >
                            {opt.label}
                          </Chip>
                        ))}
                      </div>
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-xs font-medium text-gray-500">機種</span>
                        {selectedModel && (
                          <button
                            type="button"
                            onClick={() => setSelectedModel('')}
                            className="text-[11px] text-gray-500 hover:text-gray-700"
                          >
                            すべての機種に戻す
                          </button>
                        )}
                      </div>

                      {selectedModelOption && (
                        <p className="text-xs text-indigo-700 bg-indigo-50 border border-indigo-100 rounded-md px-2 py-1">
                          選択中: <span className="font-medium">{selectedModelOption.label}</span>
                          <span className="text-indigo-500 ml-1">
                            （名前の完全一致。対象: {selectedModelOption.targets.join(' / ')}。共通資料も含む）
                          </span>
                        </p>
                      )}

                      <div className="flex flex-wrap items-center gap-1.5">
                        {ALL_MODEL_TYPES.map((opt) => (
                          <Chip
                            key={opt.value}
                            active={selectedModel === opt.value}
                            onClick={() =>
                              setSelectedModel((prev) => (prev === opt.value ? '' : opt.value))
                            }
                          >
                            {opt.label}
                          </Chip>
                        ))}
                      </div>
                      <p className="text-[11px] text-gray-400">
                        取扱機種の絞り込み 6 項目のみ表示しています（未指定でも取扱外機種の資料は検索対象外です）
                      </p>
                    </div>
                  </div>
                )}
              </div>
              )}
              {isLawMode && (
                <div className="mb-2 rounded border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs leading-relaxed text-emerald-950">
                  収録中の現行法令を対象にしたプレリリース版です。条例・告示・通知、過去時点の適用は別途確認してください。
                </div>
              )}
              {readOnlySession && (
                <div className="mb-2 rounded border border-amber-300 bg-amber-50 px-3 py-2 text-xs text-amber-900">
                  管理者として他ユーザーのセッションを閲覧しています（読み取り専用・メッセージ送信はできません）
                </div>
              )}
              <div className="flex gap-2 sm:gap-3 items-end">
                <div className="flex-1 relative">
                  <textarea
                    ref={textareaRef}
                    value={input}
                    onChange={(e) => {
                      setInput(e.target.value);
                      // 高さを自動調整
                      const target = e.target as HTMLTextAreaElement;
                      target.style.height = 'auto';
                      target.style.height = `${Math.min(target.scrollHeight, 200)}px`;
                    }}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSendMessage();
                      }
                    }}
                    placeholder={readOnlySession
                      ? '読み取り専用セッションのため送信できません'
                      : isLawMode
                        ? '調べたい法令・条文・工事条件を入力してください'
                        : '質問を入力してください... (Shift+Enterで改行、Enterで送信)'}
                    disabled={loading || readOnlySession}
                    rows={1}
                    className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50 text-sm transition-all placeholder:text-gray-500 placeholder:opacity-100 shadow-sm hover:border-gray-400 bg-white text-gray-900 resize-none min-h-[42px] max-h-[200px] overflow-y-auto"
                    style={{
                      height: 'auto',
                      minHeight: '42px',
                    }}
                  />
                  {input.trim() && (
                    <button
                      onClick={() => setInput('')}
                      className="absolute right-2.5 top-2 text-gray-400 hover:text-gray-600 transition-colors"
                      aria-label="入力をクリア"
                    >
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  )}
                </div>
                <button
                  onClick={handleSendMessage}
                  disabled={loading || readOnlySession || !input.trim()}
                  className="px-3 sm:px-4 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg font-medium text-sm flex items-center gap-2 flex-shrink-0 transform hover:scale-105 active:scale-95 disabled:transform-none"
                >
                  {loading ? (
                    <>
                      <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      <span className="hidden sm:inline">送信中</span>
                    </>
                  ) : (
                    <>
                      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                      </svg>
                      <span className="hidden sm:inline">送信</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
