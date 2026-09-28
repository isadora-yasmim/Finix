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

    # Segurança — TROQUE em produção (>= 32 bytes). Ex.: secrets.token_urlsafe(32)
    secret_key: str = "change-me-in-production-please-use-a-long-random-secret"

    # JWT (token de acesso assinado com HS256 sobre secret_key)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # Cookie do refresh token (HttpOnly + Secure + SameSite, PROJECT.md §10)
    refresh_cookie_name: str = "finix_refresh"
    refresh_cookie_path: str = "/auth"
    # secure=False em dev (HTTP); ligue em produção (HTTPS) via .env.
    cookie_secure: bool = False
    cookie_samesite: str = "lax"

    # Rate limiting (slowapi). Desligável em testes/ambientes específicos.
    rate_limit_enabled: bool = True
    rate_limit_auth: str = "10/minute"
    rate_limit_upload: str = "20/minute"

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
