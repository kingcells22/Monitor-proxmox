import time
from apscheduler.schedulers.background import BackgroundScheduler
from monitor import PROXMOX_SERVERS, get_proxmox, get_all_nodes, get_all_vms
from utils.telegram_alerts import send_telegram_alert

# Guarda el estado anterior para detectar cambios
previous_status = {}

def daily_report():
    """
    Envía un reporte diario con el estado de todos los nodos y VMs de todos los servidores.
    """
    report = "📝 *Reporte Diario Proxmox*\n"
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
            report += f"⚠️ Error obteniendo datos de {server['name']}: {e}\n"
    send_telegram_alert(report)

def monitor_events():
    """
    Monitorea cambios de estado en nodos y VMs y envía alertas inmediatas.
    """
    global previous_status
    for server in PROXMOX_SERVERS:
        try:
            proxmox = get_proxmox(server["name"])
            nodes = get_all_nodes(proxmox)
            vms = get_all_vms(proxmox)
            # Chequea nodos
            for node in nodes:
                node_id = f"{server['name']}-{node['node']}"
                status = node.get("status")
                prev = previous_status.get(node_id)
                if prev and prev != status:
                    msg = f"🚨 *ALERTA*: Nodo `{node['node']}` en `{server['name']}` cambió de estado: `{prev}` → `{status}`"
                    send_telegram_alert(msg)
                previous_status[node_id] = status
            # Chequea VMs
            for vm in vms:
                vm_id = f"{server['name']}-{vm['node']}-{vm['vmid']}"
                status = vm.get("status")
                prev = previous_status.get(vm_id)
                if prev and prev != status:
                    msg = f"🚨 *ALERTA*: VM `{vm['name']}` (ID: {vm['vmid']}) en `{server['name']}` cambió de estado: `{prev}` → `{status}`"
                    send_telegram_alert(msg)
                previous_status[vm_id] = status
        except Exception as e:
            send_telegram_alert(f"⚠️ Error monitoreando {server['name']}: {e}")

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(daily_report, "cron", hour=0, minute=0)  # Todos los días a las 12 am
    scheduler.add_job(monitor_events, "interval", minutes=2)   # Cada 2 minutos
    scheduler.start()

if __name__ == "__main__":
    print("Iniciando scheduler de alertas Proxmox...")
    start_scheduler()
    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler detenido.")