import { EvalCase, EvalResult } from "../models";

export interface Scorer {
  readonly name: string;
  score(evalCase: EvalCase, output: string): EvalResult;
}

export function makeResult(
  evalCase:      EvalCase,
  output:        string,
  score:         number,
  passThreshold: number = 0.5,
  reason?:       string,
): EvalResult {
  const clamped = Math.max(0, Math.min(1, score));
  return {
    case:     evalCase,
    output,
    score:    clamped,
    passed:   clamped >= passThreshold,
    reason,
    metadata: {},
  };
}
