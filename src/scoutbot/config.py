from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMsSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )
    anthropic_api_key: SecretStr
    anthropic_model: str = "claude-haiku-4-5"
