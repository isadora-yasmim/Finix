"""Configuração central da aplicação (lida de variáveis de ambiente / .env)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Ambiente
    environment: str = "development"
    project_name: str = "Finix"
    version: str = "0.1.0"

    # Banco de dados
    database_url: str = "postgresql+psycopg://finix:changeme@db:5432/finix"

    # Segurança (placeholders — auth real vem no Épico B)
    secret_key: str = "change-me-in-production"

    # CORS — origens separadas por vírgula
    backend_cors_origins: str = "http://localhost:5173"

    # LLM (camada opcional — desligada por padrão, ver PROJECT.md §10)
    llm_enabled: bool = False
    llm_provider: str = ""
    llm_api_key: str = ""

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.backend_cors_origins.split(",") if o.strip()]


settings = Settings()
