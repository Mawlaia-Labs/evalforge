import { readFileSync } from "fs";
import { EvalCase } from "../models";

interface RawCase {
  input:            string;
  expected?:        string;
  expected_output?: string;
  metadata?:        Record<string, unknown>;
  tags?:            string[];
}

function fromDict(d: RawCase): EvalCase {
  return {
    input:    d.input,
    expected: d.expected ?? d.expected_output,
    metadata: d.metadata ?? {},
    tags:     d.tags ?? [],
  };
}

export interface Dataset {
  name:  string;
  cases: EvalCase[];
}

export function fromJSON(path: string): Dataset {
  const raw  = JSON.parse(readFileSync(path, "utf-8"));
  const name = path.replace(/.*\//, "").replace(/\.json$/, "");
  if (Array.isArray(raw)) {
    return { name, cases: (raw as RawCase[]).map(fromDict) };
  }
  return {
    name:  raw.name ?? name,
    cases: (raw.cases as RawCase[]).map(fromDict),
  };
}

export function fromJSONL(path: string): Dataset {
  const lines = readFileSync(path, "utf-8").split("\n").filter((l) => l.trim());
  return {
    name:  path.replace(/.*\//, "").replace(/\.jsonl$/, ""),
    cases: lines.map((l) => fromDict(JSON.parse(l) as RawCase)),
  };
}

export function fromCSV(path: string): Dataset {
  const text   = readFileSync(path, "utf-8");
  const lines  = text.split("\n").filter((l) => l.trim());
  const header = lines[0].split(",").map((h) => h.trim());
  const cases  = lines.slice(1).map((line) => {
    const values: Record<string, string> = {};
    line.split(",").forEach((v, i) => { values[header[i]] = v.trim(); });
    return fromDict(values as unknown as RawCase);
  });
  return {
    name:  path.replace(/.*\//, "").replace(/\.csv$/, ""),
    cases,
  };
}

export function load(path: string): Dataset {
  if (path.endsWith(".json"))  return fromJSON(path);
  if (path.endsWith(".jsonl")) return fromJSONL(path);
  if (path.endsWith(".csv"))   return fromCSV(path);
  throw new Error(`Unsupported format: ${path}. Use .json, .jsonl, or .csv`);
}
