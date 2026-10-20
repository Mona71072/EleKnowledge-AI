export declare function appendAnnouncementPage<T extends { announcementId: string }>(
  current: T[],
  next: T[],
): T[];

export declare function sortActiveAnnouncements<T extends { severity: 'info' | 'warning' | 'critical'; publishAt: string }>(
  list: T[],
): T[];
