import { EvalCase, EvalResult } from "../models";
import { Scorer, makeResult } from "./base";

export class RegexScorer implements Scorer {
  readonly name = "regex";
  private re: RegExp;

  constructor(pattern: string, flags: string = "i") {
    this.re = new RegExp(pattern, flags);
  }

  score(evalCase: EvalCase, output: string): EvalResult {
    return makeResult(evalCase, output, this.re.test(output) ? 1.0 : 0.0);
  }
}
