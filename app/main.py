from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from app.routers import login_router, repositories_router, user_router, teams_router
from starlette.middleware.sessions import SessionMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Cargar la clave secreta desde el archivo .env
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("Falta la clave secreta en el archivo .env")

# Agregar el middleware de sesión
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Incluir el router de login:
app.include_router(login_router.logging_router, tags=["Sesión"])
# Incluir el router de repositorios:
app.include_router(repositories_router.repository_router, tags=["Repositorio"])
# Incluir el router de usuarios:
app.include_router(user_router.user_router, tags=["Usuario"])
# Incluir el router de equipos:
app.include_router(teams_router.teams_router, tags=["Teams"])

templates = Jinja2Templates(directory="./view")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
    