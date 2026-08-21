"""
Ponto de entrada da API do Instituto Oliveira.

Arquitetura MVC:
  - models/      -> formato dos documentos guardados no MongoDB
  - schemas/      -> formato dos dados que entram/saem pela API (request/response)
  - controllers/  -> regras de negócio (a "Model" ativa: fala com o banco)
  - routes/       -> a "View" da API: define os endpoints HTTP e delega ao controller
  - middlewares/  -> autenticação/autorização compartilhada entre rotas
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db.mongodb import close_mongo_connection, connect_to_mongo
from app.routes import auth_routes, contato_routes, post_routes, user_routes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(
    title=settings.APP_NAME,
    description="API institucional do Instituto Oliveira Projetos Sociais e Culturais.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(post_routes.router)
app.include_router(contato_routes.router)


@app.get("/", tags=["Status"])
async def raiz():
    return {"servico": settings.APP_NAME, "status": "online"}


@app.get("/api/health", tags=["Status"])
async def health_check():
    return {"status": "ok"}
