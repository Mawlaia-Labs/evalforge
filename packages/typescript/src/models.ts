export interface EvalCase {
  input:    string;
  expected?: string;
  metadata: Record<string, unknown>;
  tags:     string[];
}

export interface EvalResult {
  case:     EvalCase;
  output:   string;
  score:    number;       // 0.0–1.0
  passed:   boolean;
  reason?:  string;
  metadata: Record<string, unknown>;
}

export interface EvalReport {
  results:       EvalResult[];
  scorerName:    string;
  passThreshold: number;
}

export function makeCase(
  input: string,
  expected?: string,
  opts: { metadata?: Record<string, unknown>; tags?: string[] } = {},
): EvalCase {
  return { input, expected, metadata: opts.metadata ?? {}, tags: opts.tags ?? [] };
}

export function reportSummary(report: EvalReport): string {
  const n      = report.results.length;
  const passed = report.results.filter((r) => r.passed).length;
  const mean   = n === 0 ? 0 : report.results.reduce((s, r) => s + r.score, 0) / n;
  return [
    `Scorer : ${report.scorerName}`,
    `Cases  : ${n}`,
    `Passed : ${passed}/${n} (${n === 0 ? "0%" : Math.round((passed / n) * 100) + "%"})`,
    `Score  : ${mean.toFixed(3)}`,
  ].join("\n");
}

export function meanScore(report: EvalReport): number {
  if (report.results.length === 0) return 0;
  return report.results.reduce((s, r) => s + r.score, 0) / report.results.length;
}

export function passRate(report: EvalReport): number {
  if (report.results.length === 0) return 0;
  return report.results.filter((r) => r.passed).length / report.results.length;
}

export function filterDataset(cases: EvalCase[], tag: string): EvalCase[] {
  return cases.filter((c) => c.tags.includes(tag));
}
