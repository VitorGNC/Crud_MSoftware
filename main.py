from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.views.alterar_infos import router as alterar_infos_router
from app.views.gerenciar_usuarios import router as gerenciar_usuarios_router

# Cria tabelas no banco (SQLite)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Crud_MSoftware API",
    description=(
        "API REST no padrão MVC para gerenciamento de usuários e mídias.\n\n"
        "**Usuário**: cadastro, edição de dados próprios, upload e exclusão de mídias.\n"
        "**Administrador**: gerencia todos os usuários, altera permissões e visualiza mídias."
    ),
    version="1.0.0",
)

# Serve arquivos de upload como estáticos
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Routers
app.include_router(alterar_infos_router)
app.include_router(gerenciar_usuarios_router)


@app.get("/", tags=["Root"])
def root():
    return {"message": "Crud_MSoftware API está no ar. Acesse /docs para a documentação."}
