import { EvalCase, EvalResult } from "../models";
import { Scorer, makeResult } from "./base";

function lcsLength(a: string[], b: string[]): number {
  const m = a.length, n = b.length;
  const dp: number[][] = Array.from({ length: m + 1 }, () => new Array(n + 1).fill(0));
  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      dp[i][j] = a[i - 1] === b[j - 1] ? dp[i - 1][j - 1] + 1 : Math.max(dp[i - 1][j], dp[i][j - 1]);
    }
  }
  return dp[m][n];
}

export function rougeL(hypothesis: string, reference: string): number {
  const h = hypothesis.toLowerCase().split(/\s+/).filter(Boolean);
  const r = reference.toLowerCase().split(/\s+/).filter(Boolean);
  if (h.length === 0 || r.length === 0) return 0;
  const lcs       = lcsLength(h, r);
  const precision = lcs / h.length;
  const recall    = lcs / r.length;
  if (precision + recall === 0) return 0;
  return (2 * precision * recall) / (precision + recall);
}

export class RougeScorer implements Scorer {
  readonly name = "rouge_l";

  constructor(private threshold: number = 0.5) {}

  score(evalCase: EvalCase, output: string): EvalResult {
    const s = rougeL(output, evalCase.expected ?? "");
    return makeResult(evalCase, output, s, this.threshold);
  }
}
