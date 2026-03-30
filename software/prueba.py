import usb.core
import usb.util
import sys

# --- CONFIGURACIÓN ---
ID_VENDOR = 0x04D8  
ID_PRODUCT = 0x0010

# Buscar el dispositivo
dev = usb.core.find(idVendor=ID_VENDOR, idProduct=ID_PRODUCT)

if dev is None:
    print("Dispositivo no encontrado. ¿Está conectado?")
    sys.exit(1)

# --- INICIALIZACIÓN CRÍTICA ---

# 1. Resetear el dispositivo (limpia estados de transferencias previas)
dev.reset()

# 2. Liberar driver del kernel (Solo necesario en Linux, en Windows se ignora)
try:
    if dev.is_kernel_driver_active(0):
        dev.detach_kernel_driver(0)
except (NotImplementedError, usb.core.USBError):
    pass # Windows no suele implementar esto o no es necesario con WinUSB

# --- REEMPLAZO DE LA INICIALIZACIÓN ---

# 1. Resetear el bus
dev.reset()

# 2. Forzar la configuración pasándole el valor 1 (índice de configuración)
# A veces pasarlo explícitamente ayuda a que el driver no lo ignore
dev.set_configuration(1)

# 3. TRUCO: Reclamar la interfaz antes de intentar cualquier set_interface
usb.util.claim_interface(dev, 0)

# 4. En lugar de set_interface_altsetting, intentamos enviar un comando de control
# que simule el comportamiento del lab
try:
    # Esto es lo que hace set_interface_altsetting a nivel de protocolo (bmRequestType=0x01, bRequest=0x0b)
    dev.ctrl_transfer(0x01, 0x0B, 0, 0, None)
    print("Comando SET_INTERFACE forzado manualmente")
except Exception as e:
    print(f"Error al forzar: {e}")

# --- RESTO DEL CÓDIGO (Endpoints y Funciones) ---
endpoint_out = 0x01
endpoint_in = 0x81

# ... (tu función probar_comunicacion y el bloque __main__ se mantienen igual)

def probar_comunicacion(modo, param):
    try:
        # 1. Enviar datos (2 bytes: Modo y Param)
        # Enviamos Modo 15 (Todo) y Param 0 (Sin activar salidas)
        data_to_send = [modo, param]
        dev.write(endpoint_out, data_to_send)
        print(f"Enviado: Modo={modo}, Param={param}")

        # 2. Leer respuesta (9 bytes)
        # Ponemos un timeout de 1000ms
        respuesta = dev.read(endpoint_in, 9, timeout=5000)
        
        print(f"Respuesta del PIC (9 bytes): {list(respuesta)}")
        
        # Ejemplo de interpretación según documentación:
        temp = respuesta[2]
        nivel = respuesta[5]
        print(f"-> Temperatura: {temp}")
        print(f"-> Nivel: {nivel}")

    except usb.core.USBError as e:
        print(f"Error de comunicación: {e}")

if __name__ == "__main__":
    # Probar Modo 15 (Leer todo) y Param 4 (Activar Vaciado/Recirculado)
    probar_comunicacion(3, 0)