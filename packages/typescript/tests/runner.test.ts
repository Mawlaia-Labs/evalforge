import { makeCase } from "../src/models";
import { runEval, compare } from "../src/runner";
import { ExactMatchScorer } from "../src/scorers";

const cases = [
  makeCase("Capital of France?", "Paris"),
  makeCase("What is 2+2?", "4"),
];

test("runEval with pre-generated outputs", async () => {
  const report = await runEval(cases, new ExactMatchScorer(), { outputs: ["Paris", "4"] });
  expect(report.results.every((r) => r.passed)).toBe(true);
});

test("runEval partial pass", async () => {
  const report = await runEval(cases, new ExactMatchScorer(), { outputs: ["Paris", "wrong"] });
  expect(report.results.filter((r) => r.passed)).toHaveLength(1);
});

test("runEval with modelFn", async () => {
  const report = await runEval(
    [makeCase("ping", "pong")],
    new ExactMatchScorer(),
    { modelFn: () => "pong" },
  );
  expect(report.results[0].passed).toBe(true);
});

test("runEval async modelFn", async () => {
  const report = await runEval(
    [makeCase("ping", "pong")],
    new ExactMatchScorer(),
    { modelFn: async () => "pong" },
  );
  expect(report.results[0].passed).toBe(true);
});

test("runEval throws without modelFn or outputs", async () => {
  // @ts-expect-error intentional: testing runtime validation
  await expect(runEval(cases, new ExactMatchScorer(), {})).rejects.toThrow();
});

test("runEval throws on length mismatch", async () => {
  await expect(
    runEval(cases, new ExactMatchScorer(), { outputs: ["only one"] }),
  ).rejects.toThrow();
});

test("runEval empty dataset", async () => {
  const report = await runEval([], new ExactMatchScorer(), { outputs: [] });
  expect(report.results).toHaveLength(0);
});

test("compare baseline vs candidate", async () => {
  const [base, cand] = await compare(
    [makeCase("Capital of France?", "Paris")],
    new ExactMatchScorer(),
    () => "Lyon",
    () => "Paris",
  );
  expect(base.results[0].passed).toBe(false);
  expect(cand.results[0].passed).toBe(true);
});
