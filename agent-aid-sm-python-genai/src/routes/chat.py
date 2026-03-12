from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..services.genai_service import GenAIService
from ..services.vector_service import VectorService
from ..schemas import ChatQuery, ChatResponse
import logging
import json

router = APIRouter()
logger = logging.getLogger(__name__)
genai_service = GenAIService()
vector_service = VectorService(genai_service)

@router.post("/chat", response_model=ChatResponse)
async def chat(
    query: str = Form(...),
    role: str = Form(...),
    deep_search: bool = Form(False),
    image: UploadFile = File(None),
    db: AsyncSession = Depends(get_db)
):
    logger.info(f"Chat query from {role}: {query}, deep_search: {deep_search}")

    # 1. Retrieve context from vector store
    similar_docs = await vector_service.search_similar(db, query)
    context = "\n".join([doc.content for doc in similar_docs])

    # 2. If image provided, analyze it
    image_analysis = ""
    if image:
        image_bytes = await image.read()
        image_analysis = await genai_service.analyze_image(f"Analyze this image (could be a JIRA board) in context of the agile project and user query: {query}", image_bytes)
        logger.info(f"Image analysis result: {image_analysis[:100]}...")

    # 3. Construct prompt
    prompt = f"""
    You are an intelligent backend GenAI agent for an Agile Digital Scrum Master platform.
    User role: {role}

    Context from vectorized delivery data:
    {context}

    Image analysis (if any):
    {image_analysis}

    User query: {query}

    Provide a detailed and helpful response grounded in the provided context and data.
    If 'deep_search' was requested, you have access to Google Search grounding.

    Also provide a 'voice_summary' - a short, concise version of your response suitable for text-to-speech playback.

    Return your response as a JSON object with 'response' and 'voice_summary' keys.
    """

    # 4. Call Gemini
    response = await genai_service.generate_content(prompt, search_grounding=deep_search)

    try:
        resp_text = response.text.strip()
        if resp_text.startswith("```json"):
            resp_text = resp_text[7:]
        if resp_text.endswith("```"):
            resp_text = resp_text[:-3]

        resp_data = json.loads(resp_text)
        return ChatResponse(
            response=resp_data.get("response", resp_text),
            role=role,
            voice_summary=resp_data.get("voice_summary"),
            grounding_metadata=getattr(response, 'grounding_metadata', None)
        )
    except Exception as e:
        logger.error(f"Error parsing Gemini chat response: {e}")
        return ChatResponse(
            response=response.text,
            role=role,
            voice_summary=response.text[:200]
        )
