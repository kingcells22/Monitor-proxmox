import os
import logging
import time
from typing import Any, Dict, List, cast, Optional
from fastapi import FastAPI, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from proxmoxer import ProxmoxAPI
from auth import get_current_user, login_get, login_post, SESSION_COOKIE

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("proxmox-monitor")

# --- CONFIGURACIÓN DE SERVIDORES PROXMOX ---
PROXMOX_SERVERS = [
    {
        "name": "csiceprod",
        "host": "10.0.0.20",
        "port": 8006,
        "user": "root@pam",
        "password": "FloriAng3r4*0.85",
        "verify_ssl": False
    },
    {
        "name": "dmz",
        "host": "171.0.10.5",
        "port": 8006,
        "user": "root@pam",
        "password": "FiiVzla2024.",
        "verify_ssl": False
    },
    {
        "name": "master",
        "host": "172.16.0.2",
        "port": 8006,
        "user": "root@pam",
        "password": "FiiVzla2024.",
        "verify_ssl": False
    },
    {
        "name": "proxmoxvaes",
        "host": "10.0.0.16",
        "port": 8006,
        "user": "root@pam",
        "password": "FiiVzla2024.",
        "verify_ssl": False
    },
    {
        "name": "proxmoxar",
        "host": "10.0.0.12",
        "port": 8006,
        "user": "root@pam",
        "password": "FiiVzla2024.",
        "verify_ssl": False
    },
    {
        "name": "proxmoxpub",
        "host": "10.0.0.14",
        "port": 8006,
        "user": "root@pam",
        "password": "FiiVzla2024.",
        "verify_ssl": False
    },
    {
        "name": "proxmoxvacon",
        "host": "10.0.0.18",
        "port": 8006,
        "user": "root@pam",
        "password": "FiiVzla2024.",
        "verify_ssl": False
    },
    {
        "name": "proxmoxva",
        "host": "10.0.0.10",
        "port": 8006,
        "user": "root@pam",
        "password": "FiiVzla2024.",
        "verify_ssl": False
    },
    {
        "name": "csise",
        "host": "10.0.0.5",
        "port": 8006,
        "user": "root@pam",
        "password": "FloriAng3r4*0.85",
        "verify_ssl": False
    }
]

def get_server_config(server_name: str) -> Optional[Dict[str, Any]]:
    for server in PROXMOX_SERVERS:
        if server["name"] == server_name:
            return server
    return None

def get_proxmox(server_name: str) -> ProxmoxAPI:
    """
    Devuelve una instancia de ProxmoxAPI para el servidor especificado.
    """
    config = get_server_config(server_name)
    if not config:
        raise HTTPException(status_code=404, detail=f"Servidor '{server_name}' no encontrado")
    try:
        logger.info(f"Conectando a Proxmox: {config['host']}:{config['port']} ({server_name})")
        proxmox = ProxmoxAPI(
            config["host"],
            user=config["user"],
            password=config["password"],
            verify_ssl=config["verify_ssl"],
            port=config["port"]
        )
        return proxmox
    except Exception as e:
        logger.error(f"Error conectando a Proxmox {server_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Error conectando a Proxmox {server_name}: {e}")

app = FastAPI(title="Monitor Proxmox Multi-Servidor")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

def get_all_nodes(proxmox: ProxmoxAPI) -> List[Dict[str, Any]]:
    """Obtiene todos los nodos del clúster."""
    try:
        nodes = cast(List[Dict[str, Any]], proxmox.nodes.get())  # type: ignore
        if not isinstance(nodes, list):
            logger.warning("La respuesta de proxmox.nodes.get() no es una lista, retornando lista vacía.")
            nodes = []
        return nodes
    except Exception as e:
        logger.error(f"Error obteniendo nodos: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo nodos: {e}")

def get_all_vms(proxmox: ProxmoxAPI) -> List[Dict[str, Any]]:
    """Obtiene todas las VMs de todos los nodos."""
    vms_list: List[Dict[str, Any]] = []
    nodes = get_all_nodes(proxmox)
    for node in nodes:
        node_name = node.get("node")
        try:
            vms = cast(List[Dict[str, Any]], proxmox.nodes(node_name).qemu.get())  # type: ignore
            if not isinstance(vms, list):
                logger.warning(f"La respuesta de proxmox.nodes({node_name}).qemu.get() no es una lista, se ignora.")
                vms = []
            for vm in vms:
                vms_list.append({
                    "node": node_name,
                    "vmid": vm.get("vmid"),
                    "name": vm.get("name"),
                    "status": vm.get("status"),
                    "cpu": vm.get("cpu", 0),
                    "maxmem": vm.get("maxmem", 0),
                    "mem": vm.get("mem", 0),
                })
        except Exception as node_error:
            logger.warning(f"Error obteniendo VMs del nodo {node_name}: {node_error}")
    return vms_list

@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return await login_get(request, templates)

@app.post("/login", response_class=HTMLResponse)
async def login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    return await login_post(request, templates, username, password)

@app.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(SESSION_COOKIE)
    return response

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/servers", status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/servers", response_class=HTMLResponse)
async def servers_list(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    # Solo mostramos la lista de servidores
    servers = [{"name": s["name"]} for s in PROXMOX_SERVERS]
    return templates.TemplateResponse("servers.html", {
        "request": request,
        "servers": servers,
        "user": user
    })

@app.get("/servers/{server_name}", response_class=HTMLResponse)
async def server_vms(request: Request, server_name: str):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    config = get_server_config(server_name)
    if not config:
        return templates.TemplateResponse("servers.html", {
            "request": request,
            "servers": [{"name": s["name"]} for s in PROXMOX_SERVERS],
            "user": user,
            "error": f"Servidor '{server_name}' no encontrado"
        })
    try:
        proxmox = get_proxmox(server_name)
        nodes = get_all_nodes(proxmox)
        vms_list = get_all_vms(proxmox)
        return templates.TemplateResponse("server_vms.html", {
            "request": request,
            "server": config,
            "nodes": nodes,
            "vms": vms_list,
            "user": user
        })
    except Exception as e:
        logger.error(f"Error generando vista de VMs para {server_name}: {e}")
        return templates.TemplateResponse("server_vms.html", {
            "request": request,
            "server": config,
            "nodes": [],
            "vms": [],
            "error": f"Error generando vista de VMs: {e}",
            "user": user
        })

# El resto de endpoints (status, health, etc.) pueden adaptarse para multi-servidor si lo necesitas.
# Ejecuta SIEMPRE con: uvicorn monitor:app --reload