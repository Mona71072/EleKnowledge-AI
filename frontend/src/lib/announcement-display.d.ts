export function announcementDate(iso: string): string;
export function loadReadAnnouncementIds(key: string, storage?: Pick<Storage, 'getItem'>): string[];
export function markAnnouncementRead(key: string, id: string, currentIds: string[], storage?: Pick<Storage, 'getItem' | 'setItem'>): string[];
