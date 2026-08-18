AI Engineer Research

Production-oriented, local-first AI research pipeline for evidence-backed web research, source validation, structured extraction, provenance, and auditable synthesis.







Overview

ai-engineer-research turns a research question into a structured, evidence-backed research report. It is designed around the engineering problems that appear beyond a simple search-and-summarize demo:

source discovery and collection

source failure isolation

relevance filtering

evidence extraction and provenance

structured synthesis

run-level performance measurement

observability and telemetry

regression testing

benchmark-driven optimization

Research Question
       |
       v
    Planning
       |
       v
 Source Discovery
       |
       v
 Source Collection
       |
       v
 Relevance / Evidence Processing
       |
       v
    Validation
       |
       v
    Synthesis
       |
       +------------------+
       |                  |
       v                  v
 Persistence         Observability
       |
       v
 Research Report

Current local inference uses Ollama + Qwen3:4b.

Architecture

The system separates responsibilities across explicit boundaries:

ResearchTask
    |
    v
Researcher
    |
    +--> Planner
    |
    +--> Runner
    |      +--> Discovery
    |      +--> Collection
    |      +--> Validation
    |      +--> Evidence processing
    |
    +--> Synthesizer
    |
    +--> Store
    |
    +--> Telemetry / Observability

Core Engineering Features

Unified research boundary

Researcher coordinates planning, execution, synthesis, persistence, and run-level performance measurement. Each run has an explicit run_id.

Structured research tasks

ResearchTask represents the research question, task name, source types, extraction schema, and metadata independently from the interface.

Source failure isolation

Individual source failures do not automatically terminate an otherwise valid run. The runner tracks:

sources_considered
sources_collected
completed_steps
failed_steps

Evidence alignment

Collected content is scored against the research question.

Current contract:

One collected source
    -> preserve recall

Multiple collected sources
    -> reject zero-alignment evidence

Evidence and provenance

Evidence is first-class data. The intended chain is:

Source -> Evidence -> Claim -> Synthesis

Dedicated components cover evidence packets, evidence windows, source accounting, and telemetry.

Observability

Run-level performance includes:

planning_seconds
execution_seconds
synthesis_seconds
persistence_seconds
total_seconds

Research counters include:

sources_considered
sources_collected
completed_steps
failed_steps

This allows latency investigation by stage instead of guesswork.

Benchmarking

Benchmark entry point:

scripts/benchmark_research.py

Current source levels:

5, 10, 25

with repeated measurements and warmup.

Each run records exit code, wall time, reported pipeline time, stage timings, completed/failed steps, source counts, stdout, and stderr.

Artifacts are stored in data/benchmarks/ and ignored by Git.

Measured Baseline

Current local configuration:

Model: Qwen3:4b
Inference: Ollama
Runtime: local

Latest successful observations:

Requested sources

Successful runs

Successful mean

5

3/3

220.373 s

10

2/3

211.728 s

25

1/3

452.404 s*

* One successful observation only, so this is not statistically stable.

Latest benchmark totals:

Successful runs: 6
Failed / partial runs: 3

Observed successful runs ranged from approximately 177 s to 452 s, depending on workload and source count.

These numbers are a baseline, not a final performance claim.

Real End-to-End Validation

The real pipeline, rather than only mocks, has passed:

REAL ResearchRunner: PASS

completed_steps: 4
sources:          1
evidence:         1
claims:           1
syntheses:        1

Observed real E2E runtimes include 18.24 s and 30.04 s. These are separate executions, not a controlled before/after comparison.

Reliability Validation

Latest full unit regression:

163 passed

Dedicated reliability coverage includes source failures, relevance, concurrency, telemetry, observability, integration, synthesizer contracts, and benchmark classification.

Reliability gate:

17 passed

Testing

Full unit suite:

$env:PYTHONPATH="src"
python -m pytest tests\unit -q

Real E2E:

