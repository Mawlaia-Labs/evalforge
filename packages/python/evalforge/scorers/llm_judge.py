from __future__ import annotations
import re
from ..models import EvalCase, EvalResult
from .base import Scorer

_DEFAULT_RUBRIC = """\
You are a strict but fair evaluator. Given an input, an expected answer, and a model's actual output, \
score the output from 0.0 (completely wrong) to 1.0 (perfect).

Respond with exactly this JSON:
{{"score": <float 0.0-1.0>, "reason": "<one sentence>"}}

Input:    {input}
Expected: {expected}
Output:   {output}"""

_SCORE_RE = re.compile(r'"score"\s*:\s*([0-9]*\.?[0-9]+)')
_REASON_RE = re.compile(r'"reason"\s*:\s*"([^"]*)"')


class LLMJudgeScorer(Scorer):
    name = "llm_judge"

    def __init__(
        self,
        model:      str   = "gpt-4o-mini",
        provider:   str   = "openai",    # "openai" | "anthropic"
        rubric:     str   = _DEFAULT_RUBRIC,
        threshold:  float = 0.7,
    ):
        self.model     = model
        self.provider  = provider
        self.rubric    = rubric
        self.threshold = threshold
        self._client   = None

    def _get_client(self):
        if self._client is not None:
            return self._client
        if self.provider == "openai":
            from openai import OpenAI
            self._client = OpenAI()
        else:
            from anthropic import Anthropic
            self._client = Anthropic()
        return self._client

    def _call(self, prompt: str) -> str:
        client = self._get_client()
        if self.provider == "openai":
            resp = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )
            return resp.choices[0].message.content or ""
        else:
            resp = client.messages.create(
                model=self.model,
                max_tokens=256,
                messages=[{"role": "user", "content": prompt}],
            )
            return resp.content[0].text if resp.content else ""

    def score(self, case: EvalCase, output: str) -> EvalResult:
        prompt = self.rubric.format(
            input=case.input,
            expected=case.expected or "(none)",
            output=output,
        )
        raw    = self._call(prompt)
        sm     = _SCORE_RE.search(raw)
        rm     = _REASON_RE.search(raw)
        s      = float(sm.group(1)) if sm else 0.0
        reason = rm.group(1) if rm else raw[:200]
        return self._result(case, output, s, pass_threshold=self.threshold, reason=reason)
