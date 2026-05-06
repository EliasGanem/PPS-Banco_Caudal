import csv
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class GestorEnsayo:
    """Maneja el estado del ensayo y el almacenamiento de datos en disco."""
    def __init__(self):
        # Utiliza pathlib para compatibilidad de rutas multiplataforma
        self.carpeta_base = Path("ensayos_banco_caudal")
        self.carpeta_actual: Path | None = None
        self.datos_ensayo: Dict[str, Any] = {}
        self.imagenes_tomadas = 0
        
    def iniciar_nuevo_ensayo(self) -> Path:
        """Crea el directorio para un nuevo ensayo."""
        ahora = datetime.now()
        fecha_hora_str = ahora.strftime("%Y-%m-%d_%H-%M-%S")
        self.carpeta_actual = self.carpeta_base / fecha_hora_str
        # Crear directorios si no existen
        self.carpeta_actual.mkdir(parents=True, exist_ok=True)
        
        self.datos_ensayo = {
            "fecha y hora [hh:mm:ss - dd/mm/aaaa]": ahora.strftime("%H:%M:%S - %d/%m/%Y")
        }
        self.imagenes_tomadas = 0
        logger.info(f"Directorio de ensayo creado: {self.carpeta_actual}")
        return self.carpeta_actual

    def registrar_dato(self, parametro_con_unidad: str, valor: str) -> None:
        """Guarda un dato para el reporte final."""
        self.datos_ensayo[parametro_con_unidad] = valor

    def guardar_reporte_csv(self) -> str:
        """Genera el archivo mediciones.csv con los datos registrados."""
        if not self.carpeta_actual:
            logger.error("No hay un ensayo activo para guardar reporte.")
            return ""
            
        ruta_csv = self.carpeta_actual / "mediciones.csv"
        try:
            # utf-8-sig permite que Excel abra el archivo directamente con buena codificación
            with open(ruta_csv, mode='w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                for parametro, valor in self.datos_ensayo.items():
                    writer.writerow([parametro, valor])
            logger.info(f"Reporte CSV guardado en {ruta_csv}")
            return str(ruta_csv)
        except Exception as e:
            logger.error(f"Error al guardar CSV: {e}")
            return ""

    def obtener_ruta_siguiente_imagen(self) -> str:
        """Genera la ruta para guardar la siguiente imagen cronológica (img_1 a img_6)."""
        if not self.carpeta_actual:
            return ""
        self.imagenes_tomadas += 1
        ruta_img = self.carpeta_actual / f"img_{self.imagenes_tomadas}.jpg"
        return str(ruta_img)
