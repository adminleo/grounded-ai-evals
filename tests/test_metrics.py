"""Run with:  python3 -m unittest discover -s tests -v"""
import math
import unittest

from gaeval.metrics import (abstention, answer_accuracy, citation_precision,
                            citation_recall, cohens_kappa,
                            provenance_coverage, unsupported_rate)
from gaeval.scorecard import Check, HIGHER, LOWER, Scorecard, standard_layers


def stmt(needs=True, *cits):
    return {"needs_evidence": needs,
            "citations": [{"supports": s} for s in cits]}


class Citations(unittest.TestCase):
    def test_precision_counts_every_citation_not_every_statement(self):
        # one statement, three citations, one of them decorative
        s = [stmt(True, True, True, False)]
        self.assertAlmostEqual(citation_precision(s), 2 / 3)

    def test_recall_needs_only_one_good_citation_per_statement(self):
        s = [stmt(True, False, True), stmt(True, False)]
        self.assertAlmostEqual(citation_recall(s), 0.5)

    def test_statements_not_needing_evidence_are_excluded(self):
        # a restatement of the question must not count as a miss
        s = [stmt(True, True), stmt(False)]
        self.assertEqual(citation_recall(s), 1.0)

    def test_uncited_statement_is_a_recall_miss(self):
        self.assertEqual(citation_recall([stmt(True)]), 0.0)
        self.assertEqual(unsupported_rate([stmt(True)]), 1.0)

    def test_no_citations_at_all_gives_nan_precision_not_zero(self):
        # nothing was claimed, so precision is undefined rather than perfect
        self.assertTrue(math.isnan(citation_precision([stmt(True)])))


class Abstention(unittest.TestCase):
    def test_split_separates_caution_from_correctness(self):
        answers = [
            {"abstained": True, "evidence_existed": False},   # right call
            {"abstained": True, "evidence_existed": True},    # over-cautious
            {"abstained": False, "correct": True},
        ]
        rate, correct, wrong = abstention(answers)
        self.assertAlmostEqual(rate, 2 / 3)
        self.assertAlmostEqual(correct, 0.5)
        self.assertAlmostEqual(wrong, 0.5)

    def test_accuracy_ignores_abstentions(self):
        # refusing to answer must not raise accuracy
        answers = [{"abstained": True}, {"abstained": False, "correct": True}]
        self.assertEqual(answer_accuracy(answers), 1.0)
        self.assertTrue(math.isnan(answer_accuracy([{"abstained": True}])))


class Judge(unittest.TestCase):
    def test_kappa_is_near_zero_for_a_judge_that_always_agrees(self):
        # the skew trap: 90% raw agreement, no actual skill
        human = ["supported"] * 9 + ["unsupported"]
        judge = ["supported"] * 10
        self.assertLess(cohens_kappa(human, judge), 0.01)

    def test_kappa_is_one_on_perfect_agreement_with_variance(self):
        labels = ["supported", "unsupported", "supported", "unsupported"]
        self.assertAlmostEqual(cohens_kappa(labels, list(labels)), 1.0)

    def test_kappa_is_negative_when_worse_than_chance(self):
        a = ["supported", "unsupported"] * 3
        b = ["unsupported", "supported"] * 3
        self.assertLess(cohens_kappa(a, b), 0)

    def test_mismatched_lengths_are_rejected(self):
        with self.assertRaises(ValueError):
            cohens_kappa(["a"], ["a", "b"])


class Graph(unittest.TestCase):
    def test_provenance_coverage(self):
        nodes = [{"source": "s1"}, {"source": None}, {"source": "s2"}]
        self.assertAlmostEqual(provenance_coverage(nodes), 2 / 3)


class Scorecards(unittest.TestCase):
    def test_lower_is_better_direction(self):
        self.assertTrue(Check("x", 0.03, 0.05, LOWER).passed)
        self.assertFalse(Check("x", 0.07, 0.05, LOWER).passed)

    def test_unmeasured_check_fails_closed(self):
        c = Check("x", float("nan"), 0.9)
        self.assertFalse(c.passed)
        self.assertEqual(c.status, "not measured")

    def test_bad_direction_is_rejected_at_construction(self):
        with self.assertRaises(ValueError):
            Check("x", 1.0, 0.5, "bigger")

    def test_one_gating_failure_blocks_however_good_the_rest_is(self):
        card = Scorecard("s", "v1", "ds")
        g, _, a, _ = standard_layers(card)
        g.add(Check("a", 1.0, 0.9, gating=True),
              Check("b", 1.0, 0.9, gating=True))
        a.add(Check("unsupported", 0.9, 0.05, LOWER, gating=True))
        ok, blockers = card.gate()
        self.assertFalse(ok)
        self.assertEqual([c.name for c in blockers], ["unsupported"])

    def test_non_gating_failure_does_not_block(self):
        card = Scorecard("s", "v1", "ds")
        card.layer("l", "?").add(Check("nice to have", 0.1, 0.9))
        self.assertTrue(card.gate()[0])

    def test_render_marks_the_failure(self):
        card = Scorecard("s", "v1", "ds")
        card.layer("l", "?").add(Check("x", 0.1, 0.9, HIGHER, gating=True))
        md = card.render()
        self.assertIn("BLOCKED", md)
        self.assertIn("FAIL", md)


if __name__ == "__main__":
    unittest.main()
