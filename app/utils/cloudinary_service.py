"""
Serviço de upload de imagens. Usamos o Cloudinary porque o disco do Render
é efêmero (some a cada deploy/restart), então não é seguro guardar as fotos
enviadas pelo painel administrativo no próprio servidor. O Cloudinary tem um
plano gratuito que é suficiente para o volume de um site institucional.
"""
import cloudinary
import cloudinary.uploader
from fastapi import UploadFile

from app.core.config import get_settings

settings = get_settings()

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)

PASTA_UPLOADS = "instituto-oliveira/posts"


async def enviar_imagem(arquivo: UploadFile) -> dict:
    """Envia a imagem para o Cloudinary e retorna a url segura + public_id."""
    conteudo = await arquivo.read()
    resultado = cloudinary.uploader.upload(
        conteudo,
        folder=PASTA_UPLOADS,
        resource_type="image",
        overwrite=True,
    )
    return {"url": resultado["secure_url"], "public_id": resultado["public_id"]}


def remover_imagem(public_id: str) -> None:
    if public_id:
        cloudinary.uploader.destroy(public_id)
