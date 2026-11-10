# grounded-ai-evals

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24100702.svg)](https://doi.org/10.5281/zenodo.24100702)
[![tests](https://github.com/adminleo/grounded-ai-evals/actions/workflows/tests.yml/badge.svg)](https://github.com/adminleo/grounded-ai-evals/actions/workflows/tests.yml)

A four-layer method for evaluating AI systems that are supposed to answer **with
evidence** — retrieval-augmented assistants, knowledge-graph question answering,
GraphRAG-style pipelines — plus a small dependency-free Python library that
computes the metrics and renders a release gate.

The library is ~400 lines of standard library. The method is the interesting part.

```bash
git clone https://github.com/adminleo/grounded-ai-evals
cd grounded-ai-evals
python3 examples/run_example.py          # synthetic run, prints a scorecard
python3 -m unittest discover -s tests    # 18 tests
```

## Why another eval framework

Most evaluation of retrieval systems measures the last step only: given some
retrieved text, was the answer good? That misses where grounded systems actually
fail. A confident, well-cited, fluent answer built on a stale graph node is
wrong, and no answer-level metric will tell you.

So the checks are ordered, and each layer is only meaningful once the one above
it holds:

| Layer | Question | Fails when |
|---|---|---|
| **1 — Graph correctness** | Is what we stored true, sourced, current? | Extraction errors, missing provenance, stale nodes |
| **2 — Ontology hygiene** | Is the schema consistent, and does it answer what it was built for? | Constraint violations, unsatisfiable classes, competency questions the schema cannot express |
| **3 — Answer groundedness** | Does every claim trace to a source that carries it? | Decorative citations, uncited claims, confident guessing |
| **4 — Baseline comparison** | Is this better than a plain model and ordinary RAG? | All the complexity bought nothing |

Running them in this order saves time in the most boring possible way: a
citation-precision score computed over a graph with 80% provenance coverage is
not measuring the answer layer, it is measuring the graph. You will tune
prompts for a week and move nothing.

Layer 4 is last on purpose. A system that beats its baselines while failing
layer 1 has only learned to be wrong faster.

## The two design rules

**A threshold is set before the run, or it is not a threshold.** `Check`
requires the measured value *and* the bar in the same constructor call, so a
scorecard cannot be assembled afterwards to flatter the result. An unmeasured
check fails closed rather than being quietly skipped.

**One gating failure blocks the release, whatever the average says.** There is
deliberately no weighted overall score. Weighted means hide exactly the failure
you need to see — a 0.91 composite can contain a 0.40 unsupported-claim rate.
`Scorecard.gate()` ignores the mean entirely and returns the named blockers.

The example output shows why this matters: the synthetic system beats both
baselines and still gets blocked, by name, on three checks.

## Metrics

All in [`gaeval/metrics.py`](gaeval/metrics.py), all plain functions over plain
dicts, so anyone can recompute them — including someone checking your claims,
which is the point.

- **`citation_precision`** — of all citations made, how many support their
  statement. Catches decorative citation, where a plausible source is attached
  to a sentence it does not carry. ([ALCE](https://arxiv.org/abs/2305.14627)-style.)
- **`citation_recall`** / **`unsupported_rate`** — of the statements that need
  evidence, how many have one. Statements marked `needs_evidence: False` are
  excluded rather than counted as failures.
- **`abstention`** — returns the rate *split into* correct abstention (no
  evidence existed) and wrong abstention (it did). Reporting the split is what
  stops the obvious gaming: a system that abstains on everything has a perfect
  unsupported rate and is useless.
- **`answer_accuracy`** — over non-abstained answers only, so caution cannot
  inflate it.
- **`provenance_coverage`** — share of nodes carrying a resolvable source.
  Measured on the graph, before any question is asked.
- **`cohens_kappa`** — judge agreement against human labels, corrected for
  chance.

### Calibrate the judge before you trust it

If an LLM grades the answers, the grader is part of the system under test. Label
a stratified sample by hand, run the judge over the same sample, and report
Cohen's kappa — not raw agreement.

Raw agreement flatters a skewed set. When 90% of statements are supported, a
judge that answers "supported" every time scores 0.90 agreement and a kappa near
zero. The kappa is the honest number. There is a test asserting exactly this
case in [`tests/test_metrics.py`](tests/test_metrics.py).

Keep the judge deterministic, version the judge prompt alongside the dataset,
and re-calibrate when either changes.

## Build the dataset before reaching for benchmarks

Public benchmarks are useful for comparison and useless as a target. Start with
a few hundred questions from your own domain, each with an expected answer and
the source that carries it, including questions whose correct answer is *"the
evidence does not support an answer"* — a grounded system that cannot abstain is
not grounded, and no public set will contain your abstention cases.

Version the set, never fix a question because the system got it wrong, and keep
a held-out slice the people tuning prompts cannot see.

Then add public benchmarks for the layers they cover well — see
[`docs/references.md`](docs/references.md) for the standards and benchmarks this
method leans on (SHACL, OWL, OOPS!, OAEI, ALCE, FActScore, RAGAS, BFCL, τ-bench).

## Documentation

- [`docs/layers.md`](docs/layers.md) — what to measure in each layer
- [`docs/ontology-checklist.md`](docs/ontology-checklist.md) — competency
  questions and constraint checking
- [`docs/eu-ai-act.md`](docs/eu-ai-act.md) — which articles this evidence serves
- [`docs/references.md`](docs/references.md) — standards and benchmarks

## Scope

This is a methodology repository with a reference implementation. It is
deliberately framework-agnostic and contains no retrieval, no graph store and no
model calls — bring your own, emit the numbers, feed them in.

Written from production experience building grounded answering over knowledge
graphs; the method generalises, which is why it is published without any part of
that system.

## Citing this

Archived on Zenodo. The DOI above resolves to the latest version; cite a
specific one from its own record if you need the exact code you ran.

> Bornhäußer, L. (2026). *grounded-ai-evals: a four-layer method for evaluating
> AI systems that answer with evidence*. Zenodo.
> https://doi.org/10.5281/zenodo.24100702

[`CITATION.cff`](CITATION.cff) carries the machine-readable form; GitHub's
"Cite this repository" button reads it.

## License

Apache-2.0 — see [LICENSE](LICENSE).
