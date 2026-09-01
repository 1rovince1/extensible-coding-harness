from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    OPENAI_COMPATIBLE_LLM_HOST_URL: str = "https://ollama.com/v1"
    OPENAI_COMPATIBLE_LLM_API_KEY: str = ""
    OPENAI_COMPATIBLE_MAIN_AGENT_LLM: str = "gemma4:cloud"
    OPENAI_COMPATIBLE_GENERIC_SUB_AGENT_LLM: str = "gemma4:cloud"
    OPENAI_COMPATIBLE_CONTEXT_COMPRESSION_LLM: str = "gpt-oss:120b-cloud"

    OLLAMA_HOST: str = "https://ollama.com"
    OLLAMA_API_KEY: str = ""
    OLLAMA_MAIN_AGENT_MODEL: str = "gemma4:cloud"
    OLLAMA_SUB_AGENT_MODEL: str = "gemma4:cloud"
    OLLAMA_CONTEXT_COMPRESSION_MODEL: str = "gpt-oss:120b-cloud"

    LLM_PROVIDER_API: Literal[
        "openai_chat_completions",
        "openai_responses",
        "ollama"
    ] = "openai_responses"

    CONTEXT_TOKENS_ALLOWED: int = 65536
    AGENT_WORK_DIR: str

    SHELL_COMMANDS_ALLOWED: list = [
        "ls",
        "grep",
        # "rm",
        "cat",
        "echo",
        "sed",
        "mkdir",
        "find",
        "cp",
        "mv",
        "head",
        "tail",
        "patch"
    ]

    LOG_DIR: str = "dev_logs"
    LOG_FILE: str = "app.log"

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int = 0
    REDIS_POOL_MAX_CONNECTIONS: int = 20

    CHAT_SESSION_EXPIRATION_TIME: int


env_settings = EnvSettings()