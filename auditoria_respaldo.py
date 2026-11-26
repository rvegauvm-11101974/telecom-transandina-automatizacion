"""
Módulo de Auditoría y Respaldo Seguro de Configuraciones (Telecom Transandina)
Propósito: Automatizar la extracción de running-config vía SSH utilizando Netmiko,
protegiendo credenciales con variables de entorno y registrando trazas de error.
"""

import os
import logging
import traceback
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

# Configuración de auditoría con sellos de tiempo
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def respaldar_nodo(host):
    """
    Conecta de forma cifrada vía SSH al nodo indicado, extrae su configuración
    activa y captura trazas detalladas (Tracebacks) ante cualquier fallo.
    """
    # Uso de variables de entorno para evitar hardcoding de credenciales
    usuario = os.getenv("NET_USER")
    clave = os.getenv("NET_PASS")

    if not usuario or not clave:
        logging.error("Variables de entorno NET_USER o NET_PASS no configuradas.")
        return

    dispositivo = {
        "device_type": "cisco_ios",
        "host": host,
        "username": usuario,
        "password": clave,
        "timeout": 10
    }

    try:
        logging.info(f"Conectando vía SSH con {host}...")
        with ConnectHandler(**dispositivo) as conexion:
            config = conexion.send_command("show running-config")
            with open(f"backup_{host}.cfg", "w", encoding="utf-8") as archivo:
                archivo.write(config)
            logging.info(f"Respaldo completado exitosamente para {host}.")

    except (NetmikoTimeoutException, NetmikoAuthenticationException) as error_red:
        logging.error(f"Fallo de conexión o autenticación en {host}: {error_red}")
        # Registro de traza de error (Traceback) para diagnóstico rápido
        logging.debug(traceback.format_exc())

    except Exception as error_inesperado:
        logging.critical(f"Error crítico no controlado en {host}: {error_inesperado}")
        logging.error(traceback.format_exc())

if __name__ == "__main__":
    respaldar_nodo("10.20.30.1")
