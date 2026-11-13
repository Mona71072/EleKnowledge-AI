export interface ResearchJobStatus {
  jobId: string;
  sessionId?: string;
  status: string;
  stage?: string;
  pollAfterMs?: number;
  progress?: {
    step?: number;
    totalSteps?: number;
    searchesDone?: number;
    searchesTotal?: number;
  };
  message?: Record<string, unknown>;
  error?: { code?: string };
}

export interface JobPoller {
  start(jobId: string, options?: { visible?: boolean; pollAfterMs?: number }): boolean;
  stop(jobId: string): void;
  stopAll(): void;
  setVisible(visible: boolean): void;
}

export function createJobPoller(deps: {
  fetchJob(jobId: string): Promise<ResearchJobStatus>;
  onUpdate?(jobId: string, result: ResearchJobStatus): void;
  onGiveUp?(jobId: string): void;
  onRateLimited?(jobId: string): void;
}): JobPoller;