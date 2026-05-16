import { EvalCase, EvalResult } from "../models";
import { Scorer, makeResult } from "./base";

const DEFAULT_RUBRIC = `You are a strict but fair evaluator. Given an input, an expected answer, and a model's actual output, score the output from 0.0 (completely wrong) to 1.0 (perfect).

Respond with exactly this JSON:
{"score": <float 0.0-1.0>, "reason": "<one sentence>"}

Input:    {input}
Expected: {expected}
Output:   {output}`;

const SCORE_RE  = /"score"\s*:\s*([0-9]*\.?[0-9]+)/;
const REASON_RE = /"reason"\s*:\s*"([^"]*)"/;

export class LLMJudgeScorer implements Scorer {
  readonly name = "llm_judge";
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private _client: any = null;

  constructor(
    private model:     string = "gpt-4o-mini",
    private provider:  "openai" | "anthropic" = "openai",
    private rubric:    string = DEFAULT_RUBRIC,
    private threshold: number = 0.7,
  ) {}

  private getClient() {
    if (this._client) return this._client;
    if (this.provider === "openai") {
      // eslint-disable-next-line @typescript-eslint/no-require-imports
      const { OpenAI } = require("openai");
      this._client = new OpenAI();
    } else {
      // eslint-disable-next-line @typescript-eslint/no-require-imports
      const { default: Anthropic } = require("@anthropic-ai/sdk");
      this._client = new Anthropic();
    }
    return this._client;
  }

  async _call(prompt: string): Promise<string> {
    const client = this.getClient();
    if (this.provider === "openai") {
      const resp = await client.chat.completions.create({
        model: this.model,
        messages: [{ role: "user", content: prompt }],
        temperature: 0,
      });
      return resp.choices[0]?.message?.content ?? "";
    } else {
      const resp = await client.messages.create({
        model: this.model,
        max_tokens: 256,
        messages: [{ role: "user", content: prompt }],
      });
      return resp.content[0]?.text ?? "";
    }
  }

  score(evalCase: EvalCase, output: string): EvalResult {
    const prompt = this.rubric
      .replace("{input}",    evalCase.input)
      .replace("{expected}", evalCase.expected ?? "(none)")
      .replace("{output}",   output);

    // Synchronous stub — async version via scoreAsync
    throw new Error("Use scoreAsync() for LLMJudgeScorer");
  }

  async scoreAsync(evalCase: EvalCase, output: string): Promise<EvalResult> {
    const prompt = this.rubric
      .replace("{input}",    evalCase.input)
      .replace("{expected}", evalCase.expected ?? "(none)")
      .replace("{output}",   output);

    const raw    = await this._call(prompt);
    const sm     = SCORE_RE.exec(raw);
    const rm     = REASON_RE.exec(raw);
    const s      = sm ? parseFloat(sm[1]) : 0.0;
    const reason = rm ? rm[1] : raw.slice(0, 200);
    return makeResult(evalCase, output, s, this.threshold, reason);
  }
}
