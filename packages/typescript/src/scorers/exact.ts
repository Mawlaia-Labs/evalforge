import { EvalCase, EvalResult } from "../models";
import { Scorer, makeResult } from "./base";

export class ExactMatchScorer implements Scorer {
  readonly name = "exact_match";

  constructor(
    private caseSensitive: boolean = false,
    private strip:         boolean = true,
  ) {}

  score(evalCase: EvalCase, output: string): EvalResult {
    let a = output;
    let b = evalCase.expected ?? "";
    if (this.strip) { a = a.trim(); b = b.trim(); }
    if (!this.caseSensitive) { a = a.toLowerCase(); b = b.toLowerCase(); }
    return makeResult(evalCase, output, a === b ? 1.0 : 0.0);
  }
}
