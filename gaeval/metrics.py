"""Metrics for systems that are supposed to answer *with evidence*.

Each function takes plain dicts and returns plain floats. No dependencies, so
the numbers can be recomputed anywhere — including by someone checking your
claims, which is the point.

Vocabulary used throughout:

    statement   one atomic claim inside an answer
    citation    a pointer from a statement to a source
    supported   a human or judge decided the cited source carries the statement
    abstention  the system answered "no evidence" instead of guessing
"""
from __future__ import annotations


def citation_precision(statements) -> float:
    """Of all citations made, how many actually support their statement?

    ALCE-style. Punishes decorative citations — the failure mode where a system
    attaches a plausible-looking source to a sentence it does not support.
    """
    cited = [c for s in statements for c in s.get("citations", [])]
    if not cited:
        return float("nan")
    return sum(1 for c in cited if c.get("supports")) / len(cited)


def citation_recall(statements) -> float:
    """Of the statements that need evidence, how many have at least one
    supporting citation?

    Statements marked `needs_evidence: False` (pleasantries, restatements of
    the question) are excluded rather than counted as failures.
    """
    need = [s for s in statements if s.get("needs_evidence", True)]
    if not need:
        return float("nan")
    ok = sum(1 for s in need
             if any(c.get("supports") for c in s.get("citations", [])))
    return ok / len(need)


def unsupported_rate(statements) -> float:
    """Share of evidence-bearing statements with no supporting citation.

    The complement of citation recall, reported separately because it is the
    number that matters when the promise is "every claim carries a source".
    """
    r = citation_recall(statements)
    return r if r != r else 1.0 - r          # NaN propagates


def abstention(answers):
    """Abstention behaviour, split into the two cases that mean opposite things.

    A system that abstains on everything scores a perfect unsupported-rate and
    is useless. Reporting the split is what stops that gaming.

    Returns (rate, correct, wrong):
        rate     share of questions where the system abstained
        correct  of those, share where no evidence existed  (good)
        wrong    of those, share where evidence did exist   (over-caution)
    """
    if not answers:
        return float("nan"), float("nan"), float("nan")
    held = [a for a in answers if a.get("abstained")]
    rate = len(held) / len(answers)
    if not held:
        return rate, float("nan"), float("nan")
    correct = sum(1 for a in held if not a.get("evidence_existed")) / len(held)
    return rate, correct, 1.0 - correct


def answer_accuracy(answers) -> float:
    """Share of non-abstained answers judged correct.

    Deliberately excludes abstentions: mixing them in lets a cautious system
    look accurate by refusing to answer.
    """
    said = [a for a in answers if not a.get("abstained")]
    if not said:
        return float("nan")
    return sum(1 for a in said if a.get("correct")) / len(said)


def provenance_coverage(nodes) -> float:
    """Share of graph nodes or triples that carry a resolvable source.

    A knowledge graph without provenance cannot support an evidenced answer,
    however good the retrieval is — so this is measured on the graph itself,
    before any question is asked.
    """
    if not nodes:
        return float("nan")
    return sum(1 for n in nodes if n.get("source")) / len(nodes)


def cohens_kappa(a, b) -> float:
    """Agreement between two sets of labels, corrected for chance.

    Used to calibrate an automated judge against human labels before trusting
    it. Raw agreement looks impressive on skewed data — if 90% of statements
    are supported, a judge that always says "supported" scores 0.90 agreement
    and kappa near 0, which is the honest reading.
    """
    if len(a) != len(b):
        raise ValueError("label lists must be the same length")
    if not a:
        return float("nan")
    n = len(a)
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    labels = set(a) | set(b)
    pe = sum((a.count(l) / n) * (b.count(l) / n) for l in labels)
    if pe == 1.0:
        return float("nan")                  # no variance; kappa undefined
    return (po - pe) / (1 - pe)
