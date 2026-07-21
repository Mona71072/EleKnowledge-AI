'use client';

import { useRouter } from 'next/navigation';

/**
 * Segment toggle shown ONLY to admins (A-17). Switches between the shared home
 * (user view) and the admin console. Selection is expressed by bold + underline,
 * never color alone (WCAG 1.4.1). Rendered as a tablist for keyboard support.
 */
export function AdminViewToggle({ current }: { current: 'home' | 'admin' }) {
  const router = useRouter();

  const seg = (key: 'home' | 'admin', label: string, href: string) => {
    const active = current === key;
    return (
      <button
        type="button"
        role="tab"
        aria-selected={active}
        onClick={() => router.push(href)}
        className={`px-4 py-1.5 text-sm rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 ${
          active
            ? 'bg-white font-bold text-blue-700 underline underline-offset-4 shadow-sm'
            : 'text-gray-600 hover:text-gray-900'
        }`}
      >
        {label}
      </button>
    );
  };

  return (
    <div role="tablist" aria-label="表示切替" className="inline-flex items-center gap-1 rounded-lg bg-gray-100 p-1">
      {seg('home', 'ホーム', '/')}
      {seg('admin', '管理', '/admin/dashboard')}
    </div>
  );
}
