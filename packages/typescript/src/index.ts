export type { EvalCase, EvalResult, EvalReport } from "./models";
export { makeCase, reportSummary, meanScore, passRate, filterDataset } from "./models";
export { runEval, compare } from "./runner";
export type { ModelFn, RunOptions } from "./runner";
export { ExactMatchScorer, RegexScorer, RougeScorer, rougeL, LLMJudgeScorer, CustomScorer } from "./scorers";
export type { Scorer } from "./scorers";
export { load as loadDataset, fromJSON, fromJSONL, fromCSV } from "./datasets/loaders";

export const VERSION = "0.1.0";
