# What to measure in each layer

Thresholds are deliberately absent. The right bar depends on what a wrong answer
costs in your domain, and a number copied from someone else's README is not a
threshold, it is decoration. Set yours from the cost of the failure, write it
down before the run, and change it only with a reason recorded next to it.

## Layer 1 — Graph correctness

Measured on the store, with no question asked.

- **Provenance coverage** — share of nodes or triples resolving to a citable
  source. A node without one can never support an evidenced answer, so this
  usually belongs in the gate.
- **Extraction accuracy** — sample entities and relations, check against the
  source by hand. Sampling is fine; being honest about the sample size is not
  optional.
- **Staleness** — share of nodes older than their own source's refresh interval.
  Different sources decay at wildly different rates, so a single global age
  cutoff will be wrong in both directions.
- **Entity resolution** — duplicate rate and false-merge rate, reported
  separately. They trade off against each other and a single "resolution score"
  hides which way you are failing. False merges are usually the more expensive
  direction: they invent relationships that exist in no source.
- **Link integrity** — dangling references, orphaned nodes, cycles where the
  schema forbids them.

## Layer 2 — Ontology hygiene

See [`ontology-checklist.md`](ontology-checklist.md) for the detail.

- **Constraint violations per 1k triples** — SHACL or ShEx.
- **Logical consistency** — an OWL reasoner finding unsatisfiable classes or
  contradictions.
- **Modelling pitfalls** — OOPS! catches the recurring ones, and most of them
  are the same handful of mistakes everyone makes once.
- **Competency question coverage** — share of the questions the schema was
  designed to answer that it can actually express. This is the check that most
  often reveals the schema was built for the data rather than for the questions.
- **Mapping quality**, if you align to external vocabularies — precision and
  recall against a reference alignment, OAEI-style.

## Layer 3 — Answer groundedness

- **Citation precision and recall**, plus **unsupported rate** reported on its
  own. If the promise to users is "every claim carries a source", the unsupported
  rate *is* the promise.
- **Abstention, split** into correct and wrong. Always both numbers.
- **Accuracy when answering**, over non-abstained answers only.
- **Faithfulness** — share of statements entailed by the retrieved context,
  independent of whether they are true in the world. A faithful answer over bad
  context is a layer 1 failure being correctly surfaced here, which is why the
  layers are ordered.
- **Judge agreement** — Cohen's kappa against human labels, if a model grades.

## Layer 4 — Baseline comparison

Three baselines, in increasing order of how uncomfortable they are:

1. **Plain model, no retrieval.** Surprisingly strong on anything well
   represented in pretraining. If you cannot beat it, the retrieval is not
   earning its latency.
2. **Standard RAG** — chunk, embed, top-k. The honest comparison for any graph
   approach, and the one most graph write-ups skip.
3. **A published graph pipeline**, if one applies to your data.

Report win rate per question class, not in aggregate. Graph approaches tend to
win on multi-hop and aggregation questions and lose on single-fact lookup, and
one averaged number hides both halves — including the half that tells you when
to route a question to the cheaper path.

## Layer 5 — Tool and orchestration behaviour

Only if the system calls tools. Measure correct tool selection, argument
correctness, recovery from a failed call, and refusal to act without the
required confirmation. BFCL and τ-bench cover the generic shape; anything
domain-specific needs your own scenarios.
