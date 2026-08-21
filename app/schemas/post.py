from datetime import datetime

from pydantic import BaseModel, Field

from app.models.post import CategoriaPost


class PostCreate(BaseModel):
    titulo: str = Field(min_length=3, max_length=180)
    resumo: str = Field(default="", max_length=300)
    conteudo: str = Field(min_length=3)
    categoria: CategoriaPost = CategoriaPost.ACAO_SOCIAL
    publicado: bool = True


class PostUpdate(BaseModel):
    titulo: str | None = Field(default=None, min_length=3, max_length=180)
    resumo: str | None = Field(default=None, max_length=300)
    conteudo: str | None = Field(default=None, min_length=3)
    categoria: CategoriaPost | None = None
    publicado: bool | None = None
    remover_imagem: bool = False


class PostOut(BaseModel):
    id: str
    titulo: str
    resumo: str
    conteudo: str
    categoria: str
    imagem_url: str | None = None
    autor_nome: str
    publicado: bool
    criado_em: datetime
    atualizado_em: datetime


class PostListOut(BaseModel):
    total: int
    pagina: int
    tamanho_pagina: int
    itens: list[PostOut]
