import logging
import sys
from drivers.comunicacion_serie import ComunicacionSerie
from drivers.camara_usb import CamaraUSB
from core.gestor_ensayo import GestorEnsayo
from ui.app_principal import AppPrincipal

def configurar_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("banco_caudal.log", encoding='utf-8')
        ]
    )

def main():
    configurar_logging()
    logger = logging.getLogger("main")
    logger.info("Iniciando aplicación de Banco de Caudal...")
    
    # Valores parametrizables
    VID_DEFECTO = "2341" # Arduino vendor ID default (configurable por diseñadores)
    PID_DEFECTO = "0043" # Arduino Uno PID default
    
    # Inyección de dependencias
    driver_serie = ComunicacionSerie(vid_defecto=VID_DEFECTO, pid_defecto=PID_DEFECTO)
    driver_camara = CamaraUSB()
    gestor_ensayo = GestorEnsayo()
    
    try:
        app = AppPrincipal(driver_serie, driver_camara, gestor_ensayo)
        app.mainloop()
    except Exception as e:
        logger.error(f"Error crítico en la aplicación: {e}", exc_info=True)
    finally:
        logger.info("Cerrando aplicación y desconectando hardware...")
        driver_serie.desconectar()
        driver_camara.desconectar()

if __name__ == "__main__":
    main()
