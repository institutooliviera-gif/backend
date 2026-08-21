from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class ContatoCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    email: EmailStr
    telefone: str = Field(default="", max_length=30)
    assunto: str = Field(min_length=2, max_length=160)
    mensagem: str = Field(min_length=5, max_length=4000)

    # honeypot anti-spam: campo invisível para humanos; se vier preenchido,
    # é quase certeza que foi um robô que enviou o formulário.
    site_web: str = Field(default="", max_length=200)


class ContatoOut(BaseModel):
    id: str
    nome: str
    email: EmailStr
    telefone: str
    assunto: str
    mensagem: str
    lida: bool
    criado_em: datetime


class ContatoListOut(BaseModel):
    total: int
    nao_lidas: int
    itens: list[ContatoOut]
