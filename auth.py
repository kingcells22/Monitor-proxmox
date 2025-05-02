import hashlib
from fastapi import Request, Form, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

# Usuarios pre-registrados: username -> password (en texto plano)
USERS = {
    "Bladeccs": "Solera24.",
    "FDuran": "fd2025",
    "MPena": "mp2025",
    "JSalas": "js2025",
    "SStella": "ss2025"
}

SESSION_COOKIE = "session_user"

def verify_user(username: str, password: str) -> bool:
    """Verifica si el usuario y contraseña son válidos."""
    if username in USERS and USERS[username] == password:
        return True
    return False

def get_current_user(request: Request):
    """Obtiene el usuario actual desde la cookie de sesión."""
    return request.cookies.get(SESSION_COOKIE)

def require_login(request: Request):
    """Lanza una redirección si el usuario no está autenticado."""
    user = get_current_user(request)
    if not user or user not in USERS:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    return user

async def login_get(request: Request, templates: Jinja2Templates):
    """Renderiza el formulario de login."""
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

async def login_post(request: Request, templates: Jinja2Templates, username: str = Form(...), password: str = Form(...)):
    """Procesa el formulario de login."""
    if verify_user(username, password):
        response = RedirectResponse(url="/servers", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key=SESSION_COOKIE, value=username, httponly=True)
        return response
    else:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Usuario o contraseña incorrectos"})