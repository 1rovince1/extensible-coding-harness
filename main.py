from config.env_config import env_settings
from config.logger_config import setup_logging
setup_logging(LOG_DIR=env_settings.LOG_DIR, LOG_FILE=env_settings.LOG_FILE)

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from clients.ollama_llm_client import ollama_manager
from clients.openai_llm_client import openai_manager
from clients.redis_client import redis_manager
from coding_harness.skill_registries.main_agent_skill_registry import main_agent_skill_registry
from coding_harness.skill_registries.generic_sub_agent_skill_registry import generic_sub_agent_skill_registry
from api.routes.coding_harness import router as CodingRouter
from api.routes.session_management import router as SessionRouter


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    await ollama_manager.connect()
    await openai_manager.connect()
    await redis_manager.connect()
    await main_agent_skill_registry.initialize_skills()
    await generic_sub_agent_skill_registry.initialize_skills()
    yield
    await redis_manager.disconnect()
    await openai_manager.disconnect()
    await ollama_manager.disconnect()

fastapi_app = FastAPI(
    title="Harness server",
    lifespan=app_lifespan
)

fastapi_app.add_middleware(
    CORSMiddleware,
    # allow_origins=[
    #     "http://127.0.0.1:5555",
    #     "http://localhost:5555"
    # ],
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

fastapi_app.include_router(CodingRouter)
fastapi_app.include_router(SessionRouter)


@fastapi_app.get("/")
async def health_check():
    return {
        "status": "OK",
        "message": "FastAPI server is up and running!"
    }
