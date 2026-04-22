import cv2
import threading
import logging
from typing import List, Optional, Callable

logger = logging.getLogger(__name__)

class CamaraUSB:
    def __init__(self):
        """Inicializa el driver de la cámara USB."""
        self.captura: Optional[cv2.VideoCapture] = None
        self.indice_camara: int = -1
        self._conectada = False
        self._lock = threading.Lock()

    def listar_camaras_disponibles(self) -> List[str]:
        """Devuelve una lista de las cámaras disponibles probando índices."""
        camaras = []
        for i in range(5):
            # En Windows cv2.CAP_DSHOW suele funcionar mejor y evita warnings de Media Foundation
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                camaras.append(f"Cámara {i}")
                cap.release()
        return camaras

    def conectar(self, indice: int) -> bool:
        """Abre la conexión con la cámara en el índice especificado."""
        with self._lock:
            if self.captura is not None:
                self.captura.release()
            
            self.captura = cv2.VideoCapture(indice, cv2.CAP_DSHOW)
            
            if self.captura.isOpened():
                # Solicitar resolución extremadamente alta para forzar a la cámara a su máxima nativa
                self.captura.set(cv2.CAP_PROP_FRAME_WIDTH, 10000)
                self.captura.set(cv2.CAP_PROP_FRAME_HEIGHT, 10000)
                
                self.indice_camara = indice
                self._conectada = True
                logger.info(f"Cámara {indice} conectada exitosamente.")
                return True
            else:
                self._conectada = False
                logger.error(f"No se pudo conectar a la cámara {indice}.")
                return False

    def desconectar(self) -> None:
        """Libera la cámara conectada."""
        with self._lock:
            if self.captura is not None:
                self.captura.release()
                self.captura = None
            self._conectada = False
            self.indice_camara = -1
            logger.info("Cámara desconectada.")

    def esta_conectada(self) -> bool:
        """Devuelve True si la cámara está activa."""
        with self._lock:
            return self._conectada

    def tomar_foto(self, ruta_guardado: str, callback: Optional[Callable[[bool, str], None]] = None) -> None:
        """
        Toma una foto de forma asíncrona y la guarda en la ruta indicada.
        
        Args:
            ruta_guardado: Path completo para guardar la imagen (ej: C:/fotos/img_1.jpg).
            callback: Función que recibe (exito, ruta) cuando finaliza.
        """
        def tarea():
            exito = False
            with self._lock:
                if self._conectada and self.captura is not None:
                    # Se lee un frame un par de veces para descartar posibles frames viejos en el buffer
                    self.captura.read()
                    ret, frame = self.captura.read()
                    if ret:
                        cv2.imwrite(ruta_guardado, frame)
                        exito = True
                        logger.info(f"Foto guardada en {ruta_guardado}")
                    else:
                        logger.error("No se pudo leer el frame de la cámara.")
                else:
                    logger.warning("Intento de tomar foto sin cámara conectada.")
            
            if callback:
                callback(exito, ruta_guardado)

        hilo = threading.Thread(target=tarea, daemon=True)
        hilo.start()