$env:PYTHONPATH="src"

python -m pytest `
    tests\unit\test_researcher_real_e2e.py `
    -q `
    -s

Local Model Setup

Verify Ollama:

ollama list

Expected model:

qwen3:4b

Verify the local API:

Invoke-WebRequest `
    -Uri "http://127.0.0.1:11434/api/tags" `
    -UseBasicParsing

Expected status: 200.

Installation

git clone https://github.com/diwakar7619/ai-engineer-research.git
cd ai-engineer-research
uv sync
$env:PYTHONPATH="src"
python -m pytest tests\unit -q

Inspect the current CLI contract:

python -m research.cli --help

Project Structure

ai-engineer-research/
├── src/research/
│   ├── alignment.py
│   ├── daily_app.py
│   ├── evidence_packet.py
│   ├── evidence_window.py
│   ├── execution.py
│   ├── executor.py
│   ├── llm.py
│   ├── ollama.py
│   ├── observability.py
│   ├── planner.py
│   ├── researcher.py
│   ├── result.py
│   ├── runner.py
│   ├── source.py
│   ├── source_accounting.py
│   ├── store.py
│   ├── synthesizer.py
│   ├── task.py
│   ├── telemetry.py
│   └── validator.py
├── tests/unit/
├── scripts/benchmark_research.py
├── data/benchmarks/
├── pyproject.toml
└── README.md

Engineering Principles

Explicit contracts: planner, executor, synthesizer, store, and model-provider boundaries are independently testable.

Failure isolation: a failed source should not destroy an otherwise valid run.

Evidence first: claims remain connected to supporting evidence.

Observability before optimization: performance changes are measured against a baseline.

Local-first development: current inference runs through local Ollama.

Reproducible validation: targeted tests precede broader regression.

Current Limitations

This project is production-oriented and production-hardened in several areas, but does not yet claim fully production-ready deployment status.

Latency

Multi-source research currently takes several minutes in the measured benchmark.

Benchmark stability

The latest 25-source workload had:

1 successful
2 failed / partial

Retrieval efficiency

Potential improvements include:

source deduplication

caching

embedding-based retrieval

hybrid lexical/vector retrieval

top-K evidence selection

Local inference

Latency depends on model size, CPU/GPU utilization, prompt size, generated token count, concurrency, and local hardware.

Performance Roadmap

Baseline
   |
   v
Stage-level profiling
   |
   +--> LLM latency
   +--> source fetching
   +--> extraction
   +--> retrieval
   +--> persistence
   |
   v
Caching + deduplication
   |
   v
Embedding retrieval
   |
   v
Hybrid retrieval
   |
   v
Top-K evidence selection
   |
   v
Prompt / token optimization
   |
   v
Benchmark
   |
   v
Compare against baseline

An optimization is successful only when measured against the baseline.

Development Status

Component

Status

Research task model

Complete

Planner

Complete

Research execution

Complete

Source failure isolation

Complete

Evidence handling

Complete

Relevance filtering

Complete

Synthesis

Complete

Persistence

Complete

Telemetry

Complete

Observability

Complete

Unit regression

Complete

Real E2E

Complete

Benchmark harness

Complete

Performance baseline

Complete

Latency optimization

In progress

Retrieval/cache optimization

In progress

Production deployment hardening

In progress

What This Project Demonstrates

This is an AI engineering project, not a model-training project. It demonstrates modular LLM orchestration, provider abstraction, local inference, structured research tasks, source failure isolation, evidence handling, relevance filtering, provenance, telemetry, observability, benchmarking, regression testing, and performance analysis.

The goal is a research system that can be measured, debugged, and improved, rather than simply producing plausible-looking answers.

License

See the repository license for applicable terms.

Author

Pratham Diwakar

AI Engineer focused on production-oriented LLM, RAG, agentic systems, and AI infrastructure.

GitHub: https://github.com/diwakar7619