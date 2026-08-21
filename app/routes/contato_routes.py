from fastapi import APIRouter, Depends, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.controllers import contato_controller
from app.db.mongodb import get_database
from app.middlewares.auth_middleware import obter_usuario_atual
from app.schemas.auth import UsuarioLogado
from app.schemas.contact import ContatoCreate, ContatoListOut, ContatoOut

router = APIRouter(prefix="/api/contato", tags=["Fale Conosco"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def enviar_mensagem(dados: ContatoCreate, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Endpoint público usado pelo formulário "Fale Conosco" do site."""
    await contato_controller.receber_mensagem(db, dados)
    return {"detail": "Mensagem enviada com sucesso. Em breve entraremos em contato."}


@router.get("", response_model=ContatoListOut)
async def listar_mensagens(
    db: AsyncIOMotorDatabase = Depends(get_database),
    _usuario_atual: UsuarioLogado = Depends(obter_usuario_atual),
):
    return await contato_controller.listar_mensagens(db)


@router.patch("/{mensagem_id}/lida", response_model=ContatoOut)
async def marcar_mensagem_lida(
    mensagem_id: str,
    lida: bool = True,
    db: AsyncIOMotorDatabase = Depends(get_database),
    _usuario_atual: UsuarioLogado = Depends(obter_usuario_atual),
):
    return await contato_controller.marcar_mensagem(db, mensagem_id, lida)


@router.delete("/{mensagem_id}", status_code=status.HTTP_204_NO_CONTENT)
async def apagar_mensagem(
    mensagem_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    _usuario_atual: UsuarioLogado = Depends(obter_usuario_atual),
):
    await contato_controller.apagar_mensagem(db, mensagem_id)
