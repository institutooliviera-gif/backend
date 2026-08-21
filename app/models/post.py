"""
Model (camada M do MVC) que representa uma publicação da área de
Transparência/Ações na coleção `posts` do MongoDB. O mesmo modelo é usado
tanto para prestação de contas quanto para o registro de ações sociais —
o campo `categoria` é o que diferencia onde cada publicação aparece no site.
"""
from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class CategoriaPost(str, Enum):
    ACAO_SOCIAL = "acao_social"
    PRESTACAO_CONTAS = "prestacao_contas"
    NOTICIA = "noticia"


class PostModel(BaseModel):
    titulo: str
    resumo: str = ""
    conteudo: str
    categoria: CategoriaPost = CategoriaPost.ACAO_SOCIAL
    imagem_url: str | None = None
    imagem_public_id: str | None = None  # id da imagem no Cloudinary (para permitir exclusão)
    autor_id: str
    autor_nome: str
    publicado: bool = True
    criado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    atualizado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_mongo(self) -> dict:
        return self.model_dump()
