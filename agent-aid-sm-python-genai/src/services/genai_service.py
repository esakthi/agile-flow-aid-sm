import os
import logging
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GenAIService:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            logger.error("GOOGLE_API_KEY not found in environment variables")
        self.client = genai.Client(api_key=self.api_key)
        self.model_id = "gemini-2.0-flash" # Use a stable or latest version
        self.embedding_model_id = "text-embedding-004"

    async def generate_content(self, prompt: str, search_grounding: bool = False):
        logger.info(f"Generating content with model {self.model_id}, grounding: {search_grounding}")
        try:
            tools = []
            if search_grounding:
                tools.append(types.Tool(google_search=types.GoogleSearch()))

            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=tools,
                    response_mime_type="application/json"
                )
            )
            return response
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            raise e

    async def get_embedding(self, text: str):
        logger.info(f"Generating embedding for text length {len(text)}")
        try:
            response = self.client.models.embed_content(
                model=self.embedding_model_id,
                contents=text
            )
            return response.embeddings[0].values
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise e

    async def analyze_image(self, prompt: str, image_bytes: bytes):
        logger.info("Analyzing image with Gemini")
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[
                    prompt,
                    types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
                ]
            )
            return response.text
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            raise e
