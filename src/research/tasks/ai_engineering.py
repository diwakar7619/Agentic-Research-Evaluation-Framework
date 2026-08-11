from ..task import ResearchTask


AI_ENGINEERING_PROFILE_SCHEMA = {
    "type": "object",
    "properties": {
        "ai_capabilities": {
            "type": "object",
            "properties": {
                "llm_application": {
                    "type": "string",
                    "enum": ["true", "false", "unknown"],
                },
                "rag": {
                    "type": "string",
                    "enum": ["true", "false", "unknown"],
                },
                "embeddings": {
                    "type": "string",
                    "enum": ["true", "false", "unknown"],
                },
                "vector_database": {
                    "type": "string",
                    "enum": ["true", "false", "unknown"],
                },
                "agents": {
                    "type": "string",
                    "enum": ["true", "false", "unknown"],
                },
                "tool_calling": {
                    "type": "string",
                    "enum": ["true", "false", "unknown"],
                },
                "mcp": {
                    "type": "string",
                    "enum": ["true", "false", "unknown"],
                },
            },
            "required": [
                "llm_application",
                "rag",
                "embeddings",
                "vector_database",
                "agents",
                "tool_calling",
                "mcp",
            ],
        },
        "engineering_signals": {
            "type": "object",
            "properties": {
                "testing": {
                    "type": "string",
                    "enum": ["true", "false", "unknown"],
                },
                "ci_cd": {
                    "type": "string",
                    "enum": ["true", "false", "unknown"],
                },
                "docker": {
                    "type": "string",
                    "enum": ["true", "false", "unknown"],
                },
                "api_service": {
                    "type": "string",
                    "enum": ["true", "false", "unknown"],
                },
                "documentation": {
                    "type": "string",
                    "enum": ["true", "false", "unknown"],
                },
            },
            "required": [
                "testing",
                "ci_cd",
                "docker",
                "api_service",
                "documentation",
            ],
        },
    },
    "required": [
        "ai_capabilities",
        "engineering_signals",
    ],
}


AI_ENGINEERING_PROFILE_RESEARCH = ResearchTask(
    name="ai_engineering_profile_research",
    question=(
        "Identify AI capabilities and engineering signals demonstrated "
        "by publicly available technical evidence."
    ),
    source_types=(
        "github_repository",
        "web_page",
        "documentation",
        "pdf",
    ),
    extraction_schema=AI_ENGINEERING_PROFILE_SCHEMA,
)
