"""
Controller responsável pela área de Transparência/Ações: publicar (texto +
imagem opcional), listar publicamente com paginação e filtro por categoria,
editar e apagar. É o núcleo do "site de transparência" pedido — o mesmo
conjunto de regras atende tanto o feed público quanto o painel administrativo.
"""
import math

from bson import ObjectId
from fastapi import HTTPException, UploadFile, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.post import PostModel
from app.schemas.post import PostCreate, PostListOut, PostOut, PostUpdate
from app.utils.cloudinary_service import enviar_imagem, remover_imagem


def _to_post_out(doc: dict) -> PostOut:
    return PostOut(
        id=str(doc["_id"]),
        titulo=doc["titulo"],
        resumo=doc.get("resumo", ""),
        conteudo=doc["conteudo"],
        categoria=doc["categoria"],
        imagem_url=doc.get("imagem_url"),
        autor_nome=doc["autor_nome"],
        publicado=doc.get("publicado", True),
        criado_em=doc["criado_em"],
        atualizado_em=doc["atualizado_em"],
    )


async def criar_post(
    db: AsyncIOMotorDatabase,
    dados: PostCreate,
    autor_id: str,
    autor_nome: str,
    imagem: UploadFile | None,
) -> PostOut:
    imagem_url = None
    imagem_public_id = None
    if imagem is not None and imagem.filename:
        upload = await enviar_imagem(imagem)
        imagem_url, imagem_public_id = upload["url"], upload["public_id"]

    post = PostModel(
        titulo=dados.titulo,
        resumo=dados.resumo,
        conteudo=dados.conteudo,
        categoria=dados.categoria,
        imagem_url=imagem_url,
        imagem_public_id=imagem_public_id,
        autor_id=autor_id,
        autor_nome=autor_nome,
        publicado=dados.publicado,
    )
    resultado = await db.posts.insert_one(post.to_mongo())
    doc = await db.posts.find_one({"_id": resultado.inserted_id})
    return _to_post_out(doc)


async def listar_posts_publico(
    db: AsyncIOMotorDatabase,
    categoria: str | None,
    pagina: int,
    tamanho_pagina: int,
) -> PostListOut:
    filtro: dict = {"publicado": True}
    if categoria:
        filtro["categoria"] = categoria

    total = await db.posts.count_documents(filtro)
    cursor = (
        db.posts.find(filtro)
        .sort("criado_em", -1)
        .skip((pagina - 1) * tamanho_pagina)
        .limit(tamanho_pagina)
    )
    itens = [_to_post_out(doc) async for doc in cursor]
    return PostListOut(total=total, pagina=pagina, tamanho_pagina=tamanho_pagina, itens=itens)


async def listar_posts_admin(db: AsyncIOMotorDatabase, pagina: int, tamanho_pagina: int) -> PostListOut:
    total = await db.posts.count_documents({})
    cursor = (
        db.posts.find({})
        .sort("criado_em", -1)
        .skip((pagina - 1) * tamanho_pagina)
        .limit(tamanho_pagina)
    )
    itens = [_to_post_out(doc) async for doc in cursor]
    return PostListOut(total=total, pagina=pagina, tamanho_pagina=tamanho_pagina, itens=itens)


async def buscar_post(db: AsyncIOMotorDatabase, post_id: str) -> PostOut:
    if not ObjectId.is_valid(post_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publicação não encontrada.")
    doc = await db.posts.find_one({"_id": ObjectId(post_id)})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publicação não encontrada.")
    return _to_post_out(doc)


async def atualizar_post(
    db: AsyncIOMotorDatabase,
    post_id: str,
    dados: PostUpdate,
    imagem: UploadFile | None,
) -> PostOut:
    if not ObjectId.is_valid(post_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publicação não encontrada.")

    doc_atual = await db.posts.find_one({"_id": ObjectId(post_id)})
    if not doc_atual:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publicação não encontrada.")

    atualizacoes = dados.model_dump(exclude_unset=True, exclude={"remover_imagem"})

    if imagem is not None and imagem.filename:
        if doc_atual.get("imagem_public_id"):
            remover_imagem(doc_atual["imagem_public_id"])
        upload = await enviar_imagem(imagem)
        atualizacoes["imagem_url"] = upload["url"]
        atualizacoes["imagem_public_id"] = upload["public_id"]
    elif dados.remover_imagem:
        if doc_atual.get("imagem_public_id"):
            remover_imagem(doc_atual["imagem_public_id"])
        atualizacoes["imagem_url"] = None
        atualizacoes["imagem_public_id"] = None

    from datetime import datetime, timezone

    atualizacoes["atualizado_em"] = datetime.now(timezone.utc)

    doc = await db.posts.find_one_and_update(
        {"_id": ObjectId(post_id)},
        {"$set": atualizacoes},
        return_document=True,
    )
    return _to_post_out(doc)


async def apagar_post(db: AsyncIOMotorDatabase, post_id: str) -> None:
    if not ObjectId.is_valid(post_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publicação não encontrada.")

    doc = await db.posts.find_one({"_id": ObjectId(post_id)})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publicação não encontrada.")

    if doc.get("imagem_public_id"):
        remover_imagem(doc["imagem_public_id"])

    await db.posts.delete_one({"_id": ObjectId(post_id)})


def total_paginas(total: int, tamanho_pagina: int) -> int:
    return max(1, math.ceil(total / tamanho_pagina))
