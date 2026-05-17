import { Scorer, makeResult } from "./base";
import type { EvalCase, EvalResult } from "../models";

export interface HostedScorerOptions {
  apiKey: string;
  scorer?: "exact_match" | "rouge_l" | "regex" | "llm_judge";
  threshold?: number;
  criteria?: string;
  pattern?: string;
  baseUrl?: string;
  timeout?: number;
}

export class HostedScorer implements Scorer {
  readonly name = "hosted";
  private readonly apiKey: string;
  private readonly scorer: string;
  private readonly threshold: number;
  private readonly criteria?: string;
  private readonly pattern?: string;
  private readonly baseUrl: string;
  private readonly timeout: number;

  constructor(options: HostedScorerOptions) {
    this.apiKey    = options.apiKey;
    this.scorer    = options.scorer ?? "llm_judge";
    this.threshold = options.threshold ?? 0.7;
    this.criteria  = options.criteria;
    this.pattern   = options.pattern;
    this.baseUrl   = (options.baseUrl ?? "https://api.mawlaia.com").replace(/\/$/, "");
    this.timeout   = options.timeout ?? 30_000;
  }

  score(_evalCase: EvalCase, _output: string): EvalResult {
    throw new Error("Use scoreAsync() or scoreBatchAsync() for HostedScorer");
  }

  async scoreAsync(evalCase: EvalCase, output: string): Promise<EvalResult> {
    const results = await this.scoreBatchAsync([evalCase], [output]);
    return results[0];
  }

  async scoreBatchAsync(cases: EvalCase[], outputs: string[]): Promise<EvalResult[]> {
    const body: Record<string, unknown> = {
      scorer: this.scorer,
      threshold: this.threshold,
      cases: cases.map((c, i) => ({ input: c.input, output: outputs[i], expected: c.expected })),
    };
    if (this.criteria) body.criteria = this.criteria;
    if (this.pattern)  body.pattern  = this.pattern;

    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), this.timeout);
    let data: { results: Record<string, unknown>[] };
    try {
      const res = await fetch(`${this.baseUrl}/v1/eval/score`, {
        method: "POST",
        headers: { Authorization: `Bearer ${this.apiKey}`, "Content-Type": "application/json" },
        body: JSON.stringify(body),
        signal: controller.signal,
      });
      if (!res.ok) throw new Error(`Mawlaia API error: ${res.status} ${await res.text()}`);
      data = await res.json() as typeof data;
    } finally {
      clearTimeout(id);
    }

    return (data.results ?? []).map((item) =>
      makeResult(
        cases[0],
        item.output as string,
        Number(item.score),
        this.threshold,
        item.rationale as string | undefined,
      ),
    );
  }
}
