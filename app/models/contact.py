"""
Model (camada M do MVC) que representa uma mensagem enviada pelo formulário
público "Fale Conosco" na coleção `mensagens_contato` do MongoDB.
"""
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class ContatoModel(BaseModel):
    nome: str
    email: str
    telefone: str = ""
    assunto: str
    mensagem: str
    lida: bool = False
    criado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_mongo(self) -> dict:
        return self.model_dump()
