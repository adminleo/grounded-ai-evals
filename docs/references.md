# Standards and benchmarks

The method does not invent metrics where a public one exists. Prefer the
standard, then add domain-specific checks for the gaps.

## Ontology and graph

- **SHACL** — W3C Shapes Constraint Language, for the rules that must hold:
  <https://www.w3.org/TR/shacl/>
- **ShEx** — Shape Expressions, an alternative with a more compact syntax:
  <https://shex.io/>
- **OWL 2** — profiles matter for whether a reasoner terminates:
  <https://www.w3.org/TR/owl2-overview/>
- **OOPS!** — OntOlogy Pitfall Scanner, catalogue of recurring modelling
  mistakes: <https://oops.linkeddata.es/>
- **OAEI** — Ontology Alignment Evaluation Initiative, for how to evaluate
  mappings between vocabularies: <https://oaei.ontologymatching.org/>
- **PROV-O** — provenance vocabulary, if you need provenance to be queryable
  rather than a string field: <https://www.w3.org/TR/prov-o/>

## Citation and faithfulness

- **ALCE** — "Enabling Large Language Models to Generate Text with Citations"
  (Gao et al., 2023), the source of citation precision and recall as used here:
  <https://arxiv.org/abs/2305.14627>
- **FActScore** — atomic-fact decomposition for long-form factuality
  (Min et al., 2023): <https://arxiv.org/abs/2305.14251>
- **RAGAS** — faithfulness, answer relevance and context metrics for RAG
  pipelines (Es et al., 2023): <https://arxiv.org/abs/2309.15217>
- **Attributed QA** — "Measuring Attribution in Natural Language Generation
  Models" (Rashkin et al., 2021) on what "attributable to a source" means
  precisely enough to annotate: <https://arxiv.org/abs/2112.12870>

## Retrieval

- **BEIR** — zero-shot retrieval across domains, for the retrieval step in
  isolation: <https://arxiv.org/abs/2104.08663>
- **KILT** — knowledge-intensive tasks with provenance:
  <https://arxiv.org/abs/2009.02252>
- **HotpotQA** / **MuSiQue** — multi-hop question answering, the class where
  graph approaches should win if they win anywhere.

## Tools and agents

- **BFCL** — Berkeley Function Calling Leaderboard, for tool selection and
  argument correctness: <https://gorilla.cs.berkeley.edu/leaderboard.html>
- **τ-bench** — tool-agent-user interaction in realistic domains, including
  whether the agent respects confirmation requirements:
  <https://arxiv.org/abs/2406.12045>

## Judging

- **"Judging LLM-as-a-Judge"** (Zheng et al., 2023) — the known biases:
  position, verbosity, self-preference:
  <https://arxiv.org/abs/2306.05685>
- **Cohen's kappa** — chance-corrected agreement; use it rather than raw
  agreement whenever the label distribution is skewed, which is nearly always.

## Regulation

- **Regulation (EU) 2024/1689** (AI Act), consolidated text:
  <https://eur-lex.europa.eu/eli/reg/2024/1689/oj>
- **ISO/IEC 42001** — AI management systems, if you need the quality-management
  framing rather than the article-by-article one.
