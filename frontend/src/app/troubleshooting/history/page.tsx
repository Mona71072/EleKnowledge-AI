'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { getCurrentUser, fetchAuthSession } from 'aws-amplify/auth';
import axios from 'axios';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Loading } from '@/components/ui/Loading';
import { ErrorMessage } from '@/components/ui/ErrorMessage';

const API_BASE = process.env.NEXT_PUBLIC_TROUBLESHOOTING_API_URL || '';

interface SourceDocument {
  documentName: string;
  title?: string;
  sourceUri: string;
  documentType: string;
  model: string;
  relevance: number;
}

interface SessionSummary {
  sessionId: string;
  timestamp: string;
  input: {
    constructionNumber?: string;
    model?: string;
    errorCode?: string;
    troubleDescription?: string;
  };
  preview: string;
}

interface SessionDetail {
  session_id: string;
  userId: string;
  timestamp: string;
  input: SessionSummary['input'];
  result: string;
  sourceDocuments?: SourceDocument[];
}

function formatTimestamp(ts: string) {
  try {
    return new Date(ts).toLocaleString('ja-JP', {
      year: 'numeric', month: '2-digit', day: '2-digit',
      hour: '2-digit', minute: '2-digit',
    });
  } catch {
    return ts;
  }
}

const getUniqueDocs = (docs: SourceDocument[] = []) => {
  const seen = new Set<string>();
  return docs.filter((doc) => {
    const key = doc.sourceUri || doc.documentName;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
};

export default function HistoryPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [pageLoading, setPageLoading] = useState(true);
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [detail, setDetail] = useState<SessionDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState('');

  const getAuthToken = useCallback(async (): Promise<string | null> => {
    try {
      const session = await fetchAuthSession();
      return session.tokens?.idToken?.toString() || null;
    } catch {
      return null;
    }
  }, []);

  const fetchList = useCallback(async () => {
    const token = await getAuthToken();
    const response = await axios.get<{ sessions: SessionSummary[] }>(
      `${API_BASE}/history`,
      { headers: token ? { Authorization: `Bearer ${token}` } : {} }
    );
    setSessions(response.data.sessions);
  }, [getAuthToken]);

  const fetchDetail = useCallback(async (sessionId: string) => {
    setDetailLoading(true);
    setError('');
    try {
      const token = await getAuthToken();
      const response = await axios.get<SessionDetail>(
        `${API_BASE}/history?sessionId=${encodeURIComponent(sessionId)}`,
        { headers: token ? { Authorization: `Bearer ${token}` } : {} }
      );
      setDetail(response.data);
    } catch (err: any) {
      setError(err.response?.data?.error || '詳細の取得に失敗しました');
    } finally {
      setDetailLoading(false);
    }
  }, [getAuthToken]);

  useEffect(() => {
    const init = async () => {
      const skipAuth = process.env.NEXT_PUBLIC_SKIP_AUTH === 'true';
      const canBypassAuth = skipAuth && process.env.NODE_ENV !== 'production';
      if (!canBypassAuth) {
        try {
          await getCurrentUser();
        } catch {
          router.push('/login');
          return;
        }
      }
      try {
        await fetchList();
      } catch {
        setError('履歴の取得に失敗しました');
      }
      setPageLoading(false);
    };
    init();
  }, [router, fetchList]);

  useEffect(() => {
    const sessionId = searchParams.get('sessionId');
    if (sessionId && !pageLoading) {
      fetchDetail(sessionId);
    }
  }, [searchParams, pageLoading, fetchDetail]);

  if (pageLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Loading size="lg" text="読み込み中..." />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center gap-4">
          <Link href="/troubleshooting" className="text-gray-500 hover:text-gray-700 transition-colors">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
          </Link>
          <h1 className="text-xl font-bold text-gray-900">分析履歴</h1>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        {error && <ErrorMessage message={error} />}

        {/* 詳細表示 */}
        {detail && (
          <Card variant="elevated" padding="none">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900">分析結果詳細</h2>
                  <p className="text-sm text-gray-500">{formatTimestamp(detail.timestamp)}</p>
                </div>
                <Button variant="outline" size="sm" onClick={() => setDetail(null)}>
                  一覧に戻る
                </Button>
              </div>

              {/* 入力情報 */}
              <div className="mb-4 p-3 bg-gray-50 rounded-lg text-sm text-gray-600 space-y-1">
                {detail.input.constructionNumber && <p>工事番号: {detail.input.constructionNumber}</p>}
                {detail.input.model && <p>機種: {detail.input.model}</p>}
                {detail.input.errorCode && <p>エラーコード: {detail.input.errorCode}</p>}
                <p className="text-gray-700">{detail.input.troubleDescription}</p>
              </div>

              {/* 分析結果テキスト */}
              <div className="prose prose-sm max-w-none text-gray-800 whitespace-pre-wrap leading-relaxed">
                {detail.result}
              </div>

              {/* 参考資料 */}
              {(() => {
                const uniqueDocs = getUniqueDocs(detail.sourceDocuments);
                if (!uniqueDocs.length) return null;
                return (
                  <div className="mt-4 pt-4 border-t border-gray-200 space-y-1.5">
                    <p className="text-sm font-semibold text-gray-700 mb-2.5">参考資料</p>
                    {uniqueDocs.map((doc, idx) => (
                      <a
                        key={`${doc.sourceUri || doc.documentName}-${idx}`}
                        href={doc.sourceUri}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700 hover:underline p-1.5 rounded-lg hover:bg-blue-50"
                      >
                        <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        <span className="truncate flex-1">
                          {doc.title ? `${doc.title}【${doc.documentName}】` : `【${doc.documentName}】`}
                        </span>
                        <span className="text-gray-500 text-xs bg-gray-100 px-2 py-0.5 rounded-full">
                          {(doc.relevance * 100).toFixed(0)}%
                        </span>
                      </a>
                    ))}
                  </div>
                );
              })()}
            </CardContent>
          </Card>
        )}

        {/* 一覧表示 */}
        {!detail && (
          <div className="space-y-3">
            {sessions.length === 0 ? (
              <Card variant="elevated" padding="none">
                <CardContent className="p-6 text-center text-gray-500">
                  まだ分析履歴がありません
                </CardContent>
              </Card>
            ) : (
              sessions.map((session) => (
                <Card
                  key={session.sessionId}
                  variant="elevated"
                  padding="none"
                  className="cursor-pointer hover:shadow-md transition-shadow"
                >
                  <CardContent
                    className="p-4"
                    onClick={() => fetchDetail(session.sessionId)}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          {session.input.constructionNumber && (
                            <span className="text-xs font-medium text-blue-700 bg-blue-50 px-2 py-0.5 rounded">
                              {session.input.constructionNumber}
                            </span>
                          )}
                          {session.input.model && (
                            <span className="text-xs font-medium text-gray-600 bg-gray-100 px-2 py-0.5 rounded">
                              {session.input.model}
                            </span>
                          )}
                          {session.input.errorCode && (
                            <span className="text-xs font-medium text-orange-700 bg-orange-50 px-2 py-0.5 rounded">
                              {session.input.errorCode}
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-gray-700 truncate">
                          {session.input.troubleDescription || '(入力情報なし)'}
                        </p>
                        {session.preview && (
                          <p className="mt-1 text-xs text-gray-500 line-clamp-2">
                            {session.preview}
                          </p>
                        )}
                      </div>
                      <div className="text-right shrink-0">
                        <p className="text-xs text-gray-400">{formatTimestamp(session.timestamp)}</p>
                        <svg className="w-4 h-4 text-gray-400 ml-auto mt-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </div>
                    </div>
                    {detailLoading && (
                      <div className="mt-2 flex justify-center">
                        <Loading size="sm" />
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        )}
      </main>
    </div>
  );
}
