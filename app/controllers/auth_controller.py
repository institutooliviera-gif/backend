"""
Controller (camada C do MVC) responsável pela lógica de autenticação.
As rotas (routes/auth_routes.py) apenas recebem a requisição HTTP e delegam
a este controller, que fala com o Model/banco e aplica as regras de negócio.
"""
from bson import ObjectId
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.security import create_access_token, verify_password
from app.schemas.auth import LoginRequest, TokenResponse


async def autenticar_usuario(db: AsyncIOMotorDatabase, dados: LoginRequest) -> TokenResponse:
    usuario = await db.usuarios.find_one({"email": dados.email})
    if not usuario or not usuario.get("ativo", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos.",
        )

    if not verify_password(dados.senha, usuario["senha_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos.",
        )

    token = create_access_token(
        subject=str(usuario["_id"]),
        extra_claims={"nome": usuario["nome"], "cargo": usuario["cargo"]},
    )
    return TokenResponse(access_token=token)


async def buscar_usuario_por_id(db: AsyncIOMotorDatabase, usuario_id: str) -> dict | None:
    if not ObjectId.is_valid(usuario_id):
        return None
    return await db.usuarios.find_one({"_id": ObjectId(usuario_id)})
