"""
Model (camada M do MVC) que representa o documento de usuário administrador
na coleção `usuarios` do MongoDB. É quem tem permissão de publicar, editar
e apagar conteúdo na área de Transparência/Ações e de criar novos perfis.
"""
from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class CargoUsuario(str, Enum):
    PRESIDENTE = "presidente"
    DIRETORIA = "diretoria"
    EDITOR = "editor"


class UsuarioModel(BaseModel):
    nome: str
    email: EmailStr
    senha_hash: str
    cargo: CargoUsuario = CargoUsuario.EDITOR
    ativo: bool = True
    criado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_mongo(self) -> dict:
        return self.model_dump()
