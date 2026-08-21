from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.user import CargoUsuario


class UsuarioCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=72)
    cargo: CargoUsuario = CargoUsuario.EDITOR


class UsuarioUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=120)
    cargo: CargoUsuario | None = None
    ativo: bool | None = None
    senha: str | None = Field(default=None, min_length=8, max_length=72)


class UsuarioOut(BaseModel):
    id: str
    nome: str
    email: EmailStr
    cargo: str
    ativo: bool
    criado_em: datetime
