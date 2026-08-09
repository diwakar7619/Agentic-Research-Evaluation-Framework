# AI Engineer Visibility Research — Methodology

**Version:** 1.0 Draft
**Research period:** 2026
**Pilot sample:** 100 profiles
**Final target:** ~400 profiles
**Primary population:** Publicly visible AI-engineering practitioners with verifiable public work

---

# 1. Research Objective

Determine which **observable, evidence-backed characteristics** are associated with higher visibility among public AI-engineering profiles in 2026.

The study will specifically investigate whether characteristics such as:

* production/deployed systems
* technical documentation
* evaluation and metrics
* testing
* AI/LLM engineering technologies
* agentic workflows
* RAG
* MCP/tool integration
* open-source contributions
* consistent project activity
* problem-oriented project framing

occur more frequently among highly visible profiles than among emerging profiles.

The research will **not** claim that any observed characteristic causes career success or GitHub popularity.

---

# 2. Primary Research Question

> **Which observable characteristics differentiate highly visible AI-engineering GitHub profiles from emerging AI-engineering profiles in 2026?**

## Secondary Questions

### RQ1 — Engineering practices

Which engineering practices are most prevalent among the studied profiles?

### RQ2 — Production readiness

How frequently do profiles demonstrate evidence of:

* deployment
* APIs/services
* Docker/containerization
* testing
* CI/CD
* monitoring/observability
* evaluation/benchmarks
* documentation

### RQ3 — AI engineering technologies

How frequently do profiles demonstrate:

* RAG
* vector databases
* AI agents
* tool calling
* MCP
* LLM inference
* model serving
* multimodal AI

### RQ4 — Visibility

Which measurable visibility signals are associated with the visible group?

Signals may include:

* GitHub followers
* repository stars
* repository forks
* original repositories
* external/publication presence
* project activity

### RQ5 — Documentation

Do highly visible profiles demonstrate stronger documentation/evidence practices than emerging profiles?

### RQ6 — Shipping consistency

Do visible profiles demonstrate more sustained public activity than emerging profiles?

---

# 3. Important Scope Limitation

This study is about **publicly observable AI-engineering profiles**.

It is NOT a study of:

* all AI engineers
* all successful AI engineers
* hiring outcomes
* salary outcomes
* actual engineering ability
* private work
* private GitHub repositories
* recruiter decision-making in general

Therefore conclusions must be phrased as:

> "Among the publicly observable profiles in our sample..."

rather than:

> "AI engineers who do X are successful."

---

# 4. Population Definition

A profile is eligible for the study when all of the following are satisfied:

## P1 — Public identity

The individual has a publicly accessible professional/GitHub presence that can be independently verified.

## P2 — AI engineering relevance

The individual has publicly verifiable work involving one or more of:

* LLM applications
* generative AI
* RAG
* AI agents
* machine-learning systems
* model inference
* AI APIs/services
* AI infrastructure/tooling

## P3 — Engineering evidence

There must be evidence of actual implementation rather than only:

* reposted content
* tutorials with no original implementation
* purely theoretical content
* course completion
* certificates
* generic AI-related claims

## P4 — Public evidence

The characteristics being measured must be supported by publicly accessible evidence.

---

# 5. Exclusion Criteria

A candidate is excluded when:

* the profile has no meaningful AI-engineering work;
* evidence is primarily copied/forked work without meaningful original contribution;
* the profile is clearly spam or automated;
* the profile cannot be independently verified;
* AI relevance cannot be established from available public evidence;
* the available evidence is insufficient to classify the profile reliably.

A profile will NOT be excluded simply because it has few followers or stars.

---

# 6. Sampling Strategy

The study will use **stratified purposive sampling** rather than pretending that a list of highly visible GitHub accounts is a random sample of all AI engineers.

The purpose is to compare different levels of public visibility.

## Initial groups

### Group A — Highly visible

Profiles demonstrating strong public visibility according to predefined measurable signals.

### Group B — Emerging

Profiles demonstrating genuine AI-engineering work but substantially lower public visibility.

The exact numerical boundary between groups will be determined **before final analysis** using the documented visibility rules.

We will not continuously change the threshold to obtain a desired result.

---

# 7. Sample Size

## Pilot

The first dataset contains:

**100 profiles**

Purpose:

* test discovery strategy
* test extraction accuracy
* identify missing variables
* evaluate evidence quality
* measure false classifications
* refine the collection pipeline

The pilot is not automatically treated as the final statistical dataset.

## Final dataset

Target:

**approximately 400 profiles**

The final allocation between visibility groups will depend on the number of eligible profiles discovered under the frozen inclusion rules.

