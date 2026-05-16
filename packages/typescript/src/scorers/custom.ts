import { EvalCase, EvalResult } from "../models";
import { Scorer, makeResult } from "./base";

export class CustomScorer implements Scorer {
  readonly name = "custom";

  constructor(
    private fn:        (evalCase: EvalCase, output: string) => number,
    private threshold: number = 0.5,
  ) {}

  score(evalCase: EvalCase, output: string): EvalResult {
    return makeResult(evalCase, output, this.fn(evalCase, output), this.threshold);
  }
}
