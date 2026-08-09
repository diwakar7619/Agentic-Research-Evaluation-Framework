# Research Data Schema

**Version:** 1.0
**Status:** Draft
**Related methodology:** `research/methodology.md`

---

## 1. Purpose

This document defines the machine-readable structure used to represent one researched AI-engineering profile.

The schema separates:

1. identity
2. visibility
3. projects
4. engineering signals
5. AI capabilities
6. evidence
7. research metadata

The schema must preserve the distinction between:

* `true`
* `false`
* `unknown`

Missing public evidence must not automatically be interpreted as `false`.

---

# 2. Profile Record

Each researched profile will be represented by one profile record.

```text
Profile
├── identity
├── visibility
├── projects
├── engineering_signals
├── ai_capabilities
├── evidence
└── metadata
```

---

# 3. Identity

Identifies the person and the primary public sources used for research.

| Field              | Type   | Required | Description                    |
| ------------------ | ------ | -------: | ------------------------------ |
| `profile_id`       | string |      yes | Stable internal identifier     |
| `name`             | string |      yes | Publicly displayed name        |
| `github_username`  | string |      yes | GitHub username                |
| `github_url`       | string |      yes | Canonical GitHub profile URL   |
| `discovery_source` | string |      yes | How the profile was discovered |
| `research_status`  | enum   |      yes | Current research state         |

### `research_status`

Allowed values:

```text
candidate
eligible
excluded
researched
audited
```

---

# 4. Visibility

Visibility measurements are stored as raw observations.

| Field                   | Type         | Required | Description                                   |
| ----------------------- | ------------ | -------: | --------------------------------------------- |
| `followers`             | integer/null |      yes | Public GitHub follower count                  |
| `public_repositories`   | integer/null |      yes | Number of public repositories                 |
| `relevant_repositories` | integer/null |      yes | Number of repositories relevant to this study |
| `total_relevant_stars`  | integer/null |      yes | Combined stars of relevant repositories       |
| `total_relevant_forks`  | integer/null |      yes | Combined forks of relevant repositories       |
| `recent_activity`       | object       |      yes | Public activity measurements                  |
| `visibility_group`      | enum/null    |      yes | Final visibility classification               |

### `visibility_group`

Allowed values:

```text
visible
emerging
unknown
```

The classification must be produced using the predefined methodology rather than subjective judgment.

---

# 5. Recent Activity

```text
recent_activity
├── last_public_activity
├── active_repositories
└── activity_window_days
```

| Field                  | Type         | Description                                   |
| ---------------------- | ------------ | --------------------------------------------- |
| `last_public_activity` | date/null    | Most recent relevant public activity          |
| `active_repositories`  | integer/null | Relevant repositories showing recent activity |
| `activity_window_days` | integer      | Time window used for activity measurement     |

---

# 6. Projects

Each relevant project is represented separately.

```text
projects: [
    {
        project_id,
        repository_name,
        repository_url,
        description,
        relevance,
        deployment,
        engineering_signals,
        ai_capabilities,
        evaluation,
        evidence_ids
    }
]
```

### Project fields

| Field             | Type         | Description                        |
| ----------------- | ------------ | ---------------------------------- |
| `project_id`      | string       | Stable internal project identifier |
| `repository_name` | string       | Repository name                    |
| `repository_url`  | string       | Repository URL                     |
| `description`     | string/null  | Short project description          |
| `relevance`       | enum         | AI-engineering relevance           |
| `evidence_ids`    | list[string] | Evidence supporting project claims |

### `relevance`

```text
high
medium
low
excluded
```

Only `high` and `medium` relevance projects will normally contribute to the research dataset.

---

# 7. Deployment

Deployment is an evidence-backed feature.

```text
deployment
├── value
├── type
└── evidence_ids
```

### `value`

```text
true
false
unknown
```

### `type`

Possible values:

```text
live_application
public_api
cloud_service
container_deployment
other
unknown
```

A deployment claim requires public evidence.

---

# 8. Engineering Signals

The following engineering characteristics will be measured independently.

```text
engineering_signals
├── testing
├── ci_cd
├── docker
├── api_service
├── configuration_management
├── error_handling
├── logging_observability
├── documentation
└── architecture_documentation
```

Each field uses:

```text
true
false
unknown
```

The schema intentionally stores these independently instead of creating one subjective "production_ready" boolean.

---

# 9. AI Capabilities

```text
ai_capabilities
├── llm_application
├── rag
├── embeddings
├── vector_database
├── agents
├── tool_calling
├── mcp
├── model_inference
├── model_serving
└── multimodal
```

Each capability uses:

```text
true
false
unknown
```

A capability is `true` only when supported by evidence.

---

# 10. Evaluation

Evaluation evidence is stored separately.

```text
evaluation
├── has_metrics
├── has_benchmark
├── has_latency_measurement
├── has_cost_measurement
├── has_retrieval_evaluation
├── has_model_evaluation
└── evaluation_description
```

Boolean fields use:

```text
true
false
unknown
```

`evaluation_description` contains a concise description of the publicly documented evaluation methodology.

---

# 11. Open Source Signals

```text
open_source
├── original_repositories
├── meaningful_contributions
├── pull_requests
├── issues
├── reusable_tools
└── community_participation
```

Values should be based on observable public evidence.

---

# 12. Problem Framing

Projects will be classified according to the strongest evidence available.

```text
problem_framing
├── generic_demo
├── developer_tool
├── specific_user_problem
├── business_workflow
└── measurable_impact
```

A project may have more than one applicable classification.

---

# 13. Evidence Record

Every important claim must point to one or more evidence records.

```text
evidence: [
    {
        evidence_id,
        claim,
        source_url,
        source_type,
        evidence_text,
        confidence,
        retrieved_at
    }
]
```

### Evidence fields

| Field           | Type     | Description                     |
| --------------- | -------- | ------------------------------- |
| `evidence_id`   | string   | Stable evidence identifier      |
| `claim`         | string   | Claim supported by the evidence |
| `source_url`    | string   | Public source URL               |
| `source_type`   | enum     | Type of source                  |
| `evidence_text` | string   | Relevant supporting text        |
| `confidence`    | enum     | Evidence confidence             |
| `retrieved_at`  | datetime | Retrieval timestamp             |

### `source_type`

```text
github_profile
github_repository
github_readme
github_code
github_release
official_documentation
personal_website
technical_blog
professional_profile
other
```

### `confidence`

```text
high
medium
low
unknown
```

---

# 14. Metadata

```text
metadata
├── collected_at
├── collector_version
├── extraction_model
├── extraction_model_version
├── schema_version
└── audit_status
```

### `audit_status`

```text
not_audited
audited
needs_review
rejected
```

---

# 15. Data Integrity Rules

1. Every important boolean claim must have supporting evidence.
2. `unknown` must be used when public evidence is insufficient.
3. `unknown` must not be converted to `false` during collection.
4. Raw observations must be preserved.
5. Derived statistics must be calculated separately from raw data.
6. LLM-generated claims must reference evidence.
7. The LLM must not invent missing information.
8. Evidence URLs must be stored.
9. Retrieval timestamps must be stored.
10. Schema changes require a version update.

---

# 16. Derived Metrics

Derived metrics must not be manually stored as authoritative values.

Examples:

```text
deployment_rate
rag_prevalence
agent_prevalence
testing_prevalence
evaluation_prevalence
average_relevant_repositories
median_repository_stars
```

These will be calculated programmatically from the raw profile records.

---

# 17. Schema Versioning

Current version:

```text
1.0
```

Any structural change to this schema requires a version update and a corresponding migration or documented compatibility decision.
