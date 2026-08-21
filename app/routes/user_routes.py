from fastapi import APIRouter, Depends, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.controllers import user_controller
from app.db.mongodb import get_database
from app.middlewares.auth_middleware import obter_usuario_atual
from app.schemas.auth import UsuarioLogado
from app.schemas.user import UsuarioCreate, UsuarioOut, UsuarioUpdate

router = APIRouter(prefix="/api/usuarios", tags=["Usuários administradores"])


@router.post("", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
async def criar_novo_perfil(
    dados: UsuarioCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    _usuario_atual: UsuarioLogado = Depends(obter_usuario_atual),
):
    """Cria um novo perfil administrador. Requer estar autenticado."""
    return await user_controller.criar_usuario(db, dados)


@router.get("", response_model=list[UsuarioOut])
async def listar_perfis(
    db: AsyncIOMotorDatabase = Depends(get_database),
    _usuario_atual: UsuarioLogado = Depends(obter_usuario_atual),
):
    return await user_controller.listar_usuarios(db)


@router.put("/{usuario_id}", response_model=UsuarioOut)
async def editar_perfil(
    usuario_id: str,
    dados: UsuarioUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    _usuario_atual: UsuarioLogado = Depends(obter_usuario_atual),
):
    return await user_controller.atualizar_usuario(db, usuario_id, dados)


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remover_perfil(
    usuario_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    usuario_atual: UsuarioLogado = Depends(obter_usuario_atual),
):
    await user_controller.remover_usuario(db, usuario_id, usuario_atual.id)
