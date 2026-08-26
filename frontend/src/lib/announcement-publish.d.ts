export type AnnouncementPublishStatus = 'draft' | 'scheduled' | 'published';

export interface ResolveAnnouncementPublishFieldsParams {
  requestedStatus: AnnouncementPublishStatus;
  publishMode: 'now' | 'schedule';
  scheduleAt: string;
  editingId: string | null;
  existingStatus: AnnouncementPublishStatus;
  existingPublishAt?: string;
  nowMs?: number;
}

export interface ResolvedAnnouncementPublishFields {
  status: AnnouncementPublishStatus;
  publishAt?: string;
}

export function resolveAnnouncementPublishFields(
  params: ResolveAnnouncementPublishFieldsParams,
): ResolvedAnnouncementPublishFields;
