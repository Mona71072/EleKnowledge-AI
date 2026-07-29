import { AdminOnlyGuard } from '@/components/auth/AdminOnlyGuard';

export default function TroubleshootingLayout({ children }: { children: React.ReactNode }) {
  return (
    <AdminOnlyGuard
      title="管理者権限が必要です"
      description="トラブルシューティングは開発中のため、管理者のみ利用できます。"
    >
      {children}
    </AdminOnlyGuard>
  );
}
