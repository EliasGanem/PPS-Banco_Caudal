import csv
from datetime import datetime
from pathlib import Path
import logging
import json
import shutil
from typing import Dict, Any

logger = logging.getLogger(__name__)

class GestorEnsayo:
    """Maneja el estado del ensayo y el almacenamiento de datos en disco."""
    def __init__(self):
        self.config_path = Path(__file__).parent.parent / "config.json"
        self.carpeta_base = self._cargar_ruta_base()
        self.carpeta_actual: Path | None = None
        self.datos_ensayo: Dict[str, Any] = {}
        self.imagenes_tomadas = 0
        
    def _cargar_ruta_base(self) -> Path:
        default_path = Path(__file__).parent.parent.absolute() / "ensayos_banco_caudal"
        try:
            if self.config_path.exists():
                with open(self.config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    ruta = config.get("carpeta_base", "")
                    if ruta:
                        return Path(ruta)
        except Exception as e:
            logger.error(f"Error cargando config: {e}")
        return default_path
        
    def cambiar_ruta_base(self, nueva_ruta: str) -> None:
        self.carpeta_base = Path(nueva_ruta)
        self.carpeta_base.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump({"carpeta_base": str(self.carpeta_base)}, f)
            logger.info(f"Ruta base cambiada a: {self.carpeta_base}")
        except Exception as e:
            logger.error(f"Error guardando config: {e}")
        
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

    def eliminar_carpeta_actual(self) -> None:
        """Elimina el directorio del ensayo actual con todo su contenido."""
        if self.carpeta_actual and self.carpeta_actual.exists():
            try:
                shutil.rmtree(self.carpeta_actual)
                logger.info(f"Directorio de ensayo eliminado: {self.carpeta_actual}")
            except Exception as e:
                logger.error(f"Error al eliminar directorio de ensayo {self.carpeta_actual}: {e}")
            finally:
                self.carpeta_actual = None
