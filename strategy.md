# AI Evaluation & Quality Infrastructure — Strategy & Development Plan

*Opportunity #5 from infrastructure_opportunities.md*
*"GitHub Actions for AI quality"*

---

## 1. Market Opportunity

### Problem
Observability tools (Langfuse, Helicone, LangSmith) tell you what your AI did. Evaluation tells you whether it was *correct*. Every AI team discovers this gap within 2–3 months of shipping — when they realize their product is regressing silently and they have no systematic way to catch it before deployment.

### Market size
- Every company shipping AI products is a potential customer.
- The AI-shipping startup population is exploding: 10,000+ companies with active AI features in 2026, scaling to 50,000+ by 2028.
- Realistic SOM at 3 years: 500–2000 paying teams × €200–3000/month = €1.2M–72M ARR.
- Enterprise expands ceiling: large engineering orgs run thousands of eval jobs/month.

### Forcing functions
- **AI in production is normalizing** — every company that shipped AI in 2024–2025 is now on their second or third iteration and hitting quality issues
- **Regulatory pressure** — EU AI Act high-risk system requirements mandate documented quality assurance processes
- **LLM provider churn** — teams switching between models need regression testing to validate equivalence
- **Prompt engineering maturation** — teams that optimized prompts empirically now need to protect those gains
- **CI/CD culture** — engineers expect quality gates before deployment; AI is the last domain without them

### Buyer profile
- **Primary:** ML Engineer or AI Lead at a Series A–C startup (the person writing prompts and managing model versions)
- **Secondary:** Head of Engineering (after a production incident caused by an undiscovered regression)
- **Tertiary:** VP Product (needs visibility into AI feature quality without reading logs)
- **Budget:** €200–2000/month self-serve; €5K–30K/year enterprise

---

## 2. Competition Landscape

| Player | Positioning | Gap |
|---|---|---|
| **Braintrust** | Hosted eval platform, good DX | Closed-source, complex pricing, no strong CI/CD integration, limited vertical packs |
| **Patronus AI** | Automated LLM testing | Enterprise-focused, limited self-serve, opaque pricing |
| **Galileo** | AI quality + observability bundle | Enterprise only, expensive, no open-source |
| **Confident AI / DeepEval** | Open-source eval framework | Strong OSS but limited hosted product, UI is rough |
| **LangSmith evals** | Bundled with LangChain observability | Secondary feature, not primary product; requires LangChain stack |
| **Langfuse evals** | Bundled with Langfuse observability | Same issue — secondary feature, limited eval depth |
| **Promptfoo** | Open-source LLM testing | CLI-only, no hosted product, no dataset management |
| **Arize AI** | ML observability + evals | Expensive, complex, originally non-LLM MLOps |
| **Ragas** | Open-source RAG evaluation | RAG-only, no hosted service, no CI integration |

### Competitive gap
No product owns the position: **open-source eval framework + hosted control plane + CI/CD integration + vertical eval packs**, with per-eval-run pricing and no observability vendor lock-in. The market is fragmented between "good OSS with bad hosted" (DeepEval, Promptfoo) and "good hosted with vendor lock-in" (Braintrust, LangSmith).

### Defensibility
- **Dataset accumulation:** customer eval datasets, regression history, and labeled edge cases build switching cost over time
- **Vertical eval packs:** pre-built packs for specific use cases (RAG, legal, medical, code) are hard to replicate quickly
- **CI integration stickiness:** once eval gates are wired into CI pipelines, removing them is painful
- **Community:** open-source community generates feedback, eval packs, and integrations faster than any solo team

---

## 3. Customer Needs Map

### Jobs to be done
1. **"I changed the prompt and don't know if it got better or worse"** — A/B eval comparison
2. **"We swapped GPT-4o for Claude 3.5 Sonnet — need to validate equivalence"** — model migration testing
3. **"Our RAG quality dropped and we don't know why"** — RAG evaluation (retrieval + generation)
4. **"I need to block a deploy if AI quality falls below threshold"** — CI/CD gate
5. **"Our lawyers need documented quality assurance for our AI feature"** — audit-ready eval reports
6. **"I need non-engineers (doctors, lawyers) to review AI outputs"** — SME annotation interface

### Integration points
- CI/CD: GitHub Actions, GitLab CI, CircleCI
- LLM providers: OpenAI, Anthropic, Google, Cohere, open-source models (via API)
- Observability: Langfuse, Helicone (emit eval results back to existing dashboards)
- Frameworks: LangChain, LlamaIndex, Vercel AI SDK, raw API
- Dataset storage: own format + import from CSV/JSON/JSONL

### Must-have on day one
- Python SDK with `run_eval(dataset, scorer)` interface
- LLM-as-judge scorer (GPT-4o or Claude evaluating outputs)
- Programmatic scorers (ROUGE, exact match, regex, custom functions)
- GitHub Actions integration: eval runs on PR, fails if score drops
- Dataset versioning (store, version, sample eval sets)
- Free tier: 500 eval runs/month free

---

## 4. Staged Development Plan

### Phase 0 — Open-source eval runner (weeks 1–4)
**Goal:** be the canonical answer when developers search "how to eval my LLM app"

