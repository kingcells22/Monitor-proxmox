from monitor import send_telegram_alert

if __name__ == "__main__":
    print("Enviando pruebas a Telegram...")
    
    # 1. Prueba basica
    send_telegram_alert("[PRUEBA]: El monitor Dockerizado esta UP y funcionando correctamente.")
    
    # 2. Simulando una caida de red
    msg_falla = "[ALERTA DE CONEXION]\nNo se puede contactar al servidor `pruebaotic`.\n*Causa*: Servidor inalcanzable (Falla de red, sin internet o equipo apagado)."
    send_telegram_alert(msg_falla)
    
    # 3. Simulando la recuperacion de red
    msg_recovery = "[OK] *Conexion Restablecida*\nEl servidor `pruebaotic` vuelve a estar en linea y respondiendo."
    send_telegram_alert(msg_recovery)
    
    print("Pruebas enviadas. Revisa tu Telegram.")