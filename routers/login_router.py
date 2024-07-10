from github import Github
from authlib.integrations.starlette_client import OAuth
from fastapi import FastAPI, HTTPException, Request, Depends, APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from dotenv import load_dotenv
import os
import logging
from token_1 import my_git

logging_router = APIRouter()
load_dotenv()

templates = Jinja2Templates(directory="view")

logging.basicConfig(level=logging.DEBUG)

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
SECRET_KEY = os.getenv("SECRET_KEY")

if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET or not SECRET_KEY:
    raise ValueError("Faltan las credenciales de GitHub o la clave secreta en el archivo .env")

# Inicializar OAuth
oauth = OAuth()
oauth.register(
    name='github',
    client_id=GITHUB_CLIENT_ID,
    client_secret=GITHUB_CLIENT_SECRET,
    authorize_url='https://github.com/login/oauth/authorize',
    access_token_url='https://github.com/login/oauth/access_token',
    redirect_uri='http://localhost:8000/auth',
    client_kwargs={'scope': 'user:email repo'},
)

def get_current_user(request: Request):
    token = request.session.get('user')
    if not token:
        raise HTTPException(status_code=401, detail="No authenticated")

    # Autenticarse con el token de acceso
    github = Github(token)

    try:
        # Obtener el usuario autenticado
        user = github.get_user()
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener el usuario: {e}")

@logging_router.get("/", response_class=HTMLResponse)
def root(request: Request):
    request.session.clear()
    return templates.TemplateResponse("login.html", {"request": request})

@logging_router.get("/inicio", response_class=HTMLResponse)
async def inicio(request: Request, user: Github = Depends(get_current_user)):
    return templates.TemplateResponse("inicio.html", {"request": request, "user": user.login})

@logging_router.get("/login")
async def login(request: Request, redirect_to: str = "/inicio"):
    redirect_uri = request.url_for('auth')
    request.session['redirect_to'] = redirect_to  # Guardar la URL de redirección en la sesión
    return await oauth.github.authorize_redirect(request, redirect_uri)

@logging_router.get("/relogin")
async def relogin(request: Request, redirect_to: str = "/inicio"):
    # Limpiar la sesión antes de redirigir para forzar la reautenticación
    request.session.clear()
    redirect_uri = request.url_for('auth')
    request.session['redirect_to'] = redirect_to  # Guardar la URL de redirección en la sesión
    return await oauth.github.authorize_redirect(request, redirect_uri, prompt='login')

@logging_router.route('/auth')
async def auth(request: Request):
    token = await oauth.github.authorize_access_token(request)
    if token is None or 'access_token' not in token:
        raise HTTPException(status_code=401, detail="Token de acceso no obtenido")

    request.session['user'] = token['access_token']

    # Obtener la URL de redirección de la sesión
    redirect_to = request.session.pop('redirect_to', '/')

    return RedirectResponse(url=redirect_to)

@logging_router.get("/logout")
async def logout(request: Request):
    request.session.clear()  # Limpiar toda la sesión
    response = RedirectResponse(url='/logout_redirect')
    response.delete_cookie('session')  # Eliminar la cookie de sesión
    return response

@logging_router.get("/logout_redirect", response_class=HTMLResponse)
async def logout_redirect(request: Request):
    return templates.TemplateResponse("logout_redirect.html", {"request": request})