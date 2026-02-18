# Monitor-Proxmox 🖥️ Monitor

---

## Descripción General

`Monitor-proxmox` es un script simple diseñado para monitorear el estado de tus máquinas virtuales (VMs) y contenedores (CTs) en un entorno Proxmox VE. Proporciona una visión rápida sobre qué VMs/CTs están encendidas y cuáles están apagadas, ayudándote a mantener un control básico de tu infraestructura virtualizada.

A diferencia de un script simple, este monitor se ejecuta como un servicio continuo que:
1.  Provee una **Interfaz Web** para visualizar el estado de múltiples nodos.
2.  Envía **Alertas a Telegram** en tiempo real cuando una VM o Nodo cambia de estado (se apaga/enciende) o si hay errores de conexión.

---

## Características

* **Soporte Multi-Servidor:** Monitorea múltiples instancias de Proxmox desde un solo lugar.
* **Interfaz Web (FastAPI):** Panel accesible vía navegador para ver el estado de todos tus recursos.
* **Alertas de Telegram:** Notificaciones automáticas de caídas o cambios de estado.
* **Dockerizado:** Fácil de desplegar y aislar mediante contenedores Docker.
* **Auto-reinicio:** Configurado para arrancar automáticamente si el servidor se reinicia.
---

## Requisitos

* Servidor Linux (Debian/Ubuntu/CentOS).
* **Docker** instalado.
* Git.

---

## Instalación y Despliegue con Docker

Sigue estos pasos para instalar y ejecutar el script en tu servidor Proxmox:

1.  **Conéctate a tu servidor Proxmox vía SSH:**

    ```bash
    ssh root@tu_ip_proxmox
    ```

2.  **Clona el repositorio:**
    Descarga el código en tu servidor:
    Navega al directorio donde quieras guardar el script (por ejemplo, tu directorio `root` o `/opt/scripts`).

    ```bash
cd ~
git clone [https://github.com/kingcells22/Monitor-proxmox.git](https://github.com/kingcells22/Monitor-proxmox.git)
    ```
cd Monitor-proxmox

3.  **Navega al directorio del script:**

    ```bash
    cd Monitor-proxmox
    ```

4.  Configuración
    Edita el archivo monitor.py para agregar tus servidores Proxmox y credenciales de Telegram.
    ```bash
    nano monitor.py
    ```
    NOTA: Asegúrate de configurar la lista PROXMOX_SERVERS, el TELEGRAM_BOT_TOKEN y el TELEGRAM_CHAT_ID.
5.  **Construir la Imagen (Build)**
    Crea la imagen de Docker con tus configuraciones actuales:

    ```bash
    docker build -t monitor-proxmox .
    ```

6.  **Ejecutar el Contenedor (Run)**
    Levanta el contenedor en segundo plano (puerto 8000):

     ```bash
    docker run -d \
  --name monitor-proxmox \
  --restart unless-stopped \
  -p 8000:8000 \
  monitor-proxmox
    ```

**Gestión del Contenedor**
Aquí están los comandos esenciales para administrar el monitor:

Ver si el contenedor está corriendo
Usa este comando para ver el estado (STATUS) y el ID del contenedor:

 ```bash
    docker ps
 ```

(Nota: No uses docker compose ps, ya que este despliegue es standalone).
    ---
**Ver los logs (errores o actividad)**
Si necesitas depurar o ver qué está haciendo el monitor:
    docker logs -f monitor-proxmox
**(Presiona Ctrl + C para salir de los logs).**

**Detener y Eliminar el monitor**
Si necesitas bajar el servicio para actualizar el código o configuración:

1. Detener:
    ```bash
    docker stop monitor-proxmox
    ```
------

3. Eliminar:
    ```bash
    docker rm monitor-proxmox
    ```
------    

5. Acceso al Panel Web
Una vez que el contenedor esté corriendo, abre tu navegador y accede a:
http://TU_IP_DEL_SERVIDOR:8000

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
