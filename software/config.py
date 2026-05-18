# =============================================
#  CONFIGURACIÓN DEL BANCO DE CAUDAL
#  Modificar estos valores según la necesidad
# =============================================

# --- Comunicación Serie (USB) ---
TERMINADOR_RX = b'\x00'     # Terminador que se espera recibir del banco
TERMINADOR_TX = b'\x00'     # Terminador que se envía al banco
TIME_OUT_USB = 0.5           # Timeout de lectura en segundos
BAUDRATE_USB = 115200
VID_DEFECTO = "1A86"         # Vendor ID (WCH/QinHeng - CH340/CH9102)
PID_DEFECTO = "55D4"         # Product ID del adaptador USB-Serie del banco

# --- Ensayo ---
DURACION_ENSAYO_POR_DEFECTO_S = 10.0
PERIODO_MEDICION_BALANZA_RETORNO_MS = 1000
PESO_MINIMO_RETORNO_KG = 5.0
PESO_MAXIMO_TANQUE_KG = 220.0

# --- Seguridad ---
CONTRASENIA_TERMINAL = "1234"
