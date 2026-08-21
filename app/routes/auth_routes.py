from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.controllers.auth_controller import autenticar_usuario
from app.db.mongodb import get_database
from app.middlewares.auth_middleware import obter_usuario_atual
from app.schemas.auth import LoginRequest, TokenResponse, UsuarioLogado

router = APIRouter(prefix="/api/auth", tags=["Autenticação"])


@router.post("/login", response_model=TokenResponse)
async def login(dados: LoginRequest, db: AsyncIOMotorDatabase = Depends(get_database)):
    return await autenticar_usuario(db, dados)


@router.get("/me", response_model=UsuarioLogado)
async def me(usuario_atual: UsuarioLogado = Depends(obter_usuario_atual)):
    return usuario_atual
