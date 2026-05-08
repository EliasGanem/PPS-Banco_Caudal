import serial
import serial.tools.list_ports
import threading
import logging
from typing import List, Optional, Callable

logger = logging.getLogger(__name__)

# MACROS para terminadores (Modificables desde el código para pruebas)
TERMINADOR_RX = b'\x00' # Terminador que se espera recibir del banco
TERMINADOR_TX = b'\x00' # Terminador que se envía por defecto al banco

class ComunicacionSerie:
    def __init__(self, vid_defecto: str = "2341", pid_defecto: str = "0043"):
        """
        Inicializa el driver de comunicación serie.
        
        Args:
            vid_defecto: Vendor ID por defecto para autodetectar (ej. "2341" para Arduino).
            pid_defecto: Product ID por defecto para autodetectar (ej. "0043" para Arduino Uno).
        """
        self.vid_defecto = vid_defecto
        self.pid_defecto = pid_defecto
        self.puerto_serial: Optional[serial.Serial] = None
        self._conectado = False
        self._lock = threading.Lock()
        self._lock_com = threading.Lock()
        self.terminal_callback: Optional[Callable[[str, bytes], None]] = None

    def set_terminal_callback(self, callback: Callable[[str, bytes], None]) -> None:
        """Establece la función a llamar cuando hay datos de TX o RX para la terminal."""
        self.terminal_callback = callback

    def listar_puertos(self) -> List[str]:
        """Devuelve una lista con los nombres de los puertos COM disponibles."""
        puertos = serial.tools.list_ports.comports()
        return [p.device for p in puertos]

    def autodetectar_puerto(self) -> Optional[str]:
        """
        Busca entre los puertos disponibles alguno que coincida con el VID y PID.
        Devuelve el nombre del puerto (ej: "COM3") o None si no encuentra.
        """
        puertos = serial.tools.list_ports.comports()
        for p in puertos:
            if p.vid is not None and p.pid is not None:
                vid_str = f"{p.vid:04X}"
                pid_str = f"{p.pid:04X}"
                if vid_str.lower() == self.vid_defecto.lower() and pid_str.lower() == self.pid_defecto.lower():
                    return p.device
        return None

    def conectar(self, puerto: str) -> bool:
        """Conecta al puerto especificado con los parámetros requeridos."""
        with self._lock:
            if self.puerto_serial and self.puerto_serial.is_open:
                self.puerto_serial.close()
            
            try:
                self.puerto_serial = serial.Serial(
                    port=puerto,
                    baudrate=115200,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=3.0  # Aumentado para dar tiempo al banco de procesar y estabilizar balanza
                )
                self._conectado = True
                logger.info(f"Conectado a puerto serie {puerto}")
                return True
            except serial.SerialException as e:
                logger.error(f"Error al conectar al puerto serie {puerto}: {e}")
                self._conectado = False
                return False

    def desconectar(self) -> None:
        """Cierra el puerto serie."""
        with self._lock:
            if self.puerto_serial and self.puerto_serial.is_open:
                self.puerto_serial.close()
            self._conectado = False
            logger.info("Puerto serie desconectado.")

    def esta_conectado(self) -> bool:
        """Indica si el puerto está actualmente abierto."""
        with self._lock:
            return self._conectado

    def enviar_comando_async(self, comando: str, espera_respuesta: bool = True, callback: Optional[Callable[[str, str], None]] = None, terminador_tx: bytes = TERMINADOR_TX) -> None:
        """
        Envía un comando al banco de caudal en un hilo separado.
        
        Args:
            comando: El string a enviar.
            espera_respuesta: Indica si el comando espera datos devuelta.
            callback: Función que se llama cuando termina (con el comando y la respuesta como parámetros).
            terminador_tx: Terminador a anexar al final del comando.
        """
        def tarea():
            with self._lock:
                if not self._conectado or not self.puerto_serial:
                    logger.warning(f"No se puede enviar comando '{comando}', puerto desconectado.")
                    if callback: 
                        callback(comando, "")
                    return
                puerto = self.puerto_serial
                
            with self._lock_com:
                try:
                    # Limpiar el buffer de entrada para no leer basura o respuestas viejas
                    puerto.reset_input_buffer()
                    puerto.reset_output_buffer()

                    # Enviar comando con el terminador
                    trama = comando.encode('ascii') + terminador_tx
                    puerto.write(trama)
                    puerto.flush()
                    
                    if self.terminal_callback:
                        self.terminal_callback("TX", trama)
                    
                    respuesta_str = ""
                    if espera_respuesta:
                        # Leer hasta encontrar el terminador esperado o timeout
                        respuesta = b""
                        while True:
                            char = puerto.read(1)
                            if not char:
                                break
                            respuesta += char
                            if respuesta.endswith(TERMINADOR_RX):
                                break
                                
                        if self.terminal_callback and respuesta:
                            self.terminal_callback("RX", respuesta)
                            
                        # Quitar el terminador si está al final para procesarlo
                        if len(TERMINADOR_RX) > 0 and respuesta.endswith(TERMINADOR_RX):
                            respuesta = respuesta[:-len(TERMINADOR_RX)]
                            
                        respuesta_str = respuesta.decode('ascii', errors='ignore')
                    
                    if callback:
                        callback(comando, respuesta_str)
                except Exception as e:
                    logger.error(f"Error comunicando por serie: {e}")
                    self.desconectar()
                    if callback: 
                        callback(comando, "")
        
        hilo = threading.Thread(target=tarea, daemon=True)
        hilo.start()
