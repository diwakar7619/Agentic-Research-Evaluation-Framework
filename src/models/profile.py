from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class TriState(str, Enum):
    true = "true"
    false = "false"
    unknown = "unknown"


class ResearchStatus(str, Enum):
    candidate = "candidate"
    eligible = "eligible"
    excluded = "excluded"
    researched = "researched"
    audited = "audited"


class VisibilityGroup(str, Enum):
    visible = "visible"
    emerging = "emerging"
    unknown = "unknown"


class RelevanceLevel(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"
    excluded = "excluded"


class DeploymentType(str, Enum):
    live_application = "live_application"
    public_api = "public_api"
    cloud_service = "cloud_service"
    container_deployment = "container_deployment"
    other = "other"
    unknown = "unknown"


class SourceType(str, Enum):
    github_profile = "github_profile"
    github_repository = "github_repository"
    github_readme = "github_readme"
    github_code = "github_code"
    github_release = "github_release"
    official_documentation = "official_documentation"
    personal_website = "personal_website"
    technical_blog = "technical_blog"
    professional_profile = "professional_profile"
    other = "other"


class Confidence(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"
    unknown = "unknown"


class AuditStatus(str, Enum):
    not_audited = "not_audited"
    audited = "audited"
    needs_review = "needs_review"
    rejected = "rejected"


class RecentActivity(BaseModel):
    last_public_activity: Optional[date] = None
    active_repositories: Optional[int] = None
    activity_window_days: int = 365


class Visibility(BaseModel):
    followers: Optional[int] = None
    public_repositories: Optional[int] = None
    relevant_repositories: Optional[int] = None
    total_relevant_stars: Optional[int] = None
    total_relevant_forks: Optional[int] = None
    recent_activity: RecentActivity = Field(default_factory=RecentActivity)
    visibility_group: VisibilityGroup = VisibilityGroup.unknown


class Deployment(BaseModel):
    value: TriState = TriState.unknown
    type: DeploymentType = DeploymentType.unknown
    evidence_ids: list[str] = Field(default_factory=list)


class EngineeringSignals(BaseModel):
    testing: TriState = TriState.unknown
    ci_cd: TriState = TriState.unknown
    docker: TriState = TriState.unknown
    api_service: TriState = TriState.unknown
    configuration_management: TriState = TriState.unknown
    error_handling: TriState = TriState.unknown
    logging_observability: TriState = TriState.unknown
    documentation: TriState = TriState.unknown
    architecture_documentation: TriState = TriState.unknown


class AICapabilities(BaseModel):
    llm_application: TriState = TriState.unknown
    rag: TriState = TriState.unknown
    embeddings: TriState = TriState.unknown
    vector_database: TriState = TriState.unknown
    agents: TriState = TriState.unknown
    tool_calling: TriState = TriState.unknown
    mcp: TriState = TriState.unknown
    model_inference: TriState = TriState.unknown
    model_serving: TriState = TriState.unknown
    multimodal: TriState = TriState.unknown


class Evaluation(BaseModel):
    has_metrics: TriState = TriState.unknown
    has_benchmark: TriState = TriState.unknown
    has_latency_measurement: TriState = TriState.unknown
    has_cost_measurement: TriState = TriState.unknown
    has_retrieval_evaluation: TriState = TriState.unknown
    has_model_evaluation: TriState = TriState.unknown
    evaluation_description: Optional[str] = None


class OpenSourceSignals(BaseModel):
    original_repositories: Optional[int] = None
    meaningful_contributions: Optional[int] = None
    pull_requests: Optional[int] = None
    issues: Optional[int] = None
    reusable_tools: Optional[int] = None
    community_participation: TriState = TriState.unknown


class EvidenceRecord(BaseModel):
    evidence_id: str
    claim: str
    source_url: str
    source_type: SourceType = SourceType.other
    evidence_text: str
    confidence: Confidence = Confidence.unknown
    retrieved_at: datetime


class ProjectRecord(BaseModel):
    project_id: str
    repository_name: str
    repository_url: str
    description: Optional[str] = None
    relevance: RelevanceLevel = RelevanceLevel.low
    deployment: Deployment = Field(default_factory=Deployment)
    engineering_signals: EngineeringSignals = Field(default_factory=EngineeringSignals)
    ai_capabilities: AICapabilities = Field(default_factory=AICapabilities)
    evaluation: Evaluation = Field(default_factory=Evaluation)
    evidence_ids: list[str] = Field(default_factory=list)


class ProblemFraming(BaseModel):
    generic_demo: TriState = TriState.unknown
    developer_tool: TriState = TriState.unknown
    specific_user_problem: TriState = TriState.unknown
    business_workflow: TriState = TriState.unknown
    measurable_impact: TriState = TriState.unknown


class Identity(BaseModel):
    profile_id: str
    name: str
    github_username: str
    github_url: str
    discovery_source: str
    research_status: ResearchStatus = ResearchStatus.candidate


class Metadata(BaseModel):
    collected_at: Optional[datetime] = None
    collector_version: str = "0.1.0"
    extraction_model: Optional[str] = None
    extraction_model_version: Optional[str] = None
    schema_version: str = "1.0"
    audit_status: AuditStatus = AuditStatus.not_audited


class ProfileRecord(BaseModel):
    identity: Identity
    visibility: Visibility = Field(default_factory=Visibility)
    projects: list[ProjectRecord] = Field(default_factory=list)
    engineering_signals: EngineeringSignals = Field(default_factory=EngineeringSignals)
    ai_capabilities: AICapabilities = Field(default_factory=AICapabilities)
    evaluation: Evaluation = Field(default_factory=Evaluation)
    open_source: OpenSourceSignals = Field(default_factory=OpenSourceSignals)
    problem_framing: ProblemFraming = Field(default_factory=ProblemFraming)
    evidence: list[EvidenceRecord] = Field(default_factory=list)
    metadata: Metadata = Field(default_factory=Metadata)
