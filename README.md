<div align="center">

# 🔬 Agentic Research Evaluation Framework

### Production-oriented, local-first AI research pipeline

**Evidence-backed web research · Source validation · Structured extraction · Provenance · Auditable synthesis**

<br>

![Tests](https://img.shields.io/badge/tests-163%20passed-2ea44f?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![LLM](https://img.shields.io/badge/LLM-Qwen3--4B-orange?style=for-the-badge)
![Inference](https://img.shields.io/badge/Inference-Ollama-black?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active%20Development-f0ad4e?style=for-the-badge)

</div>

---

> **A measurable research-agent system built around evidence, reliability, observability, and performance evaluation.**

## 🎯 What is this?

**Agentic Research Evaluation Framework** turns a research question into a structured, evidence-backed research report.

It is deliberately engineered beyond the usual:

```text
search → stuff results into prompt → ask LLM to summarize
```

Instead, the system treats **sources, evidence, failures, provenance, telemetry, and performance** as first-class engineering concerns.

### Core Pipeline

```text
┌─────────────────────┐
│  Research Question  │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│      Planning       │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  Source Discovery   │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  Source Collection  │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ Relevance / Evidence│
│      Processing     │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│     Validation      │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│     Synthesis       │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ Evidence-backed     │
│ Research Report     │
└─────────────────────┘

        ┌───────────────────────┐
        │ Telemetry /           │
        │ Observability         │
        └───────────────────────┘
```

---

## ✨ Engineering Highlights

| Capability | What it provides |
|---|---|
| 🧠 **Structured Research** | Explicit research tasks instead of prompt-only orchestration |
| 🔎 **Source Handling** | Discovery, collection, validation and source accounting |
| 🧩 **Evidence Pipeline** | Evidence packets, windows, relevance and provenance |
| 🛡️ **Failure Isolation** | Individual source failures do not automatically kill a run |
| 🎯 **Relevance Filtering** | Alignment-based evidence selection |
| 📝 **Structured Synthesis** | Claims remain connected to supporting evidence |
| 📊 **Observability** | Stage-level timing and run-level counters |
| 🧪 **Regression Testing** | 163 passing unit tests |
| 📈 **Benchmarking** | Repeated source-scaling experiments |
| 💻 **Local Inference** | Ollama + Qwen3:4b |

---

# 🏗️ Architecture

The system separates responsibilities across explicit boundaries.

```text
                         ┌─────────────────┐
                         │  ResearchTask   │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │   Researcher    │
                         │  Orchestrator   │
                         └────────┬────────┘
                                  │
             ┌────────────────────┼────────────────────┐
             │                    │                    │
             ▼                    ▼                    ▼
      ┌────────────┐      ┌────────────┐      ┌─────────────┐
      │   Planner  │      │   Runner   │      │ Synthesizer │
      └────────────┘      └─────┬──────┘      └─────────────┘
                                │
                    ┌───────────┼───────────┐
                    │           │           │
                    ▼           ▼           ▼
               Discovery   Collection  Validation
                                │
                                ▼
                       Evidence Processing
                                │
                                ▼
                         Research Result
                                │
                  ┌─────────────┴─────────────┐
                  ▼                           ▼
             Persistence                Observability
```

### Evidence Flow

```text
Source
  │
  ▼
Collected Content
  │
  ▼
Alignment / Relevance
  │
  ▼
Evidence
  │
  ▼
Claim
  │
  ▼
Synthesis
```

The final answer is not treated as the only artifact. Evidence and provenance remain part of the pipeline.

---

# 🧠 Key Engineering Decisions

## 1. Explicit Research Boundary

`Researcher` coordinates:

- planning
- execution
- synthesis
- persistence
- performance measurement

Each run has an explicit `run_id`.

## 2. Source Failure Isolation

A failed source is treated as a **source-level failure**, not necessarily a pipeline-level failure.

The runner tracks:

```text
sources_considered
sources_collected
completed_steps
failed_steps
```

This allows the system to continue when individual sources become unavailable.

## 3. Evidence Alignment

Collected content is evaluated against the research question.

Current contract:

```text
┌───────────────────────────────┐
│ One collected source          │
│                               │
│ → preserve recall             │
└───────────────────────────────┘

┌───────────────────────────────┐
│ Multiple collected sources    │
│                               │
│ → reject zero-alignment       │
│   evidence                    │
└───────────────────────────────┘
```

This behavior was introduced after regression testing exposed the precision/recall trade-off.

## 4. Evidence-First Synthesis

The system maintains an explicit chain:

```text
Source
   ↓
Evidence
   ↓
Claim
   ↓
Synthesis
```

This makes downstream evaluation and provenance possible.

---

# 📊 Observability

Performance is measured at the research-run level.

### Stage Timing

```text
planning_seconds
execution_seconds
synthesis_seconds
persistence_seconds
total_seconds
```

### Research Counters

```text
sources_considered
sources_collected
completed_steps
failed_steps
```

> **Measure the bottleneck before optimizing it.**

---

# ⚡ Performance Baseline

Current local configuration:

```text
Model       Qwen3:4b
Inference   Ollama
Runtime     Local
```

### Latest Benchmark

| Requested Sources | Successful | Partial / Failed | Mean* |
|---:|---:|---:|---:|
| **5** | 3/3 | 0 | **220.373 s** |
| **10** | 2/3 | 1 | **211.728 s** |
| **25** | 1/3 | 2 | **452.404 s** |

\* The 25-source result is based on one successful observation and is therefore **not statistically stable**.

### Overall

```text
Successful runs        6
Failed / partial runs  3
```

Observed successful runs:

```text
~177 s → ~452 s
```

These measurements are the **current baseline**, not a performance claim.

---

# 🧪 Validation

## Full Unit Regression

Latest result:

```text
163 passed
```

Coverage includes:

- source failure handling
- relevance behavior
- runner concurrency
- telemetry
- telemetry integration
- observability
- researcher integration
- synthesizer contracts
- benchmark classification

Run:

```powershell
$env:PYTHONPATH="src"
python -m pytest tests\unit -q
```

## Real End-to-End Validation

The real research pipeline has been validated without replacing the main production components with mocks.

```text
REAL ResearchRunner: PASS

completed_steps: 4
sources:          1
evidence:         1
claims:           1
syntheses:        1
```

Observed real E2E runtimes include:

```text
18.24 s
30.04 s
```

These are separate executions and are **not a controlled before/after benchmark**.

Run:

```powershell
$env:PYTHONPATH="src"

python -m pytest `
    tests\unit\test_researcher_real_e2e.py `
    -q `
    -s
```

---

# 🛡️ Reliability Gates

Dedicated reliability testing covers:

```text
Source failure isolation
        +
Relevance behavior
        +
Runner concurrency
        +
Telemetry
        +
Telemetry integration
        +
Observability
```

Latest reliability gate:

```text
17 passed
```

---

# 💻 Local Setup

## Requirements

- Python 3.12
- `uv`
- Ollama
- Qwen3:4b
- Hardware capable of running the local model

## Installation

```powershell
git clone https://github.com/diwakar7619/Agentic-Research-Evaluation-Framework.git

cd Agentic-Research-Evaluation-Framework

uv sync

$env:PYTHONPATH="src"
```

## Verify Ollama

```powershell
ollama list
```

Expected model:

```text
qwen3:4b
```

Check the local HTTP API:

```powershell
Invoke-WebRequest `
    -Uri "http://127.0.0.1:11434/api/tags" `
    -UseBasicParsing
```

Expected:

```text
HTTP 200
```

---

# 🚀 Usage

Inspect the current CLI contract:

```powershell
$env:PYTHONPATH="src"

python -m research.cli --help
```

The README intentionally does not hard-code potentially stale CLI arguments. The implementation remains the source of truth.

---

# 📁 Project Structure

```text
Agentic-Research-Evaluation-Framework/
│
├── src/
│   └── research/
│       ├── alignment.py
│       ├── daily_app.py
│       ├── evidence_packet.py
│       ├── evidence_window.py
│       ├── execution.py
│       ├── executor.py
│       ├── llm.py
│       ├── ollama.py
│       ├── observability.py
│       ├── planner.py
│       ├── researcher.py
│       ├── result.py
│       ├── runner.py
│       ├── source.py
│       ├── source_accounting.py
│       ├── store.py
│       ├── synthesizer.py
│       ├── task.py
│       ├── telemetry.py
│       └── validator.py
│
├── tests/
│   └── unit/
│
├── scripts/
│   └── benchmark_research.py
│
├── data/
│   └── benchmarks/
│
├── pyproject.toml
└── README.md
```

---

# 📈 Benchmarking

Benchmark entry point:

```text
scripts/benchmark_research.py
```

The benchmark evaluates multiple source levels with repeated runs and warmup.

Each run records:

```text
exit_code
wall_time_seconds
reported_total_seconds

planning_seconds
execution_seconds
synthesis_seconds
persistence_seconds

completed_steps
failed_steps

sources_considered
sources_collected

stdout
stderr
```

Run:

```powershell
$env:PYTHONPATH="src"

python scripts\benchmark_research.py
```

Artifacts are written to:

```text
data/benchmarks/
```

and are ignored by Git.

---

# ⚡ Current Reality

> **Reliability is substantially hardened. Latency optimization remains the primary engineering bottleneck.**

```text
163 unit tests          PASS
17-test reliability    PASS
Real E2E                PASS
Local Ollama            PASS
Benchmark harness       PASS

Latency optimization    🚧
Retrieval optimization  🚧
Cache optimization      🚧
Production deployment   🚧
```

The system should therefore be described as:

> **production-oriented and reliability-hardened**

rather than claiming full production readiness.

---

# 🛠️ Performance Roadmap

```text
                 CURRENT BASELINE
                        │
                        ▼
               ┌─────────────────┐
               │ Stage Profiling │
               └────────┬────────┘
                        │
       ┌────────────────┼────────────────┐
       ▼                ▼                ▼
  LLM Latency       Fetching        Retrieval
       │                │                │
       └────────────────┼────────────────┘
                        ▼
               Cache + Deduplication
                        │
                        ▼
               Embedding Retrieval
                        │
                        ▼
                Hybrid Retrieval
                        │
                        ▼
               Top-K Evidence
                        │
                        ▼
             Prompt / Token Reduction
                        │
                        ▼
                    Benchmark
                        │
                        ▼
                Compare Baseline
```

An optimization is accepted only when its effect can be measured against the baseline.

---

# ⚠️ Current Limitations

### Latency

Multi-source research currently takes several minutes in the measured benchmark.

### Benchmark Stability

Higher source counts currently produce partial or failed runs.

Latest 25-source workload:

```text
1 successful
2 partial / failed
```

### Retrieval Efficiency

Potential optimization areas:

- source deduplication
- caching
- embedding-based retrieval
- hybrid lexical/vector retrieval
- top-K evidence selection
- prompt/token reduction

### Local Inference

Latency depends on:

- model size
- prompt size
- generated token count
- CPU/GPU utilization
- concurrent requests
- local hardware

---

# 📌 Development Status

| Component | Status |
|---|:---:|
| Structured research tasks | ✅ |
| Planning | ✅ |
| Research execution | ✅ |
| Source failure isolation | ✅ |
| Evidence handling | ✅ |
| Relevance filtering | ✅ |
| Synthesis | ✅ |
| Persistence | ✅ |
| Telemetry | ✅ |
| Observability | ✅ |
| Unit regression | ✅ |
| Real E2E | ✅ |
| Benchmark harness | ✅ |
| Performance baseline | ✅ |
| Latency optimization | 🚧 |
| Retrieval / cache optimization | 🚧 |
| Production deployment hardening | 🚧 |

---

# 🎯 Engineering Principles

> **Evidence before claims.**

> **Measure before optimizing.**

> **Fail at the smallest reasonable boundary.**

> **Keep contracts explicit.**

> **Treat observability as part of the system, not an afterthought.**

> **Prefer measured engineering trade-offs over fashionable architecture.**

---

# 🎓 What This Project Demonstrates

This is an **AI engineering project**, not a model-training project.

It demonstrates practical engineering around LLM systems:

- modular research orchestration
- provider abstraction
- local LLM integration
- structured task modeling
- source-level failure isolation
- evidence processing
- relevance filtering
- provenance
- telemetry
- observability
- benchmark design
- regression testing
- performance analysis

The goal is not merely to produce a plausible answer.

The goal is to build a research system that can be:

```text
MEASURED
   ↓
INSPECTED
   ↓
DEBUGGED
   ↓
OPTIMIZED
   ↓
VALIDATED
```

---

# 👤 Author

<div align="center">

### Pratham Diwakar

**AI Engineer · LLM Systems · RAG · Agentic AI**

[GitHub](https://github.com/diwakar7619)

</div>

---

# 📄 License

See the repository license for applicable terms.
