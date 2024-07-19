import logging
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from authlib.integrations.starlette_client import OAuth
from github import Github
from starlette.templating import Jinja2Templates
import os

logging_router = APIRouter()
templates = Jinja2Templates(directory="view")

oauth = OAuth()
oauth.register(
    name='github',
    client_id=os.getenv('GITHUB_CLIENT_ID'),
    client_secret=os.getenv('GITHUB_CLIENT_SECRET'),
    authorize_url='https://github.com/login/oauth/authorize',
    access_token_url='https://github.com/login/oauth/access_token',
    redirect_uri='http://localhost:8000/auth',
    client_kwargs={'scope': 'user:email repo'},
)

def get_current_user(request: Request):
    token = request.session.get('user')
    if not token:
        raise HTTPException(status_code=401, detail="No authenticated")
    
    try:
        github = Github(token)
        user = github.get_user()
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener el usuario: {e}")

@logging_router.get("/", response_class=HTMLResponse)
def root(request: Request):
    logging.info("Ruta / llamada")
    request.session.clear()
    return templates.TemplateResponse("login.html", {"request": request})

@logging_router.get("/inicio", response_class=HTMLResponse)
async def inicio(request: Request, user: Github = Depends(get_current_user)):
    logging.info("Ruta /inicio llamada")
    return templates.TemplateResponse("inicio.html", {"request": request, "user": user.login})

@logging_router.get("/login")
async def login(request: Request, redirect_to: str = "/inicio"):
    logging.info("Ruta /login llamada")
    redirect_uri = request.url_for('auth')
    request.session['redirect_to'] = redirect_to
    return await oauth.github.authorize_redirect(request, redirect_uri)

@logging_router.get("/relogin")
async def relogin(request: Request, redirect_to: str = "/inicio"):
    logging.info("Ruta /relogin llamada")
    request.session.clear()
    redirect_uri = request.url_for('auth')
    request.session['redirect_to'] = redirect_to
    return await oauth.github.authorize_redirect(request, redirect_uri, prompt='login')

@logging_router.route('/auth', methods=['GET', 'POST'])
async def auth(request: Request):
    logging.info("Ruta /auth llamada")
    token = await oauth.github.authorize_access_token(request)
    if token is None or 'access_token' not in token:
        raise HTTPException(status_code=401, detail="Token de acceso no obtenido")
    request.session['user'] = token['access_token']
    redirect_to = request.session.pop('redirect_to', '/')
    return RedirectResponse(url=redirect_to)

@logging_router.get("/logout")
async def logout(request: Request):
    logging.info("Ruta /logout llamada")
    request.session.clear()
    response = RedirectResponse(url='/logout_redirect')
    response.delete_cookie('session')
    return response

@logging_router.get("/logout_redirect", response_class=HTMLResponse)
async def logout_redirect(request: Request):
    logging.info("Ruta /logout_redirect llamada")
    return templates.TemplateResponse("logout_redirect.html", {"request": request})
