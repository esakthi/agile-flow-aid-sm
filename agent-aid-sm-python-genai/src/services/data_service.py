from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ..models import Epic, Story, Commit, CICDBuild, StatusHistory, Defect
import logging

logger = logging.getLogger(__name__)

class DataService:
    @staticmethod
    async def get_po_metrics(db: AsyncSession):
        total_stories = await db.scalar(select(func.count(Story.jira_id)))
        done_stories = await db.scalar(select(func.count(Story.jira_id)).where(Story.status == 'Done'))

        # This is a simplification; you'd want more complex logic for a real dashboard
        return {
            "scope_completion": {
                "stories_done": done_stories,
                "stories_total": total_stories,
                "percent_complete": (done_stories / total_stories * 100) if total_stories > 0 else 0
            }
        }

    @staticmethod
    async def get_all_normalized_data(db: AsyncSession):
        # Fetch a snapshot of everything for the LLM to analyze
        epics = (await db.execute(select(Epic))).scalars().all()
        stories = (await db.execute(select(Story).limit(100))).scalars().all() # Limit for prompt size
        builds = (await db.execute(select(CICDBuild).limit(50))).scalars().all()

        return {
            "epics": [e.__dict__ for e in epics],
            "stories": [s.__dict__ for s in stories],
            "builds": [b.__dict__ for b in builds]
        }
