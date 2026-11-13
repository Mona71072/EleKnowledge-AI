export interface LatestGuard {
  begin(): number;
  invalidate(): void;
  isLatest(token: number): boolean;
}

export function createLatestGuard(): LatestGuard;
