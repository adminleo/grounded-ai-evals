"""End-to-end run on synthetic data:  python3 examples/run_example.py

The numbers below are invented to show the shape of the output. The point of
the example is the last two lines: a system that looks good on average is
blocked by one check, and the gate names it.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from gaeval.metrics import (abstention, answer_accuracy, citation_precision,
                            citation_recall, cohens_kappa,
                            provenance_coverage, unsupported_rate)
from gaeval.scorecard import Check, LOWER, Scorecard, standard_layers

here = pathlib.Path(__file__).parent
data = json.loads((here / "synthetic_run.json").read_text())

answers = data["answers"]
statements = [s for a in answers for s in a.get("statements", [])]
rate, held_right, held_wrong = abstention(answers)

card = Scorecard(system="example-assistant",
                 version="v0.3.0",
                 dataset_version=data["dataset_version"])
graph, ontology, grounded, baseline = standard_layers(card)

graph.add(
    Check("provenance coverage", provenance_coverage(data["nodes"]), 0.95,
          gating=True, note="every node resolves to a citable source"),
    Check("stale nodes", data["graph"]["stale_share"], 0.10, LOWER,
          note="older than the source's own refresh interval"),
)

ontology.add(
    Check("SHACL violations per 1k triples",
          data["ontology"]["shacl_violations_per_1k"], 1.0, LOWER,
          gating=True),
    Check("competency questions answerable",
          data["ontology"]["competency_questions_answerable"], 0.90,
          note="the questions the schema was designed to answer"),
)

grounded.add(
    Check("citation precision", citation_precision(statements), 0.90,
          gating=True),
    Check("citation recall", citation_recall(statements), 0.85),
    Check("unsupported rate", unsupported_rate(statements), 0.05, LOWER,
          gating=True),
    Check("accuracy when answering", answer_accuracy(answers), 0.80),
    Check("wrong abstentions", held_wrong, 0.25, LOWER,
          note="abstained although evidence existed"),
    Check("judge agreement (kappa)",
          cohens_kappa(data["calibration"]["human"],
                       data["calibration"]["judge"]), 0.70,
          gating=True, note="automated judge vs human labels"),
)

baseline.add(
    Check("win rate vs plain model", data["baselines"]["vs_plain_llm"], 0.60),
    Check("win rate vs standard RAG", data["baselines"]["vs_rag"], 0.55),
)

print(card.render())
ok, blockers = card.gate()
print(f"gate: {'PASS' if ok else 'BLOCKED'}")
for b in blockers:
    arrow = "≥" if b.direction == "higher_is_better" else "≤"
    print(f"  blocker: {b.name} = {b.value:.3f} (needs {arrow} {b.threshold})")
