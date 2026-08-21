"""
Camada de acesso a dados (a "Model" da arquitetura MVC conversa com o Mongo
através deste módulo). Usamos Motor, o driver assíncrono oficial do MongoDB,
para não bloquear o event loop do FastAPI.
"""
import asyncio
import logging

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ServerSelectionTimeoutError

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger("instituto_oliveira.db")


class MongoDatabase:
    client: AsyncIOMotorClient | None = None
    db: AsyncIOMotorDatabase | None = None


mongo = MongoDatabase()


async def connect_to_mongo(tentativas: int = 8, espera_inicial_segundos: float = 2.0) -> None:
    """
    Conecta ao MongoDB com retentativas e espera exponencial.

    Isso existe para o backend não "morrer" logo na inicialização quando o
    MongoDB ainda está subindo (comum no `docker compose up`, onde o
    container do Mongo pode levar alguns segundos a mais para aceitar
    conexões mesmo já passando no healthcheck) ou quando há uma
    instabilidade momentânea de rede até o MongoDB Atlas em produção.
    """
    espera = espera_inicial_segundos
    ultimo_erro: Exception | None = None

    for tentativa in range(1, tentativas + 1):
        try:
            cliente = AsyncIOMotorClient(settings.MONGODB_URI, serverSelectionTimeoutMS=5000)
            # força uma round-trip real ao servidor para validar a conexão agora,
            # em vez de descobrir o problema só na primeira requisição do usuário
            await cliente.admin.command("ping")

            mongo.client = cliente
            mongo.db = cliente[settings.MONGODB_DB_NAME]

            await mongo.db.usuarios.create_index("email", unique=True)
            await mongo.db.posts.create_index("categoria")
            await mongo.db.posts.create_index("criado_em")
            await mongo.db.mensagens_contato.create_index("criado_em")
            await mongo.db.mensagens_contato.create_index("lida")

            logger.info("Conectado ao MongoDB com sucesso (tentativa %d/%d).", tentativa, tentativas)
            return
        except ServerSelectionTimeoutError as erro:
            ultimo_erro = erro
            logger.warning(
                "Não foi possível conectar ao MongoDB (tentativa %d/%d). Tentando novamente em %.1fs…",
                tentativa, tentativas, espera,
            )
            await asyncio.sleep(espera)
            espera = min(espera * 1.6, 20)  # backoff exponencial, com teto de 20s

    raise RuntimeError(
        f"Não foi possível conectar ao MongoDB após {tentativas} tentativas. "
        f"Verifique MONGODB_URI e se o serviço do MongoDB está acessível."
    ) from ultimo_erro


async def close_mongo_connection() -> None:
    if mongo.client:
        mongo.client.close()


def get_database() -> AsyncIOMotorDatabase:
    if mongo.db is None:
        raise RuntimeError("Conexão com o MongoDB ainda não foi inicializada.")
    return mongo.db

