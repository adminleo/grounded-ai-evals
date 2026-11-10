# Which articles this evidence serves

Not legal advice. This is a map from the measurements in this repository to the
places a conformity discussion tends to ask for them, written so an engineering
team and a compliance reviewer can look at the same table.

Scope note: obligations depend on your role (provider, deployer, importer) and
on whether the system is classified high-risk at all. Most retrieval assistants
are not. Establish that first — the mapping below is about *what evidence
exists* if it is asked for, not an assertion that it must be.

Timelines and implementing guidance under Regulation (EU) 2024/1689 have moved
more than once since adoption. Check the current position rather than relying on
a date in a README, including this one.

| Area | Articles | What this method produces |
|---|---|---|
| Risk management | Art. 9 | Named failure modes per layer with thresholds set in advance; the gate record showing which releases were blocked and why |
| Data governance | Art. 10 | Provenance coverage, staleness, entity-resolution error rates measured on the store itself |
| Technical documentation | Art. 11, Annex IV | Versioned dataset, versioned judge prompt, scorecard per release, the modelling decisions recorded per the ontology checklist |
| Record keeping | Art. 12 | Scorecard JSON per release, retained; a per-answer citation trail if you log it |
| Transparency to deployers | Art. 13 | Accuracy *and* abstention behaviour stated per question class, rather than one aggregate |
| Human oversight | Art. 14 | Abstention split, which tells a reviewer where the system hands off instead of guessing |
| Accuracy and robustness | Art. 15 | Layer 3 metrics plus the layer 4 baseline comparison; accuracy declared with its measurement method attached |
| Quality management | Art. 17 | A gate that blocks a release on named checks, and its history |
| Post-market monitoring | Art. 72 | The same scorecard run on production samples on a schedule, not only pre-release |

If the system is built on a general-purpose model you did not train, the GPAI
chapter (Art. 53–55) sits upstream of you. What you still owe is evidence about
*your* system: these measurements are that evidence, and they are yours to
produce regardless of what the model provider publishes.

## Two practical notes

**Declare accuracy with its method attached.** A single headline accuracy figure
is not useful to a reviewer and not defensible under scrutiny. State the dataset
version, the question classes, the judge and its calibration, and the abstention
rate alongside it. An accuracy number without an abstention rate is not an
accuracy number.

**Avoid absolute claims.** "No hallucinations" and "100% accurate" are not
supportable by any measurement procedure, including this one, and a reviewer who
finds one counterexample has grounds to discount everything else you wrote.
Report the measured rate with its dataset version and let the number carry the
argument.
