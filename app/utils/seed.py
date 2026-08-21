"""
Script de inicialização: cria o primeiro usuário administrador (por padrão,
a presidente Francisca Oliveira Lopes) para que seja possível fazer login
no painel administrativo pela primeira vez.

Não existe endpoint público de cadastro por segurança — novos perfis só
podem ser criados por quem já está autenticado (rota POST /api/usuarios).

Uso (rodar uma única vez, localmente ou via "Shell" do Render):
    python -m app.utils.seed
"""
import asyncio

from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import get_settings
from app.core.security import hash_password
from app.models.user import CargoUsuario, UsuarioModel

settings = get_settings()


async def main() -> None:
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_DB_NAME]

    existente = await db.usuarios.find_one({"email": settings.ADMIN_SEED_EMAIL})
    if existente:
        print(f"Usuário administrador '{settings.ADMIN_SEED_EMAIL}' já existe. Nada a fazer.")
        client.close()
        return

    usuario = UsuarioModel(
        nome=settings.ADMIN_SEED_NOME,
        email=settings.ADMIN_SEED_EMAIL,
        senha_hash=hash_password(settings.ADMIN_SEED_SENHA),
        cargo=CargoUsuario.PRESIDENTE,
    )
    await db.usuarios.insert_one(usuario.to_mongo())
    print(f"Usuário administrador criado com sucesso: {settings.ADMIN_SEED_EMAIL}")
    print("IMPORTANTE: faça login e troque a senha padrão imediatamente.")
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
