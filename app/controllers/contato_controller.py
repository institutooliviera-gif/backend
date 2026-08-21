"""
Controller responsável pela página "Fale Conosco": qualquer visitante pode
enviar uma mensagem (rota pública), e apenas administradores autenticados
podem listar, marcar como lida e apagar mensagens recebidas.
"""
from bson import ObjectId
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.contact import ContatoModel
from app.schemas.contact import ContatoCreate, ContatoListOut, ContatoOut


def _to_contato_out(doc: dict) -> ContatoOut:
    return ContatoOut(
        id=str(doc["_id"]),
        nome=doc["nome"],
        email=doc["email"],
        telefone=doc.get("telefone", ""),
        assunto=doc["assunto"],
        mensagem=doc["mensagem"],
        lida=doc.get("lida", False),
        criado_em=doc["criado_em"],
    )


async def receber_mensagem(db: AsyncIOMotorDatabase, dados: ContatoCreate) -> None:
    # Honeypot: formulário legítimo nunca preenche este campo (fica oculto por CSS).
    if dados.site_web:
        return  # finge sucesso pro robô, mas não grava nada

    mensagem = ContatoModel(
        nome=dados.nome,
        email=dados.email,
        telefone=dados.telefone,
        assunto=dados.assunto,
        mensagem=dados.mensagem,
    )
    await db.mensagens_contato.insert_one(mensagem.to_mongo())


async def listar_mensagens(db: AsyncIOMotorDatabase) -> ContatoListOut:
    total = await db.mensagens_contato.count_documents({})
    nao_lidas = await db.mensagens_contato.count_documents({"lida": False})
    cursor = db.mensagens_contato.find({}).sort("criado_em", -1)
    itens = [_to_contato_out(doc) async for doc in cursor]
    return ContatoListOut(total=total, nao_lidas=nao_lidas, itens=itens)


async def marcar_mensagem(db: AsyncIOMotorDatabase, mensagem_id: str, lida: bool) -> ContatoOut:
    if not ObjectId.is_valid(mensagem_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mensagem não encontrada.")
    doc = await db.mensagens_contato.find_one_and_update(
        {"_id": ObjectId(mensagem_id)},
        {"$set": {"lida": lida}},
        return_document=True,
    )
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mensagem não encontrada.")
    return _to_contato_out(doc)


async def apagar_mensagem(db: AsyncIOMotorDatabase, mensagem_id: str) -> None:
    if not ObjectId.is_valid(mensagem_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mensagem não encontrada.")
    resultado = await db.mensagens_contato.delete_one({"_id": ObjectId(mensagem_id)})
    if resultado.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mensagem não encontrada.")
