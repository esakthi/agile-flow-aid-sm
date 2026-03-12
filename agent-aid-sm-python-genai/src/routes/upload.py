from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db, Base, engine
from ..models import Epic, Story, Commit, CICDBuild, StatusHistory, Defect
from ..services.vector_service import VectorService
from ..services.genai_service import GenAIService
import json
import logging
import datetime
from sqlalchemy import text

router = APIRouter()
logger = logging.getLogger(__name__)
genai_service = GenAIService()
vector_service = VectorService(genai_service)

@router.post("/initialize")
async def initialize_db():
    logger.info("Initializing database tables")
    async with engine.begin() as conn:
        # Enable pgvector extension
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
    return {"message": "Database tables initialized"}

@router.post("/upload")
async def upload_data(files: list[UploadFile] = File(...), db: AsyncSession = Depends(get_db)):
    logger.info(f"Uploading {len(files)} files")

    for file in files:
        content = await file.read()
        data = json.loads(content)
        filename = file.filename.lower()

        if "epics" in filename:
            for item in data:
                epic = Epic(
                    epic_id=item["epicId"],
                    title=item["title"],
                    description=item["description"],
                    product_owner=item["productOwner"],
                    planned_start_date=datetime.datetime.fromisoformat(item["plannedStartDate"]),
                    planned_end_date=datetime.datetime.fromisoformat(item["plannedEndDate"]),
                    actual_start_date=datetime.datetime.fromisoformat(item["actualStartDate"]),
                    actual_end_date=datetime.datetime.fromisoformat(item["actualEndDate"]),
                    status=item["status"],
                    blockers=item["blockers"],
                    stories=item["stories"]
                )
                db.add(epic)
                await vector_service.add_to_vector_store(
                    db,
                    content=f"Epic: {epic.title}. Description: {epic.description}. PO: {epic.product_owner}. Status: {epic.status}",
                    entity_type="epic",
                    entity_id=epic.epic_id,
                    metadata=item
                )

        elif "stories" in filename:
            for item in data:
                story = Story(
                    jira_id=item["jiraId"],
                    epic_id=item["epicId"],
                    title=item["title"],
                    description=item["description"],
                    acceptance_criteria=item["acceptanceCriteria"],
                    story_points=item["storyPoints"],
                    priority=item["priority"],
                    assignee=item["assignee"],
                    type=item["type"],
                    status=item["status"],
                    created_at=datetime.datetime.fromisoformat(item["createdAt"]),
                    updated_at=datetime.datetime.fromisoformat(item["updatedAt"]),
                    comments=item["comments"],
                    commits=item["commits"],
                    cicd_deployments=item["cicdDeployments"],
                    on_plan=1 if item["onPlan"] else 0,
                    delay_days=item["delayDays"],
                    defects_linked=item["defectsLinked"]
                )
                db.add(story)
                await vector_service.add_to_vector_store(
                    db,
                    content=f"Story: {story.title}. Description: {story.description}. Status: {story.status}. Assignee: {story.assignee}",
                    entity_type="story",
                    entity_id=story.jira_id,
                    metadata=item
                )

        elif "commits" in filename:
            for item in data:
                commit = Commit(
                    sha=item["sha"],
                    jira_id=item["jiraId"],
                    author=item["author"],
                    timestamp=datetime.datetime.fromisoformat(item["timestamp"]),
                    message=item["message"],
                    lines_changed=item["linesChanged"],
                    files_changed=item["filesChanged"]
                )
                db.add(commit)
                # We could also vectorize commits if needed

        elif "cicd_builds" in filename:
            for item in data:
                build = CICDBuild(
                    build_id=item["buildId"],
                    jira_id=item["jiraId"],
                    environment=item["environment"],
                    status=item["status"],
                    timestamp=datetime.datetime.fromisoformat(item["timestamp"]),
                    duration_seconds=item["durationSeconds"],
                    failure_reason=item.get("failureReason", "")
                )
                db.add(build)

        elif "status_histories" in filename:
            for item in data:
                history = StatusHistory(
                    jira_id=item["jiraId"],
                    from_status=item["fromStatus"],
                    to_status=item["toStatus"],
                    timestamp=datetime.datetime.fromisoformat(item["timestamp"]),
                    duration_hours=item["durationHours"]
                )
                db.add(history)

        elif "defects" in filename:
            for item in data:
                defect = Defect(
                    defect_id=item["defectId"],
                    jira_id=item["jiraId"],
                    title=item["title"],
                    severity=item["severity"],
                    status=item["status"],
                    reopen_count=item["reopenCount"],
                    created_at=datetime.datetime.fromisoformat(item["createdAt"]),
                    resolved_at=datetime.datetime.fromisoformat(item["resolvedAt"]) if item["resolvedAt"] else None
                )
                db.add(defect)

    await db.commit()
    return {"message": "Data uploaded and vectorized successfully"}
