'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { getCurrentUser, fetchAuthSession } from 'aws-amplify/auth';
import axios from 'axios';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Loading } from '@/components/ui/Loading';
import { ErrorMessage } from '@/components/ui/ErrorMessage';

const ALLOWED_MODELS = ['KE-LG', 'KM-LD', 'CM-MA', 'ME-CH'] as const;

interface SourceDocument {
  documentName: string;
  title?: string;
  sourceUri: string;
  documentType: string;
  model: string;
  relevance: number;
}

interface TroubleshootingResult {
  sessionId?: string;
  result: string;
  sourceDocuments?: SourceDocument[];
}

interface FormState {
  constructionNumber: string;
  troubleDescription: string;
  model: string;
  errorCode: string;
}

interface FormErrors {
  constructionNumber?: string;
  troubleDescription?: string;
  model?: string;
  errorCode?: string;
  general?: string;
}

function validateForm(form: FormState): FormErrors {
  const errors: FormErrors = {};

  if (!form.constructionNumber && !form.model) {
    errors.constructionNumber = '工事番号か機種のどちらかを入力してください';
  }

  if (form.constructionNumber && !/^[A-Za-z0-9]{8}$/.test(form.constructionNumber)) {
    errors.constructionNumber = '工事番号は半角英数8文字で入力してください';
  }

  if (!form.troubleDescription.trim()) {
    errors.troubleDescription = '不具合情報を入力してください';
  } else if (form.troubleDescription.trim().length < 5) {
    errors.troubleDescription = '不具合情報は5文字以上で入力してください';
  } else if (form.troubleDescription.trim().length > 2000) {
    errors.troubleDescription = '不具合情報は2000文字以内で入力してください';
  }

  if (form.errorCode && !/^[A-Z0-9]{4}$/.test(form.errorCode)) {
    errors.errorCode = 'エラーコードは半角英大文字・数字4文字で入力してください';
  }

  return errors;
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

export default function TroubleshootingPage() {
  const router = useRouter();
  const [pageLoading, setPageLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<TroubleshootingResult | null>(null);
  const [apiError, setApiError] = useState('');
  const [formErrors, setFormErrors] = useState<FormErrors>({});
  const [showAllCitations, setShowAllCitations] = useState(false);

  const [form, setForm] = useState<FormState>({
    constructionNumber: '',
    troubleDescription: '',
    model: '',
    errorCode: '',
  });

  const API_URL = process.env.NEXT_PUBLIC_TROUBLESHOOTING_API_URL || '';

  useEffect(() => {
    const init = async () => {
      const skipAuth = process.env.NEXT_PUBLIC_SKIP_AUTH === 'true';
      const canBypassAuth = skipAuth && process.env.NODE_ENV !== 'production';
      if (canBypassAuth) {
        setPageLoading(false);
        return;
      }
      try {
        await getCurrentUser();
      } catch {
        router.push('/login');
        return;
      }
      setPageLoading(false);
    };
    init();
  }, [router]);

  const getAuthToken = async (): Promise<string | null> => {
    try {
      const session = await fetchAuthSession();
      return session.tokens?.idToken?.toString() || null;
    } catch {
      return null;
    }
  };

  const handleChange = (field: keyof FormState) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }));
    setFormErrors((prev) => ({ ...prev, [field]: undefined }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setApiError('');
    setResult(null);

    const errors = validateForm(form);
    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      return;
    }

    setSubmitting(true);
    try {
      const skipAuth = process.env.NEXT_PUBLIC_SKIP_AUTH === 'true';
      const canBypassAuth = skipAuth && process.env.NODE_ENV !== 'production';
      const token = canBypassAuth ? 'dev-token' : await getAuthToken();

      const payload: Record<string, string> = {
        troubleDescription: form.troubleDescription.trim(),
      };
      if (form.constructionNumber) payload.constructionNumber = form.constructionNumber.trim();
      if (form.model) payload.model = form.model;
      if (form.errorCode) payload.errorCode = form.errorCode.trim();

      const response = await axios.post<TroubleshootingResult>(
        `${API_URL}/analyze`,
        payload,
        {
          headers: {
            'Content-Type': 'application/json',
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
        }
      );

      setResult(response.data);
    } catch (err: any) {
      const msg =
        err.response?.data?.error ||
        err.response?.data?.message ||
        'エラーが発生しました。しばらく待ってから再度お試しください。';
      setApiError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setApiError('');
    setFormErrors({});
    setShowAllCitations(false);
  };

  if (pageLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Loading size="lg" text="読み込み中..." />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center gap-4">
          <Link href="/" className="text-gray-500 hover:text-gray-700 transition-colors">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
          </Link>
          <h1 className="text-xl font-bold text-gray-900">トラブルシューティング</h1>
          <Link
            href="/troubleshooting/history"
            className="ml-auto text-sm text-blue-600 hover:text-blue-700 hover:underline"
          >
            履歴
          </Link>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        {/* 入力フォーム */}
        {!result && (
          <Card variant="elevated" padding="none">
            <CardContent className="p-6">
              <div className="mb-6">
                <h2 className="text-lg font-semibold text-gray-900">トラブル情報を入力</h2>
                <p className="mt-1 text-sm text-gray-500">
                  工事番号か機種のどちらかは必須です。不具合情報を詳しく記述するほど精度が上がります。
                </p>
              </div>

              <form onSubmit={handleSubmit} noValidate className="space-y-5">
                {/* 工事番号 */}
                <Input
                  label="工事番号"
                  placeholder="例: EIK54801（半角英数8文字）"
                  value={form.constructionNumber}
                  onChange={handleChange('constructionNumber')}
                  error={formErrors.constructionNumber}
                  maxLength={8}
                  helperText="機種を指定する場合は省略可"
                />

                {/* 機種 */}
                <div className="w-full flex flex-col">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    機種
                  </label>
                  <select
                    value={form.model}
                    onChange={handleChange('model')}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors text-base text-gray-900"
                  >
                    <option value="">選択してください（任意）</option>
                    {ALLOWED_MODELS.map((m) => (
                      <option key={m} value={m}>{m}</option>
                    ))}
                  </select>
                  {formErrors.model && (
                    <p className="mt-1 text-sm text-red-600" role="alert">{formErrors.model}</p>
                  )}
                </div>

                {/* エラーコード */}
                <Input
                  label="エラーコード"
                  placeholder="例: E001（半角英大文字・数字4文字）"
                  value={form.errorCode}
                  onChange={handleChange('errorCode')}
                  error={formErrors.errorCode}
                  maxLength={4}
                  helperText="任意"
                />

                {/* 不具合情報 */}
                <div className="w-full flex flex-col">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    不具合情報 <span className="text-red-500">*</span>
                  </label>
                  <textarea
                    value={form.troubleDescription}
                    onChange={handleChange('troubleDescription')}
                    placeholder="例: 昇降機が2階と3階の間で停止し、ドアが開かない状態が続いています。エラー表示はパネルに E001 と出ています。"
                    rows={5}
                    maxLength={2000}
                    className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors text-base text-gray-900 placeholder:text-gray-500 resize-y ${
                      formErrors.troubleDescription ? 'border-red-300 focus:ring-red-500' : 'border-gray-300'
                    }`}
                  />
                  <div className="flex justify-between mt-1">
                    {formErrors.troubleDescription ? (
                      <p className="text-sm text-red-600" role="alert">{formErrors.troubleDescription}</p>
                    ) : (
                      <span className="text-sm text-gray-500">5〜2000文字</span>
                    )}
                    <span className="text-sm text-gray-400 ml-2 shrink-0">
                      {form.troubleDescription.length} / 2000
                    </span>
                  </div>
                </div>

                {apiError && <ErrorMessage message={apiError} />}

                <div className="pt-2">
                  <Button
                    type="submit"
                    variant="primary"
                    size="lg"
                    className="w-full"
                    disabled={submitting}
                  >
                    {submitting ? (
                      <span className="flex items-center justify-center gap-2">
                        <Loading size="sm" />
                        分析中...（最大60秒）
                      </span>
                    ) : (
                      'トラブルを分析する'
                    )}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* 分析結果 */}
        {result && (
          <div className="space-y-4">
            <Card variant="elevated" padding="none">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h2 className="text-lg font-semibold text-gray-900">分析結果</h2>
                    {result.sessionId && (
                      <Link
                        href={`/troubleshooting/history?sessionId=${result.sessionId}`}
                        className="text-xs text-blue-500 hover:underline"
                      >
                        履歴で確認
                      </Link>
                    )}
                  </div>
                  <Button variant="outline" size="sm" onClick={handleReset}>
                    もう一度分析する
                  </Button>
                </div>
                <div className="prose prose-sm max-w-none text-gray-800 whitespace-pre-wrap leading-relaxed">
                  {result.result}
                </div>

                {/* 参考資料 */}
                {result.sourceDocuments && result.sourceDocuments.length > 0 && (() => {
                  const uniqueDocs = getUniqueDocs(result.sourceDocuments);
                  if (!uniqueDocs.length) return null;
                  const primaryDocs = uniqueDocs.slice(0, 3);
                  const extraDocs = uniqueDocs.slice(3);
                  return (
                    <div className="mt-4 pt-4 border-t border-gray-200 space-y-1.5">
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
                            href={doc.sourceUri}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700 hover:underline transition-all duration-200 p-1.5 rounded-lg hover:bg-blue-50 group"
                          >
                            <svg className="w-4 h-4 flex-shrink-0 group-hover:scale-110 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                            <span className="truncate flex-1">
                              {doc.title ? `${doc.title}【${doc.documentName}】` : `【${doc.documentName}】`}
                            </span>
                            <span className="text-gray-500 text-xs bg-gray-100 px-2 py-0.5 rounded-full">{(doc.relevance * 100).toFixed(0)}%</span>
                          </a>
                        ))}

                        {extraDocs.length > 0 && (
                          <div className="space-y-1.5">
                            <button
                              onClick={() => setShowAllCitations((prev) => !prev)}
                              className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1.5"
                              aria-expanded={showAllCitations}
                            >
                              <svg className={`w-4 h-4 transition-transform ${showAllCitations ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                              </svg>
                              {showAllCitations ? '折りたたむ' : `さらに ${extraDocs.length} 件表示`}
                            </button>
                            {showAllCitations && (
                              <div className="space-y-1.5">
                                {extraDocs.map((doc, idx) => (
                                  <a
                                    key={`${doc.sourceUri || doc.documentName}-extra-${idx}`}
                                    href={doc.sourceUri}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700 hover:underline transition-all duration-200 p-1.5 rounded-lg hover:bg-blue-50 group"
                                  >
                                    <svg className="w-4 h-4 flex-shrink-0 group-hover:scale-110 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                    </svg>
                                    <span className="truncate flex-1">
                                      {doc.title ? `${doc.title}【${doc.documentName}】` : `【${doc.documentName}】`}
                                    </span>
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
              </CardContent>
            </Card>

            <div className="flex justify-center">
              <Button variant="secondary" onClick={handleReset}>
                新しいトラブルを入力
              </Button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