The number 400 is a practical research target, not a claim that 400 provides universal statistical certainty.

---

# 8. Sampling Principles

The following principles are mandatory:

1. Do not select profiles solely because they are famous.
2. Do not use repository stars as a proxy for engineering quality.
3. Do not use followers as a proxy for engineering ability.
4. Do not exclude emerging engineers because they have low visibility.
5. Apply the same feature definitions to every profile.
6. Record the discovery method for every profile.
7. Preserve the original evidence.
8. Record unknown values rather than guessing.
9. Do not change classification rules after seeing an individual's results.
10. Maintain a reproducible audit trail.

---

# 9. Visibility Measurement

Visibility will be treated as a **multi-signal construct**.

Potential signals:

* GitHub followers
* repository stars
* repository forks
* number of original relevant repositories
* recent public activity
* external technical publications
* public technical/community presence

No single metric will automatically determine engineering quality.

Where possible, raw measurements will be preserved instead of converting everything immediately into a single score.

---

# 10. Feature Measurement Framework

Every profile will be evaluated against the same feature schema.

## A. Production / Shipping

Measure evidence of:

* deployed application
* public API
* hosted service
* production-oriented architecture
* Docker/containerization
* cloud deployment

## B. Engineering Quality

Measure evidence of:

* automated tests
* CI/CD
* type checking
* structured logging
* error handling
* configuration management
* documentation
* architecture documentation

## C. AI Engineering

Measure evidence of:

* LLM application
* RAG
* embeddings
* vector database
* agents
* tool calling
* MCP
* model serving/inference
* multimodal systems

## D. Evaluation

Measure evidence of:

* benchmark
* accuracy/quality metrics
* latency
* cost
* retrieval evaluation
* model evaluation
* experiment comparison

## E. Open Source

Measure:

* original repositories
* meaningful contributions
* issues/PRs
* reusable libraries/tools
* community participation

## F. Problem Framing

Classify projects according to whether they demonstrate:

* generic demonstration
* useful developer tool
* specific user problem
* business/workflow problem
* measurable real-world impact

---

# 11. Operational Definition: "Deployed"

A project is classified as **deployed = TRUE** only when public evidence demonstrates that the software is accessible or has been deployed to an identifiable runtime environment.

Examples of strong evidence:

* live application URL
* public API endpoint
* documented cloud deployment
* deployment configuration tied to the project
* publicly accessible service

A README statement such as:

> "This project can be deployed to AWS"

is NOT sufficient evidence of actual deployment.

If deployment cannot be verified:

**deployed = UNKNOWN**

not FALSE.

---

# 12. Operational Definition: "Evaluation Metrics"

`evaluation_metrics = TRUE` requires evidence that the project measures system/model performance using a defined metric or benchmark.

Examples:

* accuracy
* precision/recall
* F1
* retrieval metrics
* latency
* throughput
* cost
* benchmark score
* human evaluation with a documented methodology

A statement such as:

> "High-quality responses"

is not sufficient.

---

# 13. Operational Definition: "Production-Oriented"

A project is classified as production-oriented when public evidence demonstrates engineering considerations beyond a basic prototype.

Possible evidence:

* API/service architecture
* authentication
* testing
* Docker
* deployment
* observability
* retries/timeouts
* configuration management
* persistence
* CI/CD

A project does not need every feature to qualify.

The individual evidence dimensions will be stored separately so that "production-oriented" does not become a subjective black-box label.

---

# 14. Evidence Model

Every important extracted claim must have evidence.

Required structure:

```text
Claim
Source URL
Source type
Evidence text/location
Extraction timestamp
Confidence
```

Example:

```json
{
  "feature": "deployment",
  "value": true,
  "source_url": "https://...",
  "source_type": "github_readme",
  "evidence": "Live demo: ...",
  "confidence": "high"
}
```

---

# 15. Unknown ≠ False

This is a core methodological rule.

If public evidence does not reveal whether a profile uses Docker:

```text
docker = unknown
```

NOT:

```text
docker = false
```

This prevents absence of evidence from being incorrectly interpreted as evidence of absence.

---

# 16. Evidence Confidence

Each extracted claim receives:

### HIGH

Direct primary-source evidence.

Examples:

* GitHub repository
* official project documentation
* author's own technical site

### MEDIUM

Reliable secondary evidence that clearly supports the claim.

### LOW

Indirect or incomplete evidence.

### UNKNOWN

Insufficient evidence.

Only HIGH/MEDIUM evidence should normally be used for quantitative feature claims.

---

# 17. Source Hierarchy

Preferred sources:

1. GitHub profile
2. GitHub repository
3. Official project documentation
4. Personal technical website
5. Official publication/blog
6. Professional profile
7. Reputable third-party source

