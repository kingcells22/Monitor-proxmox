# main.py

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from proxmoxer import ProxmoxAPI

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Configura tu conexión a Proxmox
proxmox = ProxmoxAPI(
    "10.0.0.20",  # Cambia por tu IP/nombre de host
    user="root@pam",
    password="TU_PASSWORD",
    verify_ssl=False
)

@app.get("/vms", response_class=HTMLResponse)
async def list_vms(request: Request):
    node = "csiceprod"  # Cambia por tu nodo
    vms = proxmox.nodes(node).qemu.get()
    vm_list = []
    for vm in vms:
        vm_list.append({
            "vmid": vm["vmid"],
            "name": vm.get("name", ""),
            "status": vm.get("status", "")
        })
    return templates.TemplateResponse("vms.html", {"request": request, "vms": vm_list})

# templates/vms.html (Jinja2)
"""
<!DOCTYPE html>
<html>
<head>
    <title>Lista de VMs</title>
</head>
<body>
    <h1>Lista de VMs</h1>
    <table border="1">
        <tr>
            <th>VMID</th>
            <th>Nombre</th>
            <th>Status</th>
        </tr>
        {% for vm in vms %}
        <tr>
            <td>{{ vm.vmid }}</td>
            <td>{{ vm.name }}</td>
            <td>{{ vm.status }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""
