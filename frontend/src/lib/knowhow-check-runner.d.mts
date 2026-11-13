export type CheckTaskStatus = 'pending' | 'running' | 'done' | 'failed' | 'cancelled';

export type CheckTaskState<Task, Result> = Task & {
  status: CheckTaskStatus;
  /** 成功したときの結果。 */
  result?: Result;
  /** 失敗したときの、利用者に見せてよい説明（例外本文は入れない）。 */
  failure?: string;
};

export type CheckRunSnapshot<Task, Result> = {
  readonly tasks: ReadonlyArray<Readonly<CheckTaskState<Task, Result>>>;
  readonly running: boolean;
};

export type CheckRunner<Task, Result> = {
  start(): void;
  cancel(): void;
  retry(id: string): void;
  dispose(): void;
  snapshot(): CheckRunSnapshot<Task, Result>;
};

export const CHECK_CONCURRENCY: number;

export function createCheckRunner<Task extends { id: string }, Result>(options: {
  tasks: readonly Task[];
  execute: (task: Task, signal: AbortSignal) => Promise<Result>;
  /** 1〜CHECK_CONCURRENCY。省略時は CHECK_CONCURRENCY。 */
  concurrency?: number;
  onUpdate?: (snapshot: CheckRunSnapshot<Task, Result>) => void;
  describeFailure?: (error: unknown, task: Task) => string;
  isFatal?: (error: unknown) => boolean;
}): CheckRunner<Task, Result>;

export function summarizeCheckRun(snapshot: { tasks: ReadonlyArray<{ status: string }> }): {
  total: number;
  done: number;
  failed: number;
  cancelled: number;
  finished: number;
};
