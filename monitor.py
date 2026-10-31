import os
import logging
import time
import requests
from typing import Any, Dict, List, cast, Optional
from fastapi import FastAPI, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from proxmoxer import ProxmoxAPI
from apscheduler.schedulers.background import BackgroundScheduler
from auth import get_current_user, login_get, login_post, SESSION_COOKIE
from contextlib import asynccontextmanager

# Configuracion de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("proxmox-monitor")

# --- CONFIGURACION DE TELEGRAM ---
TELEGRAM_BOT_TOKEN = "7930279041:AAFYGcAOmWT6fZZnmdNqKENHgMFKGlCCHow"
TELEGRAM_CHAT_ID = str(1292808439)

# --- CONFIGURACION DE SERVIDORES PROXMOX ---
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
        "name": "aliados",
        "host": "171.0.0.6",
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
        "name": "pruebaotic",
        "host": "172.31.45.91",
        "port": 8006,
        "user": "root@pam",
        "password": "123456789",
        "verify_ssl": False
    },
    {
        "name": "gestion",
        "host": "172.31.100.31",
        "port": 8006,
        "user": "root@pam",
        "password": "FiiVzla2024.",
        "verify_ssl": False
    },
]

def get_server_config(server_name: str) -> Optional[Dict[str, Any]]:
    for server in PROXMOX_SERVERS:
        if server["name"] == server_name:
            return server
    return None

def get_proxmox(server_name: str) -> ProxmoxAPI:
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
            port=config["port"],
            timeout=15
        )
        return proxmox
    except Exception as e:
        logger.error(f"Error conectando a Proxmox {server_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Error conectando a Proxmox {server_name}: {e}")

# --- Scheduler de alertas ---
previous_status = {}
last_telegram_update_id = None  # <--- ESTA ES LA LÍNEA QUE TE FALTA AÑADIR

def send_telegram_alert(message: str):
    logger.info("ALERTA TELEGRAM: Preparando envio...")
    token = TELEGRAM_BOT_TOKEN
    chat_id = TELEGRAM_CHAT_ID
    if not token or not chat_id:
        logger.warning("Token o chat_id de Telegram no configurados correctamente. Mensaje no enviado.")
        return
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    MAX_LENGTH = 4000
    mensajes_a_enviar = []

    if len(message) <= MAX_LENGTH:
        mensajes_a_enviar.append(message)
    else:
        lineas = message.split('\n')
        mensaje_actual = ""
        for linea in lineas:
            if len(mensaje_actual) + len(linea) + 1 > MAX_LENGTH:
                mensajes_a_enviar.append(mensaje_actual)
                mensaje_actual = linea + "\n"
            else:
                mensaje_actual += linea + "\n"
        if mensaje_actual:
            mensajes_a_enviar.append(mensaje_actual)

    for i, texto in enumerate(mensajes_a_enviar):
        payload = {
            "chat_id": chat_id,
            "text": texto,
            "parse_mode": "Markdown"
        }
        try:
            resp = requests.post(url, data=payload, timeout=10)
            resp.raise_for_status()
            logger.info(f"Mensaje (Parte {i+1}/{len(mensajes_a_enviar)}) enviado a Telegram exitosamente.")
            if len(mensajes_a_enviar) > 1:
                time.sleep(1) 
        except Exception as e:
            logger.error(f"Error enviando mensaje a Telegram (Parte {i+1}): {e}")

            # =====================================================================
# --- NUEVA FUNCIONALIDAD: PROCESAR COMANDOS DEL MENÚ DE TELEGRAM ---
# =====================================================================
def poll_telegram_commands():
    """Lee silenciosamente si apretaste algún botón en Telegram"""
    global last_telegram_update_id
    token = TELEGRAM_BOT_TOKEN
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    params = {"timeout": 3}
    if last_telegram_update_id:
        params["offset"] = last_telegram_update_id + 1

    try:
        resp = requests.get(url, params=params, timeout=5)
        if resp.status_code != 200:
            return
            
        for update in resp.json().get("result", []):
            last_telegram_update_id = update["update_id"]
            message = update.get("message", {})
            text = message.get("text", "").strip()
            chat_id = str(message.get("chat", {}).get("id"))

            # Solo responde a tu Chat ID por seguridad
            if chat_id == TELEGRAM_CHAT_ID:
                if text == "/listar":
                    msg = "🖥️ *Nodos Proxmox Integrados:*\n"
                    for s in PROXMOX_SERVERS:
                        msg += f"• `{s['name']}` (Comando: `/status_{s['name']}`)\n"
                    send_telegram_alert(msg)
                    
                elif text.startswith("/status_"):
                    target = text.replace("/status_", "").strip()
                    if not get_server_config(target):
                        send_telegram_alert(f"⚠️ El servidor `{target}` no existe en la configuración.")
                        continue
                    
                    send_telegram_alert(f"⏳ Consultando estado actual de `{target}`...")
                    try:
                        px = get_proxmox(target)
                        nodes = get_all_nodes(px)
                        vms = get_all_vms(px)
                        
                        summary = f"📊 *Reporte instantáneo de {target.upper()}*\n\n*Nodos:*\n"
                        for n in nodes: 
                            summary += f"- `{n['node']}`: {n['status']}\n"
                        
                        running = sum(1 for v in vms if v['status'] == 'running')
                        summary += f"\n*VMs Totales ({len(vms)}):*\n🟢 Encendidas: {running}\n🔴 Apagadas: {len(vms) - running}"
                        send_telegram_alert(summary)
                    except Exception as e:
                        send_telegram_alert(f"❌ Error al consultar `{target}`. Asegúrate de que está encendido y tiene red.")
    except Exception:
        pass # Ignoramos errores de red momentáneos para no hacer spam en los logs

