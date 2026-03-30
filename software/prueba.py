import usb.core
import usb.util
import sys

# --- CONFIGURACIÓN ---
# Reemplazá con los valores que obtuviste de lsusb
ID_VENDOR = 0x04D8  
ID_PRODUCT = 0x0010

# Buscar el dispositivo
dev = usb.core.find(idVendor=ID_VENDOR, idProduct=ID_PRODUCT)

if dev is None:
    print("Dispositivo no encontrado. ¿Está conectado?")
    sys.exit(1)

    # En Windows, a veces es necesario hacer un "detach" si el driver está ocupado
    if dev.is_kernel_driver_active(0):
        dev.detach_kernel_driver(0)

# Configurar el dispositivo
dev.set_configuration()

# 1. Reclamar la interfaz (Interface 0 en tu caso)
usb.util.claim_interface(dev, 0)

# 2. Forzar el SET INTERFACE (esto genera el paquete que falta en tu captura)
dev.set_interface_altsetting(interface = 0, alternate_setting = 0)

# Definir los EndPoints (EP1 en el código del PIC)
# 0x01 es el EP1 OUT (PC -> PIC)
# 0x81 es el EP1 IN (PIC -> PC)
endpoint_out = 0x01
endpoint_in = 0x81

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