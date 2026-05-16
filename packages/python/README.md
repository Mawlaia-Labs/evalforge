# evalforge

> Eval runner for LLM applications. CI-native AI quality.

Your code has tests. Your prompts don't. **evalforge** brings the same quality gates you have for code to your LLM features — run on every PR, catch regressions before they reach production.

```python
from evalforge import EvalDataset, run_eval
from evalforge.scorers import llm_judge, exact_match

dataset = EvalDataset.from_json("evals/rag_quality.json")

report = run_eval(
    dataset=dataset,
    model="claude-3-5-sonnet",
    scorers=[llm_judge(rubric="Is the answer accurate and grounded?"), exact_match()],
)

report.assert_pass(threshold=0.85)  # fails CI if score drops below 85%
```

## Status

🚧 **Early development.** Star to follow progress.

## What it does

- **Eval runner** — LLM-as-judge, exact match, ROUGE, semantic similarity, custom Python scorers
- **CI integration** — GitHub Actions native, fails the build if quality drops
- **Dataset versioning** — store, version, and sample eval sets
- **Comparison mode** — A/B test prompts and models against a baseline
- **Shadow traffic** — route production traffic to a new model and compare live
- **Vertical eval packs** — pre-built datasets and scorers for RAG, customer support, code generation, legal, medical

## Roadmap

- [ ] Python SDK
- [ ] CLI
- [ ] GitHub Actions action
- [ ] Hosted control plane ([mawlaia.com](https://mawlaia.com))
- [ ] Vertical eval packs

## License

MIT