Search-result snippets are discovery mechanisms, not final evidence where the underlying source is accessible.

---

# 18. LLM Role

The local LLM is an **extraction and reasoning component**, not the source of truth.

Pipeline:

```text
Web Evidence
     ↓
LLM
     ↓
Structured Extraction
     ↓
Evidence Link
     ↓
Validation
```

The LLM must never be allowed to invent missing information.

If evidence is insufficient:

```text
UNKNOWN
```

---

# 19. Deterministic Analysis

LLMs will not calculate final research percentages.

Python/statistical code will calculate:

```text
feature prevalence
group differences
distributions
confidence intervals
correlations
```

Example:

```text
deployed profiles
=
247 / 400
=
61.75%
```

The calculation must be reproducible from the stored dataset.

---

# 20. Pilot Validation

The collection pipeline will be tested sequentially:

```text
5 profiles
   ↓
manual audit

10 profiles
   ↓
audit

25 profiles
   ↓
audit

50 profiles
   ↓
audit

100 profiles
   ↓
pilot review
```

At each checkpoint we evaluate:

* extraction correctness
* evidence quality
* duplicate rate
* missing-data rate
* classification consistency
* search coverage
* LLM hallucination rate

---

# 21. Independent Audit

At least a subset of profiles will be manually reviewed against the stored evidence.

The audit will compare:

```text
Automated classification
        vs
Human verification
```

Disagreements will be recorded rather than silently corrected.

---

# 22. Statistical Interpretation

The final analysis will distinguish:

### Descriptive findings

Example:

> 62% of sampled profiles had verifiable deployment evidence.

### Association

Example:

> Deployment evidence was more prevalent in the high-visibility group.

### Causal claim

We will generally NOT make causal claims from this observational dataset.

We cannot conclude:

> "Deployment causes higher visibility."

Possible confounding factors include:

* years of experience
* employer/company visibility
* existing audience
* open-source history
* networking
* content creation
* algorithmic exposure
* geographic differences
* survivorship bias

---

# 23. Biases and Limitations

Known risks:

## Selection bias

Public GitHub profiles are not equivalent to all AI engineers.

## Visibility bias

Popular profiles are easier to discover.

## Survivorship bias

Successful/public profiles may be overrepresented.

## Platform bias

GitHub-centered research underrepresents engineers whose primary work is private.

## Documentation bias

Better-documenting engineers may appear stronger simply because more evidence is public.

## LLM extraction bias

Local model quality may affect classification.

## Language bias

English-language sources may be easier to discover and process.

## Temporal bias

AI engineering changes rapidly; findings are specific to the research period.

---

# 24. Reproducibility Requirements

The project must preserve:

```text
research question
sampling rules
candidate discovery source
raw source URLs
retrieved evidence
extraction results
timestamps
model/version
analysis code
final dataset
```

A future researcher should be able to understand how a final percentage was produced from the underlying records.

---

# 25. Research Integrity Rules

The following are prohibited:

* inventing missing data
* manually changing results to fit expectations
* selecting examples after seeing the desired conclusion
* treating stars as engineering quality
* treating followers as engineering ability
* reporting unsupported percentages
* hiding contradictory evidence
* deleting inconvenient profiles without documenting why

If the data contradicts our original hypothesis:

**the hypothesis loses.**

---

# 26. Final Output

The final project will produce:

```text
data/
├── raw/
├── processed/
└── evidence/

reports/
├── methodology.md
├── dataset_summary.md
├── statistical_analysis.md
└── final_report.md
```

The final report will contain:

1. methodology
2. sample characteristics
3. data-quality assessment
4. feature prevalence
5. visible vs emerging comparison
6. statistical results
7. limitations
8. contradictory findings
9. practical implications
10. reproducibility information

---

# 27. Claim Strength Framework

Every major conclusion will receive a strength classification:

### Strong

Repeated pattern + good evidence + robust across analyses.

### Moderate

Consistent pattern but meaningful limitations remain.

### Weak

Interesting observation with insufficient evidence.

### Unsupported

The available data does not support the claim.

---

# 28. Stopping Rule

The research will not be declared complete simply because the target number of profiles has been reached.

The final dataset must satisfy minimum quality requirements:

* acceptable evidence coverage
* manageable duplicate rate
* acceptable extraction accuracy
* sufficient representation across visibility groups
* documented missing data
* successful audit

If quality requirements are not met, collection continues or methodology is explicitly revised and documented.

---

# 29. Core Principle

> **Collect evidence first. Interpret second.**

The objective is not to prove that the original seven-pillar hypothesis is correct.

The objective is to determine **what the evidence actually supports**.
