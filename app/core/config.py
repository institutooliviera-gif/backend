"""
Configurações centrais da aplicação.
Todas as variáveis sensíveis vêm de variáveis de ambiente (.env em desenvolvimento,
"Environment Variables" no painel do Render em produção). Nada de credenciais
hard-coded no código-fonte.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Geral
    APP_NAME: str = "Instituto Oliveira API"
    ENV: str = "development"  # development | production

    # MongoDB
    MONGODB_URI: str
    MONGODB_DB_NAME: str = "instituto_oliveira"

    # Segurança / JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60 * 12  # 12 horas

    # CORS – domínios que podem consumir a API
    # Ex: "https://www.institutooliveira.com,https://institutooliveira.com,http://localhost:5500"
    CORS_ORIGINS: str = "http://localhost:5500,http://127.0.0.1:5500"

    # Cloudinary (armazenamento de imagens – o Render tem disco efêmero,
    # então as imagens enviadas pelo painel administrativo não podem ficar
    # salvas localmente, precisam de um serviço externo)
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    # Primeiro usuário administrador (usado apenas pelo script de seed)
    ADMIN_SEED_NOME: str = "Francisca Oliveira Lopes"
    ADMIN_SEED_EMAIL: str = "institutooliveira7@gmail.com"
    ADMIN_SEED_SENHA: str = "TrocarEssaSenha123!"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