def daily_report():
    report = "[REPORTE] *Reporte Diario Proxmox*\n"
    for server in PROXMOX_SERVERS:
        try:
            proxmox = get_proxmox(server["name"])
            nodes = get_all_nodes(proxmox)
            vms = get_all_vms(proxmox)
            report += f"\nServidor: {server['name']}\n"
            report += f"Nodos: {len(nodes)}\n"
            for node in nodes:
                report += f"  - Nodo: {node['node']} | Estado: {node['status']}\n"
            report += f"VMs: {len(vms)}\n"
            for vm in vms:
                report += f"  - VM: {vm['name']} (ID: {vm['vmid']}) | Estado: {vm['status']}\n"
        except Exception as e:
            report += f"[ERROR] Error obteniendo datos de {server['name']}: {e}\n"
    send_telegram_alert(report)

def monitor_events():
    global previous_status
    for server in PROXMOX_SERVERS:
        conn_key = f"conn_status_{server['name']}"
        
        try:
            proxmox = get_proxmox(server["name"])
            nodes = get_all_nodes(proxmox)
            vms = get_all_vms(proxmox)
            
            # --- LOGICA DE RECUPERACION DE RED ---
            if previous_status.get(conn_key) == "down":
                msg_recovery = f"[OK] *Conexion Restablecida*\nEl servidor `{server['name']}` vuelve a estar en linea y respondiendo."
                send_telegram_alert(msg_recovery)
            
            previous_status[conn_key] = "up"
            # -------------------------------------

            for node in nodes:
                node_id = f"{server['name']}-{node['node']}"
                status = node.get("status")
                prev = previous_status.get(node_id)
                logging.info(f"NODE {node_id}: estado anterior={prev}, estado actual={status}")
                if prev and prev != status:
                    msg = f"[ALERTA]: Nodo `{node['node']}` en `{server['name']}` cambio de estado: `{prev}` -> `{status}`"
                    send_telegram_alert(msg)
                previous_status[node_id] = status
                
            for vm in vms:
                vm_id = f"{server['name']}-{vm['node']}-{vm['vmid']}"
                status = vm.get("status")
                prev = previous_status.get(vm_id)
                logging.info(f"VM {vm_id}: estado anterior={prev}, estado actual={status}")
                if prev and prev != status:
                    msg = f"[ALERTA]: VM `{vm['name']}` (ID: {vm['vmid']}) en `{server['name']}` cambio de estado: `{prev}` -> `{status}`"
                    send_telegram_alert(msg)
                previous_status[vm_id] = status

        except Exception as e:
            error_str = str(e)
            logging.error(f"Error monitoreando {server['name']}: {error_str}")
            
            # --- LOGICA DE MENSAJE AMIGABLE Y ANTI-SPAM ---
            if previous_status.get(conn_key) != "down":
                if "No route to host" in error_str or "Max retries exceeded" in error_str or "timeout" in error_str.lower():
                    friendly_error = "Servidor inalcanzable (Falla de red, sin internet o equipo apagado)."
                elif "401" in error_str or "auth" in error_str.lower():
                    friendly_error = "Error de autenticacion (Credenciales invalidas o ticket expirado)."
                else:
                    friendly_error = "Error interno de conexion."

                msg_falla = f"[ALERTA DE CONEXION]\nNo se puede contactar al servidor `{server['name']}`.\n*Causa*: {friendly_error}"
                send_telegram_alert(msg_falla)
                
                previous_status[conn_key] = "down"
            # ----------------------------------------------

scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        scheduler.add_job(daily_report, "cron", hour=0, minute=0)
        scheduler.add_job(monitor_events, "interval", minutes=2)

        # AQUI AGREGAMOS LA NUEVA TAREA PARA LEER TUS BOTONES DE TELEGRAM:
        scheduler.add_job(poll_telegram_commands, "interval", seconds=3)

        scheduler.start()
        logger.info("Scheduler de alertas iniciado correctamente")
    except Exception as e:
        logger.error(f"Error iniciando el scheduler: {e}")
    yield
    scheduler.shutdown()
    logger.info("Scheduler detenido correctamente")

app = FastAPI(title="Monitor Proxmox Multi-Servidor", lifespan=lifespan)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

def get_all_nodes(proxmox: ProxmoxAPI) -> List[Dict[str, Any]]:
    try:
        nodes = cast(List[Dict[str, Any]], proxmox.nodes.get())  # type: ignore
        if not isinstance(nodes, list):
            logger.warning("La respuesta no es una lista, retornando vacio.")
            nodes = []
        return nodes
    except Exception as e:
        logger.error(f"Error obteniendo nodos: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo nodos: {e}")

def get_all_vms(proxmox: ProxmoxAPI) -> List[Dict[str, Any]]:
    vms_list: List[Dict[str, Any]] = []
    nodes = get_all_nodes(proxmox)
    for node in nodes:
        node_name = node.get("node")
        try:
            vms = cast(List[Dict[str, Any]], proxmox.nodes(node_name).qemu.get())  # type: ignore
            if not isinstance(vms, list):
                logger.warning(f"La respuesta de qemu.get() no es lista, se ignora.")
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
        logger.error(f"Error generando vista para {server_name}: {e}")
        return templates.TemplateResponse("server_vms.html", {
            "request": request,
            "server": config,
            "nodes": [],
            "vms": [],
            "error": f"Error generando vista de VMs: {e}",
            "user": user
        })
