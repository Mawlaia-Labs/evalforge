import { EvalCase, EvalReport, EvalResult } from "./models";
import { Scorer } from "./scorers/base";

export type ModelFn = (input: string) => Promise<string> | string;

export interface RunOptions {
  passThreshold?: number;
  concurrency?:   number;
}

export async function runEval(
  cases:    EvalCase[],
  scorer:   Scorer,
  opts:     RunOptions & ({ modelFn: ModelFn; outputs?: never } | { outputs: string[]; modelFn?: never }),
): Promise<EvalReport> {
  const threshold = opts.passThreshold ?? 0.5;
  let outputs: string[];

  if ("outputs" in opts && opts.outputs !== undefined) {
    if (opts.outputs.length !== cases.length) {
      throw new Error(`outputs length ${opts.outputs.length} !== cases length ${cases.length}`);
    }
    outputs = opts.outputs;
  } else if ("modelFn" in opts && opts.modelFn !== undefined) {
    outputs = await runParallel(cases.map((c) => c.input), opts.modelFn, opts.concurrency ?? 4);
  } else {
    throw new Error("Provide either modelFn or outputs");
  }

  const results: EvalResult[] = cases.map((c, i) => {
    const r = scorer.score(c, outputs[i]);
    r.passed = r.score >= threshold;
    return r;
  });

  return { results, scorerName: scorer.name, passThreshold: threshold };
}

export async function compare(
  cases:     EvalCase[],
  scorer:    Scorer,
  baseline:  ModelFn,
  candidate: ModelFn,
  opts:      RunOptions = {},
): Promise<[EvalReport, EvalReport]> {
  const [baseOut, candOut] = await Promise.all([
    runParallel(cases.map((c) => c.input), baseline,  opts.concurrency ?? 4),
    runParallel(cases.map((c) => c.input), candidate, opts.concurrency ?? 4),
  ]);
  const [baseReport, candReport] = await Promise.all([
    runEval(cases, scorer, { outputs: baseOut, passThreshold: opts.passThreshold }),
    runEval(cases, scorer, { outputs: candOut, passThreshold: opts.passThreshold }),
  ]);
  return [baseReport, candReport];
}

async function runParallel(inputs: string[], fn: ModelFn, concurrency: number): Promise<string[]> {
  const results: string[] = new Array(inputs.length);
  for (let i = 0; i < inputs.length; i += concurrency) {
    const batch   = inputs.slice(i, i + concurrency);
    const outputs = await Promise.all(batch.map((inp) => Promise.resolve(fn(inp))));
    outputs.forEach((out, j) => { results[i + j] = out; });
  }
  return results;
}
