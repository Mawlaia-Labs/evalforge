export type { EvalCase, EvalResult, EvalReport } from "./models";
export { makeCase, reportSummary, meanScore, passRate, filterDataset } from "./models";
export { runEval, compare } from "./runner";
export type { ModelFn, RunOptions } from "./runner";
export { ExactMatchScorer, RegexScorer, RougeScorer, rougeL, LLMJudgeScorer, CustomScorer, HostedScorer } from "./scorers";
export type { Scorer, HostedScorerOptions } from "./scorers";
export { load as loadDataset, fromJSON, fromJSONL, fromCSV } from "./datasets/loaders";

export const VERSION = "0.3.0";
