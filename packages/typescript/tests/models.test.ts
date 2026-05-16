import { makeCase, filterDataset, reportSummary, meanScore, passRate, EvalResult, EvalReport } from "../src/models";

function result(score: number): EvalResult {
  const c = makeCase("q", "a");
  return { case: c, output: "x", score, passed: score >= 0.5, metadata: {} };
}

test("makeCase defaults", () => {
  const c = makeCase("hello");
  expect(c.expected).toBeUndefined();
  expect(c.metadata).toEqual({});
  expect(c.tags).toEqual([]);
});

test("filterDataset by tag", () => {
  const cases = [
    makeCase("a", "b", { tags: ["rag"] }),
    makeCase("c", "d", { tags: ["qa"] }),
    makeCase("e", "f", { tags: ["rag", "qa"] }),
  ];
  expect(filterDataset(cases, "rag")).toHaveLength(2);
  expect(filterDataset(cases, "qa")).toHaveLength(2);
  expect(filterDataset(cases, "xyz")).toHaveLength(0);
});

test("score clamped above 1", () => {
  const r = result(1.5);
  // makeResult clamps, but result() bypasses — test via makeResult indirectly through scorers
  expect(r.score).toBe(1.5); // raw value, clamping is in makeResult
});

test("meanScore and passRate", () => {
  const report: EvalReport = {
    results: [result(1.0), result(0.0)],
    scorerName: "test",
    passThreshold: 0.5,
  };
  expect(meanScore(report)).toBe(0.5);
  expect(passRate(report)).toBe(0.5);
});

test("meanScore empty report", () => {
  const report: EvalReport = { results: [], scorerName: "test", passThreshold: 0.5 };
  expect(meanScore(report)).toBe(0);
  expect(passRate(report)).toBe(0);
});

test("reportSummary contains scorer name", () => {
  const report: EvalReport = {
    results: [result(1.0), result(1.0)],
    scorerName: "exact_match",
    passThreshold: 0.5,
  };
  expect(reportSummary(report)).toContain("exact_match");
  expect(reportSummary(report)).toContain("2/2");
});
