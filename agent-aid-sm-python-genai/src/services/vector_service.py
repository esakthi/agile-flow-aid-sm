from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from ..models import VectorStore
from .genai_service import GenAIService
import logging
import json

logger = logging.getLogger(__name__)

class VectorService:
    def __init__(self, genai_service: GenAIService):
        self.genai_service = genai_service

    async def add_to_vector_store(self, db: AsyncSession, content: str, entity_type: str, entity_id: str, metadata: dict):
        logger.info(f"Adding {entity_type} {entity_id} to vector store")
        embedding = await self.genai_service.get_embedding(content)

        vector_entry = VectorStore(
            content=content,
            extra_metadata=metadata,
            embedding=embedding,
            entity_type=entity_type,
            entity_id=entity_id
        )
        db.add(vector_entry)
        await db.commit()

    async def search_similar(self, db: AsyncSession, query: str, limit: int = 5):
        logger.info(f"Searching vector store for query: {query}")
        query_embedding = await self.genai_service.get_embedding(query)

        # Using pgvector distance operator <=> for cosine distance
        stmt = select(VectorStore).order_by(VectorStore.embedding.cosine_distance(query_embedding)).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()
