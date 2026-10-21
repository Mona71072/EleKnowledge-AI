export function modelWithFacts(model: string): string;
export function modelFitNotice(
  match: { modelFit?: string; modelFitProducts?: readonly string[] },
  selectedModel?: string,
): string | null;
