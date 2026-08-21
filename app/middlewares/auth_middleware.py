"""
Dependency do FastAPI usada para proteger as rotas administrativas
(publicar/editar/apagar conteúdo, criar novos perfis). Extrai e valida o
JWT do cabeçalho Authorization: Bearer <token>.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.controllers.auth_controller import buscar_usuario_por_id
from app.core.security import JWTError, decode_access_token
from app.db.mongodb import get_database
from app.schemas.auth import UsuarioLogado

security_scheme = HTTPBearer()


async def obter_usuario_atual(
    credenciais: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> UsuarioLogado:
    credenciais_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sessão inválida ou expirada. Faça login novamente.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(credenciais.credentials)
        usuario_id = payload.get("sub")
        if usuario_id is None:
            raise credenciais_invalidas
    except JWTError as exc:
        raise credenciais_invalidas from exc

    usuario = await buscar_usuario_por_id(db, usuario_id)
    if not usuario or not usuario.get("ativo", True):
        raise credenciais_invalidas

    return UsuarioLogado(
        id=str(usuario["_id"]),
        nome=usuario["nome"],
        email=usuario["email"],
        cargo=usuario["cargo"],
    )
