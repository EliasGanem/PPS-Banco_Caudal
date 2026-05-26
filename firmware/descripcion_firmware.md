# Descripción General del Firmware

El firmware está diseñado para un microcontrolador ESP32 utilizando FreeRTOS como sistema operativo en tiempo real. Se programa utilizando PlatformIO con el framework ESP-IDF dentro del entorno de VSCode. Su objetivo principal es controlar válvulas mediante salidas digitales y mantener comunicación concurrente con:
- Una **PC** (vía USB) para recibir comandos y enviar mediciones.
- Una **balanza** (vía RS-232).
- Un **reloj** (vía RS-232).

## Arquitectura y Tareas

Para gestionar múltiples eventos sin bloquear la ejecución, el firmware divide sus responsabilidades en tareas independientes administradas por el RTOS:

1. **Recepción USB (`Tarea_USB`)**: Se dedica exclusivamente a leer comandos enviados por la PC. Acumula caracteres en un buffer hasta detectar el terminador configurado por la macro `CMD_TERMINATOR_USB`, valida el comando y lo empuja a una cola de mensajes (Queue).
2. **Control Central (`Tarea_Control`)**: Lee los mensajes de la cola de comandos y toma decisiones. Gestiona los cambios de estado de las válvulas (cambio de modos) y delega la ejecución de mediciones.
3. **Lectura RS-232 (`Tarea_UART`)**: Balanza y reloj comparten el mismo bus físico a través de un multiplexor de hardware. El acceso a los instrumentos está protegido mediante un Mutex (exclusión mutua), garantizando que nadie mueva los pines de selección mientras una lectura está en proceso. Antes de cada lectura, el buffer del UART se limpia para descartar datos obsoletos y luego se busca activamente el inicio de una trama válida.

## Hardware y Asignación de Pines

El firmware abstrae el hardware definiendo macros de lógica activa que permiten adaptar fácilmente el código a lógicas positivas o negativas de los periféricos. Las asignaciones de pines actuales son:

- **GPIO 35 (`hab_mux`)**: Habilita el multiplexor RS-232. Se mantiene activo durante las lecturas.
- **GPIO 34 (`selector_uart`)**: Selecciona el instrumento a leer: `0` conecta la balanza, `1` conecta el reloj.
- **GPIO 26 (`valvula_recirculacion`)**: Activa la válvula del tanque de recirculación.
- **GPIO 27 (`selector_tanque`)**: Selector lógico de tanque: `0` para tanque de recirculación, `1` para tanque de pesada.
- **GPIO 14 (`valvula_pesada`)**: Activa la válvula del tanque de pesada.
- **UART0**: Se utiliza para la comunicación USB a la PC usando el conversor UART-USB de la placa base (Pines 1 y 3).
- **UART2**: Se utiliza para la comunicación con los instrumentos (Pines 16 y 17).

## Modos de Operación y Comandos

Al energizarse, el sistema arranca en un **Estado de Arranque Seguro (Modo Recirculación)**: se fuerza el apagado de la `valvula_pesada`, el `selector_tanque` se ubica en el de recirculación, y se habilita la `valvula_recirculacion`.

El flujo normal de ejecución depende de los comandos string (terminados por el carácter definido en la macro `CMD_TERMINATOR_USB`, por defecto nulo `\0`) que la PC envía a través del USB:

- **`INICIAR ENSAYO`**: Se mantiene la `valvula_recirculacion` activada y el `selector_tanque` cambia a tanque de pesada. A partir de este momento, la PC puede pedir iterativamente lecturas.
- **`INICIAR RETORNO`**: Se habilita la `valvula_pesada` primero y, tras una breve espera para garantizar su apertura, se cierra la `valvula_recirculacion`, pasando el `selector_tanque` al tanque de recirculación (retorno).
- **`FINALIZAR ENSAYO`**: Se fuerza de forma **inmediata** la vuelta al estado seguro (Modo Recirculación). Además, se realiza una última lectura segura del reloj y se envía ese valor a la PC.
- **`FINALIZAR RETORNO`**: Se regresa de forma inmediata al estado seguro (Modo Recirculación).
- **`MEDICION BALANZA`**: Dispara la lectura de la balanza y se envía el resultado por USB a la PC.
- **`MEDICION RELOJ`**: Dispara la lectura del tiempo en el reloj y se envía el resultado por USB.
- **`MEDICION COMPLETA`**: Dispara secuencialmente la lectura de la balanza y del reloj, y transmite ambos valores.

*Nota: Los comandos críticos que cambian el estado del ensayo (`INICIAR_...` y `FINALIZAR_...`) tienen prioridad; al recibirse, limpian la cola de mensajes descartando cualquier medición pendiente, para garantizar que el cambio de válvulas se aplique sin demoras.*

## Protocolos de Instrumentos y Envío de Datos

### Comunicación con la Balanza
La balanza envía continuamente datos por RS-232 (1200 baudios, 8N1) en bloques de 8 caracteres con formato `"SPPPPPPC"`, donde `S` es el status, `P` son los dígitos de peso en ASCII, y `C` es el terminador configurado en la macro `CMD_TERMINATOR_UART` (por defecto Carriage Return `\r`). 
El firmware se encarga de sincronizarse con esta trama durante una ventana de tiempo, aislar el peso y descartar los saltos de línea para reformatear el dato.

### Comunicación con el Reloj
Para leer el tiempo de ensayo actual, el firmware selecciona el reloj con el multiplexor y le transmite un byte de comando parametrizado en la macro `COMANDO_RELOJ` (cuyo valor por defecto es `100`). El reloj responde emitiendo 2 bytes en formato *little endian*, que conforman un entero sin signo de 16 bits que representa los milisegundos transcurridos. (Ej. `0xab 0x11` corresponde a `4523` milisegundos).

### Envío hacia la PC
Todo dato devuelto a la PC a través de USB posee un formato de string fijo e incluye siempre al final el terminador correspondiente de la macro `CMD_TERMINATOR_USB`:
- **Respuesta de la Balanza**: Se envían los caracteres del peso insertando el punto decimal de forma explícita. El string posee el formato `"PPPP.PP"`.
- **Respuesta del Reloj**: Se transforman los milisegundos a formato de segundos y milisegundos, rellenando con ceros si hiciera falta. El string enviado tiene el formato `"XXXX.YYY"` (ej. `"0004.523"`).
