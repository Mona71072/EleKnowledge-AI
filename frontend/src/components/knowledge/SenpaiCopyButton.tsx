'use client';

import { useEffect, useRef, useState } from 'react';
import { copyText } from '@/lib/knowledge-senpai-research-view.mjs';
import { CopyIcon } from './SenpaiIcons';

/** 「回答をコピー」。クリップボードが使えない環境でも画面は壊さず、結果を短く知らせる。 */
export function SenpaiCopyButton({ getText }: { getText: () => string }) {
  const [state, setState] = useState<'idle' | 'copied' | 'failed'>('idle');
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  useEffect(() => () => { if (timer.current) clearTimeout(timer.current); }, []);

  async function copy() {
    setState((await copyText(getText())) ? 'copied' : 'failed');
    if (timer.current) clearTimeout(timer.current);
    timer.current = setTimeout(() => setState('idle'), 2000);
  }

  return (
    <>
      <button type="button" onClick={copy} aria-label="回答をコピー" title="回答をコピー" className="flex h-8 w-8 items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-900 focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500"><CopyIcon /></button>
      <span role="status" className="text-xs text-gray-500">{state === 'copied' ? 'コピーしました' : state === 'failed' ? 'コピーできませんでした' : ''}</span>
    </>
  );
}
