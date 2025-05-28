# Monitor-Proxmox 🖥️ Monitor

---

## Descripción General

`Monitor-proxmox` es un script simple diseñado para monitorear el estado de tus máquinas virtuales (VMs) y contenedores (CTs) en un entorno Proxmox VE. Proporciona una visión rápida sobre qué VMs/CTs están encendidas y cuáles están apagadas, ayudándote a mantener un control básico de tu infraestructura virtualizada.

Este script es ideal para administradores que necesitan una herramienta ligera para verificar el estado operativo de sus instancias de Proxmox sin necesidad de acceder a la interfaz web completa o usar comandos más complejos.

---

## Características

* **Listado de VMs/CTs:** Muestra un listado claro de todas las VMs y CTs configuradas en tu Proxmox.
* **Estado Operativo:** Indica si cada VM/CT está **encendida** o **apagada**.
* **Salida Sencilla:** Presenta la información en un formato fácil de leer en la terminal.

---

## Requisitos

Para utilizar este script, necesitarás:

* Un servidor **Proxmox VE** en funcionamiento.
* Acceso **SSH** al servidor Proxmox.
* **Bash** (generalmente ya disponible en Proxmox).

---

## Instalación y Uso

Sigue estos pasos para instalar y ejecutar el script en tu servidor Proxmox:

1.  **Conéctate a tu servidor Proxmox vía SSH:**

    ```bash
    ssh root@tu_ip_proxmox
    ```

2.  **Clona el repositorio:**
    Navega al directorio donde quieras guardar el script (por ejemplo, tu directorio `root` o `/opt/scripts`).

    ```bash
    cd ~
    git clone [https://github.com/kingcells22/Monitor-proxmox.git](https://github.com/kingcells22/Monitor-proxmox.git)
    ```

3.  **Navega al directorio del script:**

    ```bash
    cd Monitor-proxmox
    ```

4.  **Haz el script ejecutable:**

    ```bash
    chmod +x monitor_proxmox.sh
    ```

5.  **Ejecuta el script:**

    ```bash
    ./monitor_proxmox.sh
    ```

### Ejemplo de Salida

Cuando ejecutes el script, verás una salida similar a esta:

[+] Mostrando estado de VMs y CTs en Proxmox:

100 (tu_vm_o_ct_1) Estado: ON
101 (tu_vm_o_ct_2) Estado: OFF
102 (tu_vm_o_ct_3) Estado: ON


---

## Cómo Contribuir

¡Las contribuciones son bienvenidas! Si tienes ideas para mejorar este script, puedes:

1.  Hacer un `fork` del repositorio.
2.  Crear una nueva rama (`git checkout -b feature/nueva-funcionalidad`).
3.  Realizar tus cambios y hacer `commit` (`git commit -m 'Añade nueva funcionalidad'`).
4.  Subir tus cambios (`git push origin feature/nueva-funcionalidad`).
5.  Abrir un `Pull Request`.

---

## Licencia

Este proyecto está bajo la licencia [MIT](https://opensource.org/licenses/MIT). Consulta el archivo `LICENSE` para más detalles.
