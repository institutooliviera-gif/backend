"""
Controller responsável pela gestão de perfis administradores: criar novo
perfil, listar, atualizar cargo/senha e desativar. Somente usuários já
autenticados (ver middlewares/auth_middleware.py) podem acessar estas ações.
"""
from bson import ObjectId
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.security import hash_password
from app.models.user import UsuarioModel
from app.schemas.user import UsuarioCreate, UsuarioOut, UsuarioUpdate


def _to_usuario_out(doc: dict) -> UsuarioOut:
    return UsuarioOut(
        id=str(doc["_id"]),
        nome=doc["nome"],
        email=doc["email"],
        cargo=doc["cargo"],
        ativo=doc.get("ativo", True),
        criado_em=doc["criado_em"],
    )


async def criar_usuario(db: AsyncIOMotorDatabase, dados: UsuarioCreate) -> UsuarioOut:
    existente = await db.usuarios.find_one({"email": dados.email})
    if existente:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe um usuário com este e-mail.")

    usuario = UsuarioModel(
        nome=dados.nome,
        email=dados.email,
        senha_hash=hash_password(dados.senha),
        cargo=dados.cargo,
    )
    resultado = await db.usuarios.insert_one(usuario.to_mongo())
    doc = await db.usuarios.find_one({"_id": resultado.inserted_id})
    return _to_usuario_out(doc)


async def listar_usuarios(db: AsyncIOMotorDatabase) -> list[UsuarioOut]:
    cursor = db.usuarios.find().sort("criado_em", -1)
    return [_to_usuario_out(doc) async for doc in cursor]


async def atualizar_usuario(db: AsyncIOMotorDatabase, usuario_id: str, dados: UsuarioUpdate) -> UsuarioOut:
    if not ObjectId.is_valid(usuario_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")

    atualizacoes = {k: v for k, v in dados.model_dump(exclude_unset=True).items() if k != "senha"}
    if dados.senha:
        atualizacoes["senha_hash"] = hash_password(dados.senha)

    if not atualizacoes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nenhum dado para atualizar.")

    resultado = await db.usuarios.find_one_and_update(
        {"_id": ObjectId(usuario_id)},
        {"$set": atualizacoes},
        return_document=True,
    )
    if not resultado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
    return _to_usuario_out(resultado)


async def remover_usuario(db: AsyncIOMotorDatabase, usuario_id: str, usuario_logado_id: str) -> None:
    if usuario_id == usuario_logado_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você não pode remover o próprio perfil enquanto está logado.",
        )
    if not ObjectId.is_valid(usuario_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")

    resultado = await db.usuarios.delete_one({"_id": ObjectId(usuario_id)})
    if resultado.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
