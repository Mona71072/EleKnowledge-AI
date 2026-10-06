export type TemplateKey = 'incident' | 'recovered' | 'signup_stop' | 'mail_limit' | 'maintenance' | 'model';

export interface AnnouncementTemplate {
  key: TemplateKey;
  name: string;
  type: 'update' | 'maintenance' | 'notice';
  severity: 'info' | 'warning' | 'critical';
  pinned: boolean;
  showInChat: boolean;
  when: string;
  title: string;
  body: string;
}

export const ANNOUNCEMENT_TEMPLATES: AnnouncementTemplate[];
export function getTemplate(key: string | null | undefined): AnnouncementTemplate | null;
export function fillTemplate(text: string | null | undefined, vars?: Record<string, string | number | null | undefined>): string;
export function templatePlaceholders(text: string | null | undefined): string[];
