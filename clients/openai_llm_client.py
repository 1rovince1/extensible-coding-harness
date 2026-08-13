import logging

from openai import AsyncClient

from config.env_config import env_settings

logger = logging.getLogger(__name__)


class OpenAIClient:
    def __init__(self):
        self.client = None

    async def connect(self):
        logger.info("Connecting to OpenAI client...")
        self.client = AsyncClient(
            base_url=env_settings.OPENAI_COMPATIBLE_LLM_HOST_URL,
            api_key=env_settings.OPENAI_COMPATIBLE_LLM_API_KEY
        )
        logger.info("Connected to OpenAI client!")

    async def disconnect(self):
        logger.info("Disconnecting OpenAI client...")
        self.client = None
        logger.info("Disconnected OpenAI client!")


openai_manager = OpenAIClient()