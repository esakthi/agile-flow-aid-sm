from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..services.genai_service import GenAIService
from ..services.vector_service import VectorService
from ..services.data_service import DataService
from ..schemas import DashboardResponse
import logging
import json

router = APIRouter()
logger = logging.getLogger(__name__)
genai_service = GenAIService()
vector_service = VectorService(genai_service)

ROLE_PROMPTS = {
    "ProductOwner": """
        Objective: Product Owner needs to know scope completion, acceptance criteria status, and release readiness. The detailed model shows which stories are merged, which are in UAT, and which are blocked by external issues.
        Data sources: Epics, Stories, Acceptance Criteria, Status History, CICD Deployments.
        Objectives:
        - Show scope completion (% stories done vs total).
        - Track acceptance criteria status (met vs unmet).
        - Highlight release readiness (stories merged, UAT passed, PROD deployed).
        - Identify blockers (external dependencies, failed builds).
        Enrichments:
        - Summarise epic health in natural language.
        - Detect anomalies (stories delayed > planned end date).
        - Sentiment analysis: Extract tone from developer/QA comments to surface morale signals.
        - Velocity trends: Compute rolling averages of story completion per sprint.
        Visualisations: bar_chart, table, gauge.
    """,
    "ScrumMaster": """
        Objective: Scrum Master needs flow metrics and impediment signals. status_history and defect reopen events enable cycle time, blocked time, and bottleneck detection.
        Data sources: Status History, Defects, Commits, CICD Deployments.
        Objectives:
        - Show flow metrics (cycle time, lead time, throughput).
        - Identify impediments (stories reopened, defects linked, blocked statuses).
        - Track bottlenecks (stories stuck in Code Review or QA).
        Enrichments:
        - Summarise impediment signals in natural language.
        - Highlight stories with multiple reopen events.
        - Compute blocked time per story.
        - Sentiment analysis: Extract tone from developer/QA comments.
        Visualisations: cumulative flow diagram, scatter plot, heatmap, timeline.
    """,
    "DeliveryLead": """
        Objective: Delivery Lead needs release-level risk and CI stability. Build records with environment and failure reasons, let them decide go/no‑go and plan rollbacks.
        Data sources: CICD Build Records, Release Versions, Environment Deployments, Defect Logs.
        Objectives:
        - Show release-level risk (failed builds, rollback events).
        - Track CI stability (success rate per environment).
        - Provide go/no-go readiness signals for releases.
        Enrichments:
        - Summarise release risk in natural language.
        - Detect anomalies (failure spikes, unstable builds).
        - Risk signals: Combine defect reopen rate + UAT failure rate + blocker count into a composite risk score.
        Visualisations: timeline, environment stability dashboard, scorecard, risk heatmap.
    """
}

@router.get("/dashboard/{role}", response_model=DashboardResponse)
async def get_dashboard(role: str, db: AsyncSession = Depends(get_db)):
    logger.info(f"Generating dashboard for role: {role}")

    # 1. Retrieve a snapshot of the actual data
    data_snapshot = await DataService.get_all_normalized_data(db)
    # Remove SQLAlchemy state from dicts
    for list_key in data_snapshot:
        for item in data_snapshot[list_key]:
            item.pop('_sa_instance_state', None)
            # Convert datetime to string for JSON serialization in prompt
            for k, v in item.items():
                if hasattr(v, 'isoformat'):
                    item[k] = v.isoformat()

    # 2. Construct role-specific prompt
    prompt = f"""
    You are an intelligent backend GenAI agent responsible for powering an Agile Digital Scrum Master platform.
    Generate a {role} dashboard in JSON format using the provided delivery data snapshot.

    Data Snapshot:
    {json.dumps(data_snapshot, indent=2)}

    Role context and requirements:
    {ROLE_PROMPTS.get(role, "General dashboard requirements")}

    Return a JSON object matching this schema EXACTLY:
    {{
      "role": "{role}",
      "summary": "Detailed natural language overview of current state based on data",
      "metrics": {{
          "scope_completion": {{ "stories_done": 0, "stories_total": 0, "percent_complete": 0 }},
          "acceptance_criteria": [ {{ "story_id": "...", "criteria_met": true }} ],
          "release_readiness": {{ "uat_pass_rate": 0, "prod_deploy_success_rate": 0, "blocked_stories": 0 }},
          "flow_metrics": {{ "cycle_time_avg_days": 0, "lead_time_avg_days": 0, "throughput_per_sprint": 0 }},
          "ci_stability": {{ "dev_success_rate": 0, "uat_success_rate": 0, "prod_success_rate": 0, "rollback_events": 0 }},
          "risk_signals": {{ "defect_reopen_rate": 0, "uat_failure_spike": false, "blocker_count": 0 }}
      }},
      "visualisations": [
        {{ "type": "bar_chart", "title": "...", "data_source": "metrics.scope_completion" }},
        {{ "type": "table", "title": "...", "data_source": "metrics.acceptance_criteria" }},
        {{ "type": "gauge", "title": "...", "data_source": "metrics.release_readiness.uat_pass_rate" }}
      ],
      "drilldowns": {{
        "epic_to_story": true,
        "story_to_commit": true,
        "commit_to_build": true,
        "build_to_acceptance": true
      }},
      "alerts": [
        {{ "severity": "high", "message": "..." }}
      ]
    }}
    """

    # 3. Call Gemini
    response = await genai_service.generate_content(prompt)

    try:
        # Clean the response text if it contains markdown code blocks
        resp_text = response.text.strip()
        if resp_text.startswith("```json"):
            resp_text = resp_text[7:]
        if resp_text.endswith("```"):
            resp_text = resp_text[:-3]

        dashboard_data = json.loads(resp_text)
        return dashboard_data
    except Exception as e:
        logger.error(f"Error parsing Gemini response: {e}. Raw response: {response.text}")
        raise HTTPException(status_code=500, detail=f"Failed to generate dashboard data: {str(e)}")