- [ ] Open-source `evalforge` (or similar name) monorepo
- [ ] Python SDK: `EvalDataset`, `EvalCase`, `run_eval(dataset, scorer, model)` → `EvalReport`
- [ ] Built-in scorers: LLM-as-judge (GPT-4o/Claude), exact match, ROUGE-L, semantic similarity (cosine), regex, custom Python function
- [ ] Dataset formats: JSON, JSONL, CSV, Hugging Face datasets import
- [ ] CLI: `evalforge run --dataset my_evals.json --scorer llm-judge`
- [ ] Comparison mode: `evalforge compare --baseline gpt-4o --candidate claude-3-5-sonnet`
- [ ] README with "Why eval matters" + clear comparison vs DeepEval/Promptfoo
- [ ] Publish: GitHub, PyPI, HN Show HN, Twitter/X thread

**Success metric:** 300+ GitHub stars, 1000+ PyPI downloads/week, 5 design partner convos

---

### Phase 1 — Hosted control plane + CI (months 1–3)
**Goal:** first paying customers via CI integration

- [ ] Hosted web app: dataset management, eval run history, score trends over time
- [ ] GitHub Actions action: `evalforge/run-evals@v1` — triggers eval run, posts results as PR comment
- [ ] Eval run comparison view: side-by-side output diff with scores
- [ ] Score trend charts: track quality over time per dataset/model/prompt version
- [ ] Slack/email notifications on score regression
- [ ] Vertical eval pack #1: **RAG quality** — retrieval precision/recall, answer faithfulness, context relevance
- [ ] Free tier: 500 eval runs/month, 3 datasets
- [ ] Pro tier: €49/month, 5000 runs, unlimited datasets, CI integration

**Success metric:** 10 paying teams, €500–2000 MRR, 1 recognized brand as design partner

---

### Phase 2 — Shadow traffic + annotation (months 3–6)
**Goal:** cover the "production quality" use case

- [ ] Shadow traffic comparison: route X% of production traffic to new model/prompt, compare against baseline in real-time
- [ ] Drift detection: alert when production output distribution shifts from eval baseline
- [ ] SME annotation interface: non-engineer reviewers can rate outputs on custom rubrics (lawyer rates legal summaries, doctor rates medical extractions)
- [ ] Vertical eval pack #2: **customer support quality** — tone, resolution rate, escalation detection, CSAT prediction
- [ ] Vertical eval pack #3: **code generation** — correctness (run tests), security (static analysis), style
- [ ] LangChain / LlamaIndex native callbacks (emit eval events automatically)
- [ ] Langfuse / Helicone integration (push eval scores into existing observability dashboards)
- [ ] SOC 2 Type I process started

**Success metric:** 40–80 paying teams, €8K–15K MRR

---

### Phase 3 — Vertical expansion + compliance (months 6–12)
**Goal:** win regulated verticals, start raising

- [ ] Vertical eval pack #4: **legal document QA** — factual accuracy, citation correctness, hallucination detection
- [ ] Vertical eval pack #5: **medical summarization** — clinical accuracy, omission detection, safety flags
- [ ] HIPAA-compatible eval storage (for healthcare customers running evals on patient data)
- [ ] SOC 2 Type II
- [ ] Enterprise tier: €500+/month, custom eval packs, SLA, dedicated support
- [ ] API for embedding eval results in customer-facing quality dashboards
- [ ] Seed raise: target €1–2M

**Success metric:** 150–300 paying teams, €30–50K MRR

---

### Phase 4 — Platform (months 12–24)
**Goal:** become the AI quality standard

- [ ] Bundle with PII Vault (#2) and Guardrails (#7) — "AI middleware platform"
- [ ] Eval marketplace: community-contributed eval packs (monetize as add-ons)
- [ ] Automated eval generation: given a system prompt + sample outputs, auto-generate an eval dataset
- [ ] Model leaderboards for private models: customers benchmark internal fine-tunes against frontier models
- [ ] ISO 42001 alignment certification
- [ ] Series A raise

---

## 5. Zero-to-revenue path (bootstrap)

**Week 1–4:** publish open-source SDK → GitHub stars → developer community
**Month 2:** hosted MVP + GitHub Actions → convert 5–10 design partners to €49/month
**Month 3:** 15 paying teams, €750 MRR → refine RAG eval pack (most common ask)
**Month 4–5:** 50 teams, €5K MRR → shadow traffic feature → enterprise conversations begin
**Month 6:** €10K MRR → SOC 2 started → seed-raise ready

**Infrastructure cost at €10K MRR:** ~€300–600/month (Supabase + Vercel + LLM API costs for judge)

---

## 6. Tech stack recommendation

- **Eval runner:** Python library (primary) + TypeScript for web SDK
- **Hosted backend:** FastAPI + Postgres (Supabase or RDS)
- **Eval job queue:** BullMQ (Redis) or Celery for async eval runs
- **Frontend:** Next.js on Vercel
- **LLM judge calls:** Anthropic Claude (best instruction-following for eval rubrics)
- **CI action:** GitHub Actions YAML wrapper around `evalforge run`
- **Storage:** S3/R2 for dataset files

---

*Last updated: 2026-05-15*
