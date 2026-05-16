import { writeFileSync, mkdirSync } from "fs";
import { join } from "path";
import { tmpdir } from "os";
import { fromJSON, fromJSONL, fromCSV, load } from "../src/datasets/loaders";

function tmpFile(name: string, content: string): string {
  const dir  = tmpdir();
  const path = join(dir, name);
  writeFileSync(path, content, "utf-8");
  return path;
}

test("fromJSON array", () => {
  const p  = tmpFile("evals.json", JSON.stringify([
    { input: "2+2?", expected: "4" },
    { input: "Capital of France?", expected: "Paris", tags: ["geo"] },
  ]));
  const ds = fromJSON(p);
  expect(ds.cases).toHaveLength(2);
  expect(ds.cases[1].expected).toBe("Paris");
  expect(ds.cases[1].tags).toContain("geo");
});

test("fromJSON named object", () => {
  const p  = tmpFile("named.json", JSON.stringify({ name: "my-evals", cases: [{ input: "hi" }] }));
  const ds = fromJSON(p);
  expect(ds.name).toBe("my-evals");
});

test("fromJSONL", () => {
  const p  = tmpFile("evals.jsonl", '{"input":"q1","expected":"a1"}\n{"input":"q2","expected":"a2"}\n');
  const ds = fromJSONL(p);
  expect(ds.cases).toHaveLength(2);
  expect(ds.cases[0].input).toBe("q1");
});

test("fromCSV", () => {
  const p  = tmpFile("evals.csv", "input,expected\n2+2,4\n3+3,6\n");
  const ds = fromCSV(p);
  expect(ds.cases).toHaveLength(2);
  expect(ds.cases[1].expected).toBe("6");
});

test("load dispatches by extension", () => {
  const p  = tmpFile("test.jsonl", '{"input":"hi","expected":"hello"}\n');
  const ds = load(p);
  expect(ds.cases).toHaveLength(1);
});

test("load throws on unsupported extension", () => {
  const p = tmpFile("test.txt", "unsupported");
  expect(() => load(p)).toThrow(".txt");
});

test("missing expected is undefined", () => {
  const p  = tmpFile("noe.json", JSON.stringify([{ input: "hello" }]));
  const ds = fromJSON(p);
  expect(ds.cases[0].expected).toBeUndefined();
});
