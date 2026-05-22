# Descripción del Software

## Índice
1. [Descripción General](#1-descripción-general)
2. [Descripción de la Interfaz de Usuario](#2-descripción-de-la-interfaz-de-usuario)
3. [Descripción del Funcionamiento](#3-descripción-del-funcionamiento)

---

## 1. Descripción General

Este software controla un banco de caudal a través de comunicación USB COM para realizar ensayos de calibración de caudalímetros. Permite enviar comandos y recibir datos de medición (peso y tiempo) desde el hardware del banco, y capturar imágenes sincronizadas con el ensayo mediante una cámara USB.

### Principales funcionalidades
- **Ensayo de caudal:** inicia y detiene un ensayo con duración configurable. Registra el peso inicial, el peso final y el tiempo de ensayo para calcular los caudales másico y volumétrico.
- **Captura de imágenes:** toma 6 fotografías distribuidas a lo largo del ensayo y las muestra en la interfaz.
- **Retorno de fluido:** controla el retorno del fluido al tanque, monitoreando el peso hasta que alcanza un mínimo configurable.
- **Almacenamiento de datos:** guarda las imágenes y un archivo CSV con los resultados de cada ensayo en una carpeta organizada por fecha y hora.
- **Terminal serie:** terminal integrada con acceso protegido por contraseña para comunicación directa con el banco de caudal.
- **Modos de operación (Manual/Automático):** cada campo de medición (peso inicial, peso final y tiempo) puede obtenerse del banco de caudal (modo automático) o ingresarse manualmente por el usuario.

### Tecnologías utilizadas
| Componente | Tecnología |
|---|---|
| Interfaz gráfica | CustomTkinter |
| Cámara USB | OpenCV (cv2) |
| Comunicación serie | pyserial |
| Hilos secundarios | threading (stdlib) |

> **Nota sobre concurrencia:** la comunicación USB COM y la captura de fotos se ejecutan en hilos (threads) secundarios para no bloquear la interfaz de usuario. Los hilos secundarios nunca actualizan directamente la UI; en su lugar, los resultados se envían al hilo principal mediante callbacks seguros (`after()`).

### Parámetros configurables
Los siguientes parámetros son configurables desde el archivo `config.py` para que los diseñadores/programadores puedan modificarlos sin alterar la lógica del programa:

| Parámetro | Descripción | Valor por defecto |
|---|---|---|
| `TERMINADOR_RX` | Terminador esperado en las respuestas del banco | `\x00` (Null) |
| `TERMINADOR_TX` | Terminador que se envía al banco | `\x00` (Null) |
| `TIME_OUT_USB` | Timeout de lectura en segundos | 0.5 |
| `TIME_OUT_USB_RELOJ` | Timeout de lectura en segundos para el reloj | 1 |
| `BAUDRATE_USB` | Velocidad de comunicación | 115200 |
| `VID_DEFECTO` | Vendor ID para autodetección del puerto | `"1A86"` |
| `PID_DEFECTO` | Product ID para autodetección del puerto | `"55D4"` |
| `DURACION_ENSAYO_POR_DEFECTO_S` | Duración por defecto del ensayo [s] | 10.0 |
| `PERIODO_MEDICION_BALANZA_RETORNO_MS` | Período de polling de peso durante el retorno [ms] | 1000 |
| `PESO_MINIMO_RETORNO_KG` | Peso mínimo que detiene el retorno [kg] | 5.0 |
| `PESO_MAXIMO_TANQUE_KG` | Peso máximo del tanque (impide iniciar ensayo si se supera) [kg] | 220.0 |
| `CONTRASENIA_TERMINAL` | Contraseña para desbloquear la terminal serie | `"1234"` |

### Unidades
Todas las unidades se expresan en el Sistema Internacional (SIMELA):
- Peso: **kg** (2 decimales)
- Tiempo: **s** (3 decimales)
- Caudal másico: **kg/s**
- Caudal volumétrico: **m³/s**
- Densidad: **kg/m³**

---

## 2. Descripción de la Interfaz de Usuario

### Estilo Visual
- **Tema:** Modo oscuro (Dark Mode), con estilo técnico/industrial de panel de control de laboratorio.
- **Colores principales:**
    - Fondo principal: `#242424` (gris oscuro).
    - Fondo de contenedores/secciones: `#2b2b2b` (gris ligeramente más claro).
    - Fondo de inputs: gris claro mate (`#D3D3D3`).
- **Texto:** blanco o gris muy claro (`#FFFFFF` / `#F5F5F5`) para alta legibilidad. Texto dentro de inputs: gris o negro.
- **Tipografía:** sans-serif, moderna y limpia (Inter).

### Paleta de colores para botones

| Categoría | Color base (reposo) | Color hover |
|---|---|---|
| **Acción principal** (Iniciar / OK / Calcular) | `#388E3C` (verde sólido) | `#4CAF50` |
| **Crítico / Parada** (Detener / Finalizar) | `#D32F2F` (rojo profundo) | `#F44336` |
| **Advertencia / Transición** (Retorno / Pausa) | `#F57C00` (naranja/ámbar) | `#FFB300` |
| **Secundario / Neutro** (Refrescar / Config) | `#1976D2` (azul) o `#424242` (gris) | `#2196F3` o `#545454` |

Textos dentro de botones de colores saturados: blanco puro (`#FFFFFF`) o blanco roto (`#F5F5F5`).

### Sliders Manual/Automático
Los sliders tienen dos posiciones con colores distintivos:
- **Manual (M):** color naranja (`#F57C00`).
- **Automático (A):** color verde (`#388E3C`).

Al iniciar el programa, todos los sliders comienzan en modo **Automático**.

### Contenedor principal
Toda la interfaz está envuelta en un contenedor con desplazamiento vertical (scrollable) para garantizar que los elementos no queden ocultos en monitores con resoluciones bajas.

### Estructura y disposición (Layout)

La interfaz se divide en **cuatro paneles horizontales** principales. Cada sección tiene fondo `#2b2b2b` con esquinas redondeadas y su título incrustado en la línea superior del marco (estilo fieldset/legend de HTML).

#### Panel 1 — Fila superior (dos columnas)

**Columna izquierda — "Configuración"** (~60% del ancho)

Contiene los controles de conexión de hardware dispuestos horizontalmente:
1. Texto **"Banco de Caudal"** + menú desplegable con los puertos COM disponibles + indicador LED (rojo = desconectado, verde = conectado). El desplegable muestra inicialmente el puerto autodetectado, pero permite seleccionar otro manualmente.
2. A continuación, con espaciado suficiente, texto **"Cámara"** + menú desplegable con las cámaras disponibles + indicador LED.
3. Botón circular con ícono de actualizar (🔄) para refrescar la lista de puertos COM y cámaras.
4. En el extremo derecho, ícono de carpeta (📁). Al posicionar el mouse muestra la ruta actual de la carpeta de ensayos. Al hacer clic, abre un explorador de archivos para seleccionar una nueva ruta base.

**Columna derecha — "Advertencias"** (~40% del ancho)

Recuadro de texto donde se muestran mensajes de advertencia al usuario, como por ejemplo: "Falta peso inicial para iniciar ensayo" o "No está conectado el banco de caudal".

#### Panel 2 — Panel central (tres columnas)

**Columna izquierda — Controles de ensayo** (~1/3 del ancho)

Dividida en tres secciones verticales:
1. **Campos de entrada:**
    - "Duración Ensayo [s]": campo numérico (valor por defecto: 10.0 s).
    - "Densidad del Fluido [kg/m³]": campo numérico (valor por defecto: 998.0).
2. **Botón "Iniciar Ensayo":** botón grande verde que ocupa el ancho de la columna.
3. **Botones de retorno:**
    - "Iniciar Retorno" (naranja): ocupa la mitad izquierda.
    - "Finalizar Retorno" (rojo, deshabilitado por defecto): ocupa la mitad derecha.

**Columna central — "Mediciones"** (~1/3 del ancho)

Lista de dos campos con botón de acción, recuadro numérico y slider:
- **"Peso Inicial [kg]"**: botón + campo numérico + slider (M/A).
- **"Peso Final [kg]"**: botón + campo numérico + slider (M/A).

En modo automático, al presionar el botón se solicita el valor al banco de caudal. En modo manual, el campo se habilita para tipeo directo y el botón se deshabilita.

**Columna derecha — "Resultados"** (~1/3 del ancho)

Lista de cuatro campos de solo lectura:
- **"Tiempo [s]"**: campo numérico + slider (M/A).
- **"Peso Neto [kg]"**: campo numérico.
- **"Caudal Másico [kg/s]"**: campo numérico.
- **"Caudal Volumétrico [m³/s]"**: campo numérico.

Debajo de los campos, un botón **"Calcular"** (verde) que procesa las ecuaciones y muestra los resultados.

#### Panel 3 — "Imágenes del Ensayo"

Ocupa el ancho completo de la interfaz. Contiene una galería horizontal (grid de 1 fila × 6 columnas) con marcadores de posición (placeholders):
- Cada marcador tiene forma cuadrada con esquinas redondeadas y fondo gris claro.
- En el centro llevan el ícono de una cámara fotográfica.
- Debajo de cada cuadro aparece la etiqueta: "Imagen 1", "Imagen 2", ..., "Imagen 6".

#### Panel 4 — "Terminal"

Ocupa el ancho completo de la interfaz. Está protegida por contraseña.
- **Estado bloqueado (por defecto):** muestra un campo de contraseña y un botón "Desbloquear".
- **Estado desbloqueado:** despliega una terminal serie con:
    - Un textbox de solo lectura que muestra los datos enviados (TX) y recibidos (RX).
    - Un campo de entrada para escribir comandos manualmente.
    - Un selector de terminador (Null, LF, CR, CRLF, Ninguno).
    - Botones "Enviar", "Limpiar" y "🔒 Bloquear".

### Imagen de referencia
Existe una imagen llamada `IU.png` dentro de la carpeta `software/` que sirve como guía visual del diseño.

---

## 3. Descripción del Funcionamiento

### 3.1. Inicio del programa

Al iniciar el programa:
1. Se intenta detectar automáticamente el puerto COM del banco de caudal a partir del Vendor ID y Product ID configurados. Si se encuentra, se establece la conexión. El usuario puede cambiar el puerto desde el desplegable si fuera necesario.
2. Se listan las cámaras USB disponibles y se conecta a la primera encontrada. Si no hay cámara, el programa sigue funcionando normalmente pero sin capturar fotos.
3. Los indicadores LED reflejan el estado de conexión de cada dispositivo y se actualizan periódicamente.

### 3.2. Comunicación USB COM

La comunicación con el banco de caudal utiliza los siguientes parámetros serie: **115200 baudios, 8 bits de datos, sin paridad, 1 bit de stop**. Las señales de control DTR y RTS se deshabilitan para evitar reinicios en microcontroladores (como ESP32/Arduino).

Tanto los comandos enviados como los datos recibidos son cadenas de caracteres ASCII finalizadas con un **terminador configurable** (por defecto `\x00`). Los terminadores de envío y recepción se configuran de forma independiente.

**Comandos enviados al banco de caudal:**

| Comando | Longitud (sin terminador) | Espera respuesta |
|---|---|---|
| `INICIAR ENSAYO` | 15 caracteres | No |
| `FINALIZAR ENSAYO` | 16 caracteres | Sí (tiempo del ensayo) |
| `MEDICION BALANZA` | 17 caracteres | Sí (valor de peso) |
| `MEDICION RELOJ` | 16 caracteres | Sí (valor de tiempo) |
| `MEDICION COMPLETA` | 17 caracteres | Sí (peso + tiempo) |
| `INICIAR RETORNO` | — | No |
| `FINALIZAR RETORNO` | — | No |

**Formato de datos recibidos:**

| Tipo de medición | Formato | Ejemplo |
|---|---|---|
| **MEDICION BALANZA** | String de 7 caracteres + terminador. Parte entera, punto decimal, parte decimal. | `"123.456"` |
| **MEDICION RELOJ** | String de 8 caracteres + terminador. Parte entera, punto decimal, parte decimal. | `"1234.567"` |
| **MEDICION COMPLETA** | Dos strings consecutivos: primero el peso (formato BALANZA), luego el tiempo (formato RELOJ). | — |

### 3.3. Modos de operación: Manual y Automático

Los campos: Peso Inicial, Peso Final y Tiempo tienen un slider que permite seleccionar entre modo **Manual** y **Automático**. El modo es independiente para cada campo.

- **Modo Automático (A):** el valor se obtiene del banco de caudal. El campo numérico está deshabilitado (no se puede editar) y el botón de medición está habilitado. Al iniciar el programa, todos los campos comienzan en este modo.
- **Modo Manual (M):** el campo numérico se habilita para que el usuario ingrese el valor manualmente. El botón de medición se deshabilita. Los valores ingresados se usan para los cálculos.

**Validación de campos numéricos:** todos los campos numéricos validan que los valores ingresados sean números válidos. No se permite el ingreso de letras ni caracteres no numéricos (excepto el punto decimal y el signo menos).

### 3.4. Ensayo de caudal

#### Precondiciones para iniciar un ensayo

Para poder presionar "Iniciar Ensayo" se deben cumplir **todas** las siguientes condiciones:
1. Se debe haber ingresado un valor de **densidad** válido.
2. Se debe haber ingresado una **duración de ensayo** válida (mayor a 0).
3. Se debe contar con un **peso inicial** válido, ya sea obtenido del banco (presionando el botón en modo automático) o ingresado manualmente. Al iniciar un nuevo ensayo, el peso inicial del ensayo anterior se borra, por lo que siempre debe volver a tomarse o ingresarse.
4. El peso inicial no debe superar el **peso máximo del tanque** (macro `PESO_MAXIMO_TANQUE_KG`). Si lo supera, se muestra una advertencia indicando que se debe vaciar el tanque mediante el retorno.
5. No debe haber un **ensayo anterior pendiente de cálculo de resultados**. Es decir, después de un ensayo se debe presionar el botón "Calcular" antes de poder iniciar otro.
6. No debe estar en curso un **retorno**.

Si alguna condición no se cumple, se muestra una advertencia en el panel correspondiente.

#### Secuencia del ensayo

1. **Inicio:** al presionar "Iniciar Ensayo":
    - Se borran los resultados del ensayo anterior: Peso Final, Peso Neto, Caudal Másico y Caudal Volumétrico se restablecen a `"---"`. El Tiempo se restablece a `"0.000"`. Las imágenes se reinician a placeholders vacíos.
    - Se crea una nueva carpeta de ensayo dentro de `ensayos_banco_caudal/`, con nombre basado en la fecha y hora (formato `AAAA-MM-DD_HH-MM-SS`).
    - Se envía el comando `INICIAR ENSAYO` al banco de caudal.
    - Se deshabilitan los botones "Iniciar Ensayo" e "Iniciar Retorno".
    - Se toma la **primera foto** (imagen 1, en T=0).

2. **Durante el ensayo:**
    - Se utiliza el reloj de la computadora para medir el tiempo transcurrido, el cual se actualiza en pantalla cada ~50 ms.
    - Las 5 fotos restantes se toman a intervalos iguales de un quinto de la duración. Por ejemplo, si la duración es 25 s, las fotos se toman en T=0, 5, 10, 15, 20 y 25 s.
    - Las imágenes se muestran en los recuadros correspondientes en orden cronológico.

3. **Finalización:** cuando el tiempo transcurrido alcanza la duración del ensayo:
    - Se envía el comando `FINALIZAR ENSAYO` al banco de caudal.
    - Se espera recibir la **duración oficial del ensayo** medida por el banco.
    - Este valor de tiempo es el que se utiliza para calcular los caudales.
    - Si el banco no responde (timeout), el campo Tiempo se muestra como `"---"` y se habilita automáticamente el **modo manual** para que el usuario lo ingrese.
    - Se habilitan nuevamente los botones "Iniciar Ensayo" e "Iniciar Retorno".

### 3.5. Cálculo de resultados

Al presionar el botón **"Calcular"**:

1. Se leen los valores de Peso Final y Tiempo. Si alguno de estos campos está en modo manual, se toma el valor del campo de texto; si está en modo automático, se usa el valor obtenido del banco.
2. Se verifica que existan valores válidos de peso inicial, peso final y tiempo. Si falta alguno, se muestra una advertencia.
3. Se calculan:

| Resultado | Fórmula | Unidad |
|---|---|---|
| **Peso Neto** | Peso Final − Peso Inicial | kg |
| **Caudal Másico** | (Peso Final − Peso Inicial) / Tiempo | kg/s |
| **Caudal Volumétrico** | (Peso Final − Peso Inicial) / (Tiempo × Densidad) | m³/s |

4. Los resultados se muestran en los campos correspondientes.
5. Se genera un archivo **`mediciones.csv`** dentro de la carpeta del ensayo, con una fila por cada variable:

| Variable (columna 1) | Valor (columna 2) |
|---|---|
| fecha y hora [hh:mm:ss - dd/mm/aaaa] | 14:30:00 - 21/05/2026 |
| Tiempo de ensayo [s] | 10.000 |
| Peso inicial [kg] | 5.000 |
| Peso final [kg] | 15.000 |
| Peso neto [kg] | 10.000 |
| Caudal másico [kg/s] | 1.0000 |
| Caudal volumétrico [m3/s] | 0.001002 |
| Densidad [kg/m3] | 998.000 |

6. Luego de calcular los resultados:
    - Se borra el valor de peso inicial, indicando que se debe volver a medir o ingresar para el próximo ensayo.
    - Se desbloquea la posibilidad de iniciar un nuevo ensayo.

### 3.6. Medición de peso (fuera de un ensayo)

Cuando **no** se está ensayando ni en retorno, al presionar el botón **"Peso Inicial"** o **"Peso Final"** (en modo automático):
- Se envía el comando `MEDICION BALANZA` al banco de caudal.
- Se espera recibir el valor de peso.
- El valor se muestra en el campo correspondiente con 2 decimales.

### 3.7. Retorno

El retorno permite devolver el fluido acumulado en el tanque a su origen.

#### Precondiciones
- No se puede iniciar un retorno mientras se está realizando un ensayo.
- No se puede iniciar un ensayo mientras se está realizando un retorno.

#### Secuencia del retorno

1. Al presionar **"Iniciar Retorno":**
    - Se envía el comando `INICIAR RETORNO` al banco de caudal.
    - Se deshabilita el botón "Iniciar Ensayo" y "Iniciar Retorno".
    - Se habilita el botón "Finalizar Retorno".
    - Se inicia un **polling periódico** del peso del tanque: cada `PERIODO_MEDICION_BALANZA_RETORNO_MS` milisegundos se envía el comando `MEDICION BALANZA`.

2. **El retorno se detiene automáticamente** cuando el peso recibido es menor o igual a `PESO_MINIMO_RETORNO_KG`, o **manualmente** cuando el usuario presiona "Finalizar Retorno".

3. Al detenerse:
    - Se envía el comando `FINALIZAR RETORNO` al banco de caudal.
    - Se rehabilitan los botones "Iniciar Ensayo" e "Iniciar Retorno".
    - Se deshabilita "Finalizar Retorno".

### 3.8. Captura y almacenamiento de imágenes

- Las imágenes se capturan usando **OpenCV (cv2)** en un hilo secundario.
- Se toman **6 fotos** por ensayo: la primera en T=0 y las 5 restantes distribuidas equitativamente a lo largo de la duración del ensayo.
- Cada imagen se muestra en el recuadro correspondiente (Imagen 1 a Imagen 6) en orden cronológico.
- Las imágenes se guardan como archivos `.jpg` con nombres `img_1.jpg` a `img_6.jpg`.
- La estructura de carpetas es:
    ```
    <ruta_base>/ensayos_banco_caudal/
    └── 2026-05-21_14-30-00/
        ├── img_1.jpg
        ├── img_2.jpg
        ├── ...
        ├── img_6.jpg
        └── mediciones.csv
    ```
- La **ruta base** donde se crea la carpeta `ensayos_banco_caudal` se puede cambiar desde el ícono de carpeta en la interfaz. La ruta seleccionada se guarda en un archivo `config.json` para que persista entre reinicios de la aplicación.
- Si no hay cámara conectada, el programa funciona normalmente sin tomar fotos.

### 3.9. Terminal serie

La terminal serie permite enviar comandos directamente al banco de caudal y ver las tramas de datos en ambas direcciones (TX y RX).

- **Acceso restringido:** la terminal está bloqueada por defecto. Para desbloquearla se debe ingresar la contraseña configurada en `CONTRASENIA_TERMINAL`. Se puede volver a bloquear presionando "🔒 Bloquear".
- **Funcionalidades disponibles:**
    - Enviar un comando de texto libre con el terminador seleccionado (Null, LF, CR, CRLF o ninguno).
    - Visualizar en tiempo real las tramas enviadas (`> TX:`) y recibidas (`< RX:`), con caracteres no imprimibles formateados (por ejemplo, `\0`, `\r`, `\n`).
    - Limpiar el historial de la terminal.
- **Nota:** la terminal funciona de forma transparente junto con los comandos enviados automáticamente por el programa. Cualquier comunicación (automática o manual) se refleja en la terminal si está desbloqueada.

### 3.10. Peso máximo del tanque

Si al finalizar un ensayo el peso final obtenido es **mayor o igual** al valor de `PESO_MAXIMO_TANQUE_KG`, no se permite iniciar un nuevo ensayo. Se muestra una advertencia indicando que se debe vaciar el tanque usando la función de retorno.
