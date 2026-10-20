import { AdminOnlyGuard } from '@/components/auth/AdminOnlyGuard';

export default function KnowledgeChatLayout({ children }: { children: React.ReactNode }) {
  return (
    <AdminOnlyGuard description="工技先輩は開発中のため、管理者のみ利用できます。">
      {children}
    </AdminOnlyGuard>
  );
}
