import { makeCase } from "../src/models";
import { ExactMatchScorer, RegexScorer, RougeScorer, rougeL, CustomScorer, LLMJudgeScorer } from "../src/scorers";

const c = (expected: string) => makeCase("q", expected);

// ── ExactMatchScorer ─────────────────────────────────────────────────────────

test("exact match pass", () => {
  expect(new ExactMatchScorer().score(c("Paris"), "Paris").score).toBe(1.0);
});

test("exact match fail", () => {
  expect(new ExactMatchScorer().score(c("Paris"), "Lyon").score).toBe(0.0);
});

test("exact match case-insensitive by default", () => {
  expect(new ExactMatchScorer().score(c("Paris"), "paris").score).toBe(1.0);
});

test("exact match case-sensitive", () => {
  expect(new ExactMatchScorer(true).score(c("Paris"), "paris").score).toBe(0.0);
});

test("exact match strips whitespace", () => {
  expect(new ExactMatchScorer().score(c("Paris"), "  Paris  ").score).toBe(1.0);
});

// ── RegexScorer ───────────────────────────────────────────────────────────────

test("regex match", () => {
  expect(new RegexScorer("\\d{3}-\\d{4}").score(c(""), "Call 555-1234 now").score).toBe(1.0);
});

test("regex no match", () => {
  expect(new RegexScorer("\\d{3}-\\d{4}").score(c(""), "No number").score).toBe(0.0);
});

// ── RougeScorer ───────────────────────────────────────────────────────────────

test("ROUGE-L perfect", () => {
  const s = rougeL("the cat sat on the mat", "the cat sat on the mat");
  expect(s).toBeCloseTo(1.0);
});

test("ROUGE-L empty output", () => {
  expect(rougeL("", "hello world")).toBe(0);
});

test("ROUGE-L partial", () => {
  const s = rougeL("the cat", "the cat sat on the mat");
  expect(s).toBeGreaterThan(0.3);
  expect(s).toBeLessThan(1.0);
});

test("RougeScorer threshold respected", () => {
  const r = new RougeScorer(0.9).score(c("the quick brown fox"), "the quick");
  expect(r.passed).toBe(false);
});

// ── CustomScorer ──────────────────────────────────────────────────────────────

test("custom scorer", () => {
  const scorer = new CustomScorer((_, o) => (o.length > 5 ? 1.0 : 0.0));
  expect(scorer.score(c(""), "long output").score).toBe(1.0);
  expect(scorer.score(c(""), "hi").score).toBe(0.0);
});

test("custom scorer score clamped", () => {
  const scorer = new CustomScorer(() => 1.5);
  expect(scorer.score(c(""), "x").score).toBe(1.0);
});

// ── LLMJudgeScorer (mocked) ──────────────────────────────────────────────────

test("llm judge parses response", async () => {
  const scorer = new LLMJudgeScorer();
  jest.spyOn(scorer, "_call" as never).mockResolvedValue('{"score": 0.9, "reason": "Correct."}' as never);
  const r = await scorer.scoreAsync(makeCase("2+2?", "4"), "4");
  expect(r.score).toBeCloseTo(0.9);
  expect(r.passed).toBe(true);
  expect(r.reason).toContain("Correct");
});

test("llm judge handles bad json gracefully", async () => {
  const scorer = new LLMJudgeScorer();
  jest.spyOn(scorer, "_call" as never).mockResolvedValue("oops" as never);
  const r = await scorer.scoreAsync(makeCase("q", "a"), "b");
  expect(r.score).toBe(0.0);
  expect(r.passed).toBe(false);
});

test("llm judge sync score throws", () => {
  const scorer = new LLMJudgeScorer();
  expect(() => scorer.score(makeCase("q", "a"), "b")).toThrow();
});
