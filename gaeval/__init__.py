"""Evaluation for AI systems that answer with evidence.

See README.md for the method; the code here only computes and reports.
"""
from gaeval.metrics import (abstention, answer_accuracy, citation_precision,
                            citation_recall, cohens_kappa,
                            provenance_coverage, unsupported_rate)
from gaeval.scorecard import (Check, HIGHER, LOWER, Layer, Scorecard,
                              standard_layers)

__version__ = "0.1.0"
__all__ = ["abstention", "answer_accuracy", "citation_precision",
           "citation_recall", "cohens_kappa", "provenance_coverage",
           "unsupported_rate", "Check", "Layer", "Scorecard",
           "standard_layers", "HIGHER", "LOWER"]
