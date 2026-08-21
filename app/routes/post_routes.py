from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.controllers import transparencia_controller as posts_controller
from app.db.mongodb import get_database
from app.middlewares.auth_middleware import obter_usuario_atual
from app.models.post import CategoriaPost
from app.schemas.auth import UsuarioLogado
from app.schemas.post import PostCreate, PostListOut, PostOut, PostUpdate

router = APIRouter(prefix="/api/posts", tags=["Publicações (Transparência/Ações)"])


# ---------- Endpoints públicos (usados pelas páginas Ações e Transparência) ----------

@router.get("", response_model=PostListOut)
async def listar_publicacoes(
    categoria: CategoriaPost | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    tamanho_pagina: int = Query(default=9, ge=1, le=50),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    categoria_valor = categoria.value if categoria else None
    return await posts_controller.listar_posts_publico(db, categoria_valor, pagina, tamanho_pagina)


@router.get("/{post_id}", response_model=PostOut)
async def detalhar_publicacao(post_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    return await posts_controller.buscar_post(db, post_id)


# ---------- Endpoints administrativos (exigem login) ----------

@router.get("/admin/todas", response_model=PostListOut)
async def listar_todas_admin(
    pagina: int = Query(default=1, ge=1),
    tamanho_pagina: int = Query(default=10, ge=1, le=50),
    db: AsyncIOMotorDatabase = Depends(get_database),
    _usuario_atual: UsuarioLogado = Depends(obter_usuario_atual),
):
    return await posts_controller.listar_posts_admin(db, pagina, tamanho_pagina)


@router.post("", response_model=PostOut, status_code=status.HTTP_201_CREATED)
async def criar_publicacao(
    titulo: str = Form(...),
    resumo: str = Form(default=""),
    conteudo: str = Form(...),
    categoria: CategoriaPost = Form(default=CategoriaPost.ACAO_SOCIAL),
    publicado: bool = Form(default=True),
    imagem: UploadFile | None = File(default=None),
    db: AsyncIOMotorDatabase = Depends(get_database),
    usuario_atual: UsuarioLogado = Depends(obter_usuario_atual),
):
    dados = PostCreate(titulo=titulo, resumo=resumo, conteudo=conteudo, categoria=categoria, publicado=publicado)
    return await posts_controller.criar_post(db, dados, usuario_atual.id, usuario_atual.nome, imagem)


@router.put("/{post_id}", response_model=PostOut)
async def editar_publicacao(
    post_id: str,
    titulo: str | None = Form(default=None),
    resumo: str | None = Form(default=None),
    conteudo: str | None = Form(default=None),
    categoria: CategoriaPost | None = Form(default=None),
    publicado: bool | None = Form(default=None),
    remover_imagem: bool = Form(default=False),
    imagem: UploadFile | None = File(default=None),
    db: AsyncIOMotorDatabase = Depends(get_database),
    _usuario_atual: UsuarioLogado = Depends(obter_usuario_atual),
):
    dados = PostUpdate(
        titulo=titulo,
        resumo=resumo,
        conteudo=conteudo,
        categoria=categoria,
        publicado=publicado,
        remover_imagem=remover_imagem,
    )
    return await posts_controller.atualizar_post(db, post_id, dados, imagem)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def apagar_publicacao(
    post_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    _usuario_atual: UsuarioLogado = Depends(obter_usuario_atual),
):
    await posts_controller.apagar_post(db, post_id)
