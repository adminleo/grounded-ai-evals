"""A scorecard turns a pile of metrics into a decision.

The unit is a *layer*: a group of checks that fail for the same reason and are
fixed by the same team. A layer holds checks; a check holds a measured value, a
threshold, and a direction. Nothing here knows what the values mean — that is
the point. The layers below are the ones that matter for a system answering
with evidence over a knowledge graph, but the structure is generic.

Two rules the structure enforces, both learned the expensive way:

1.  A check without a threshold set *before* the run is not a check, it is a
    reading. `Check` requires both, so a scorecard cannot be assembled after
    the fact to flatter the result.

2.  A gating check that fails fails the release, regardless of the average.
    Weighted overall scores hide exactly the failures you need to see, so
    `Scorecard.gate()` ignores the mean entirely.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict

HIGHER, LOWER = "higher_is_better", "lower_is_better"


@dataclass
class Check:
    name: str
    value: float
    threshold: float
    direction: str = HIGHER
    gating: bool = False
    note: str = ""

    def __post_init__(self):
        if self.direction not in (HIGHER, LOWER):
            raise ValueError(f"direction must be {HIGHER!r} or {LOWER!r}")

    @property
    def passed(self) -> bool:
        if self.value != self.value:                 # NaN: not measured
            return False
        return (self.value >= self.threshold if self.direction == HIGHER
                else self.value <= self.threshold)

    @property
    def status(self) -> str:
        if self.value != self.value:
            return "not measured"
        return "pass" if self.passed else "FAIL"


@dataclass
class Layer:
    name: str
    question: str
    checks: list = field(default_factory=list)

    def add(self, *checks) -> "Layer":
        self.checks.extend(checks)
        return self

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks)


@dataclass
class Scorecard:
    system: str
    version: str
    dataset_version: str
    layers: list = field(default_factory=list)

    def layer(self, name: str, question: str) -> Layer:
        l = Layer(name, question)
        self.layers.append(l)
        return l

    @property
    def checks(self):
        return [c for l in self.layers for c in l.checks]

    def gate(self):
        """Release decision. Returns (ok, blockers).

        A blocker is any failing check marked `gating`. Non-gating failures are
        reported but do not block — that distinction is what keeps a gate
        credible enough that nobody is tempted to switch it off.
        """
        blockers = [c for c in self.checks if c.gating and not c.passed]
        return not blockers, blockers

    def to_dict(self):
        return asdict(self)

    def to_json(self, **kw) -> str:
        return json.dumps(self.to_dict(), indent=2, **kw)

    def render(self) -> str:
        """Markdown table, for pasting into a release note or a PR."""
        ok, blockers = self.gate()
        out = [f"# {self.system} {self.version}",
               f"dataset `{self.dataset_version}`", "",
               f"**Gate: {'PASS' if ok else 'BLOCKED'}**"
               + (f" — {len(blockers)} blocking failure(s)" if blockers else ""),
               ""]
        for l in self.layers:
            out += [f"## {l.name}", f"_{l.question}_", "",
                    "| check | value | threshold | | |",
                    "|---|---:|---:|---|---|"]
            for c in l.checks:
                v = "—" if c.value != c.value else f"{c.value:.3f}"
                arrow = "≥" if c.direction == HIGHER else "≤"
                out.append(f"| {c.name} | {v} | {arrow} {c.threshold:.3f} "
                           f"| {c.status} | {'gate' if c.gating else ''} |")
            out.append("")
        return "\n".join(out)


def standard_layers(card: Scorecard):
    """The four layers, in the order you should build them.

    Returned empty, to be filled with your own checks and thresholds. The order
    is deliberate: each layer is meaningless until the one above it holds.

    A wrong fact in the graph cannot be fixed by better retrieval, and a
    citation metric computed over a graph with 60% provenance coverage measures
    the graph, not the answer. Benchmark comparisons come last because that is
    the only point at which they mean anything — a system that beats a baseline
    while failing layer 1 has beaten it at being wrong faster.
    """
    return (
        card.layer("1 — Graph correctness",
                   "Is what we stored true, sourced, and current?"),
        card.layer("2 — Ontology hygiene",
                   "Is the schema consistent, and does it answer the "
                   "questions it was built for?"),
        card.layer("3 — Answer groundedness",
                   "Does every claim trace to a source that carries it?"),
        card.layer("4 — Baseline comparison",
                   "Is this better than a plain model and ordinary RAG?"),
    )
