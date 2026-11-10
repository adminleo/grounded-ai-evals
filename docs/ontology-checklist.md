# Ontology hygiene checklist

An ontology can be perfectly consistent and still useless, because consistency
says nothing about whether it answers the questions it exists for. Check both.

## 1. Competency questions first

Write the questions the schema must answer, in plain language, before touching
the schema — then keep them in version control next to it.

For each question, record whether the schema can express it, which classes and
properties it needs, and a query that answers it. The share that are answerable
is your coverage metric.

Two failure modes this surfaces that nothing else does:

- **Modelled for the data, not the questions.** Everything in the source is
  faithfully represented and the question still cannot be asked.
- **Right in isolation, unjoinable in practice.** Each class is defensible, but
  no path connects the two ends of the question.

When a question is unanswerable, that is a schema finding, not a query problem.
Resist the urge to rewrite the question.

## 2. Constraint checking

Express the rules that must hold as SHACL shapes (or ShEx) and run them in CI:
cardinality, datatypes, value ranges, required provenance, controlled
vocabularies, referential integrity.

Report violations per 1k triples rather than as an absolute count, or the metric
moves every time the graph grows and tells you nothing about whether quality
changed.

## 3. Logical consistency

Run an OWL reasoner and look for unsatisfiable classes, contradictions, and
unintended inferences. The third is the interesting one: a domain or range
declaration that silently classifies half the graph as something it is not.

Treat a reasoner timeout as a finding. Either the ontology is more complex than
it needs to be, or the profile is wrong for the job.

## 4. Modelling pitfalls

[OOPS!](https://oops.linkeddata.es/) catches the recurring mistakes — missing
inverses, confusing a class with an instance, cycles in the hierarchy, missing
annotations, misused `owl:equivalentClass`. Worth running once per release; most
findings are cheap to fix and a handful are genuinely load-bearing.

## 5. Mapping quality

If you align to external vocabularies, measure the alignment: precision and
recall against a hand-checked reference, as the
[OAEI](https://oaei.ontologymatching.org/) campaigns do.

Two mappings to watch specifically, because both are wrong in ways that are hard
to see later: `owl:sameAs` asserted on a name match, and a hierarchy flattened
to make a join work.

## 6. Document the decisions

For each non-obvious modelling choice, record the alternatives and why this one
won. Six months later this is the difference between changing the schema and
rebuilding it — and it is also the artifact an auditor asks for first.
