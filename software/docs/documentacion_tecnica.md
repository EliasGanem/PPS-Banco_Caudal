# Documentación Técnica — Software de Control: Banco de Caudal

---

## Índice

1. [Introducción](#1-introducción)
2. [Arquitectura del Sistema](#2-arquitectura-del-sistema)
3. [Estructura de Archivos](#3-estructura-de-archivos)
4. [Descripción de Módulos](#4-descripción-de-módulos)
5. [Diagramas de Flujo del Funcionamiento](#5-diagramas-de-flujo-del-funcionamiento)
6. [Protocolo de Comunicación Serie](#6-protocolo-de-comunicación-serie)
7. [Modelo de Concurrencia](#7-modelo-de-concurrencia)
8. [Almacenamiento de Datos](#8-almacenamiento-de-datos)
9. [Renderización de Diagramas PlantUML](#9-renderización-de-diagramas-plantuml)

---

## 1. Introducción

Este documento describe la arquitectura, el diseño y el funcionamiento interno del software de control del Banco de Caudal. Está dirigido a desarrolladores y diseñadores que necesiten comprender, mantener o extender el sistema.

El software es una aplicación de escritorio multiplataforma (Linux/Windows) que:
- Controla un banco de caudal a través de comunicación **USB COM** (serie).
- Captura imágenes sincronizadas con el ensayo mediante una **cámara USB**.
- Calcula caudales másico y volumétrico a partir de las mediciones de peso y tiempo.
- Genera reportes en formato **CSV** y almacena las imágenes de cada ensayo.

### Tecnologías

| Componente | Tecnología | Paquete |
|---|---|---|
| Interfaz gráfica | CustomTkinter | `customtkinter` |
| Comunicación serie | pyserial | `serial` |
| Cámara USB | OpenCV | `cv2` |
| Concurrencia | threading | stdlib |
| Procesamiento de imagen | Pillow | `PIL` |

---

## 2. Arquitectura del Sistema

La aplicación sigue un patrón de **inyección de dependencias** donde `main.py` crea las instancias de los drivers y la lógica de negocio, y las inyecta en la interfaz gráfica.

**Diagrama PlantUML:** [`diagramas/arquitectura.puml`](diagramas/arquitectura.puml)

```
┌──────────────────────────────────────────────────────────────────┐
│                        main.py                                   │
│  Crea instancias y las inyecta en AppPrincipal                  │
└──────┬──────────────┬──────────────┬────────────────────────────┘
       │              │              │
       ▼              ▼              ▼
┌─────────────┐ ┌───────────┐ ┌──────────────┐
│   drivers/  │ │   core/   │ │    config.py │
│             │ │           │ │              │
│ Comunicación│ │ Gestor    │ │ Parámetros   │
│ Serie       │ │ Ensayo    │ │ configurables│
│             │ │           │ │              │
│ Cámara USB  │ │ Calculador│ │              │
└──────┬──────┘ │ Caudal    │ └──────────────┘
       │        └─────┬─────┘
       │              │
       ▼              ▼
┌──────────────────────────────────────────────────────────────────┐
│                          ui/                                     │
│                                                                  │
│  AppPrincipal (ventana principal, lógica de UI)                 │
│  ContenedorConTitulo, IndicadorConexion, PanelImagenes, ToolTip │
└──────────────────────────────────────────────────────────────────┘
```

### Capas del sistema

| Capa | Paquete | Responsabilidad |
|---|---|---|
| **Presentación** | `ui/` | Interfaz gráfica, interacción con el usuario, visualización de datos |
| **Lógica de negocio** | `core/` | Cálculos de caudal, gestión de ensayos, almacenamiento de archivos |
| **Drivers** | `drivers/` | Abstracción del hardware: comunicación serie y cámara USB |
| **Configuración** | `config.py` | Parámetros centralizados del sistema |
| **Punto de entrada** | `main.py` | Bootstrapping, inyección de dependencias, logging |

---

## 3. Estructura de Archivos

```
software/
├── main.py                      # Punto de entrada principal
├── config.py                    # Parámetros configurables (macros)
├── config.json                  # Ruta de ensayos persistente (autogenerado)
├── requerimientos.txt           # Dependencias pip
├── IU.png                       # Imagen de referencia de la interfaz
├── descripcion_software.md      # Descripción funcional del software
├── README.md                    # Instrucciones de instalación y ejecución
│
├── core/                        # Lógica de negocio
│   ├── __init__.py
│   ├── gestor_ensayo.py         # Gestión de carpetas, CSV, estado del ensayo
│   └── calculador_caudal.py     # Funciones de cálculo de caudal
│
├── drivers/                     # Abstracción de hardware
│   ├── __init__.py
│   ├── comunicacion_serie.py    # Driver USB COM (pyserial + threading)
│   └── camara_usb.py            # Driver cámara USB (OpenCV + threading)
│
├── ui/                          # Interfaz gráfica
│   ├── __init__.py
│   ├── app_principal.py         # Ventana principal y lógica de UI
│   └── componentes_ui.py        # Componentes reutilizables de UI
│
├── docs/                        # Documentación técnica
│   ├── documentacion_tecnica.md # Este documento
│   └── diagramas/               # Diagramas PlantUML (.puml)
│       ├── arquitectura.puml
│       ├── inicio_programa.puml
│       ├── ensayo_caudal.puml
│       ├── retorno_fluido.puml
│       ├── calculo_resultados.puml
│       ├── medicion_peso.puml
│       ├── captura_imagenes.puml
│       ├── comunicacion_serie.puml
│       ├── modos_manual_automatico.puml
│       └── terminal_serie.puml
│
└── ensayos_banco_caudal/        # Carpeta de resultados (autogenerada)
    └── AAAA-MM-DD_HH-MM-SS/    # Una carpeta por ensayo
        ├── img_1.jpg ... img_6.jpg
        └── mediciones.csv
```

---

## 4. Descripción de Módulos

### 4.1. `main.py` — Punto de entrada

Configura el sistema de logging (consola + archivo `banco_caudal.log`), crea las instancias de los tres componentes principales y lanza la interfaz gráfica.

```python
driver_serie = ComunicacionSerie(vid_defecto=VID_DEFECTO, pid_defecto=PID_DEFECTO)
driver_camara = CamaraUSB()
gestor_ensayo = GestorEnsayo()
app = AppPrincipal(driver_serie, driver_camara, gestor_ensayo)
app.mainloop()
```

Al cerrar la aplicación (o si ocurre un error crítico), se desconectan los drivers en el bloque `finally`.

---

### 4.2. `config.py` — Configuración centralizada

Contiene **constantes globales** que actúan como macros configurables por el programador. Cualquier parámetro que pueda necesitar ajuste por parte del diseñador de hardware está centralizado aquí.

| Grupo | Constantes |
|---|---|
| **Comunicación Serie** | `TERMINADOR_RX`, `TERMINADOR_TX`, `TIME_OUT_USB`, `BAUDRATE_USB`, `VID_DEFECTO`, `PID_DEFECTO` |
| **Ensayo** | `DURACION_ENSAYO_POR_DEFECTO_S`, `PERIODO_MEDICION_BALANZA_RETORNO_MS`, `PESO_MINIMO_RETORNO_KG`, `PESO_MAXIMO_TANQUE_KG` |
| **Seguridad** | `CONTRASENIA_TERMINAL` |

---

### 4.3. `drivers/comunicacion_serie.py` — Clase `ComunicacionSerie`

Encapsula toda la interacción con el puerto serie USB.

#### Métodos principales

| Método | Descripción |
|---|---|
| `listar_puertos()` | Devuelve una lista de puertos COM disponibles en el sistema. |
| `autodetectar_puerto()` | Busca un puerto cuyo VID/PID coincida con los configurados. |
| `conectar(puerto)` | Abre la conexión serie con parámetros 115200/8N1. Deshabilita DTR/RTS para evitar reinicios en microcontroladores. |
| `desconectar()` | Cierra el puerto serie. |
| `esta_conectado()` | Indica si el puerto está abierto (thread-safe). |
| `enviar_comando_async(...)` | Envía un comando en un hilo secundario. Acepta un `callback(comando, respuesta)` que se ejecuta al finalizar. |
| `set_terminal_callback(cb)` | Registra un callback para recibir las tramas TX/RX (usado por la terminal de la UI). |

#### Mecánica de `enviar_comando_async`

1. Crea un `threading.Thread` daemon.
2. Limpia los buffers de entrada y salida del puerto (`reset_input_buffer`, `reset_output_buffer`).
3. Envía el comando codificado en ASCII + el terminador TX.
4. Si `espera_respuesta=True`, lee byte a byte hasta encontrar el terminador RX o hasta timeout.
5. Notifica al `terminal_callback` las tramas enviadas y recibidas.
6. Invoca el `callback` con el comando original y la respuesta decodificada.

#### Thread-safety

Utiliza dos locks:
- `_lock`: protege el estado de conexión (`_conectado`, `puerto_serial`).
- `_lock_com`: serializa las operaciones de envío/recepción para evitar colisiones entre hilos.

---

### 4.4. `drivers/camara_usb.py` — Clase `CamaraUSB`

Encapsula la interacción con la cámara USB mediante OpenCV.

| Método | Descripción |
|---|---|
| `listar_camaras_disponibles()` | Prueba índices 0 a 4 con `cv2.CAP_DSHOW` y devuelve las cámaras que responden. |
| `conectar(indice)` | Abre la cámara y solicita resolución máxima (10000×10000 para forzar la nativa). |
| `desconectar()` | Libera la cámara. |
| `esta_conectada()` | Indica si hay cámara activa (thread-safe). |
| `obtener_frame()` | Obtiene un frame para vista previa en tiempo real. Usa lock **no bloqueante** (`acquire(blocking=False)`) para no interferir con `tomar_foto()`. Retorna el frame BGR o `None`. |
| `tomar_foto(ruta, callback)` | Captura un frame en un hilo secundario, lo guarda en disco y llama al callback `(exito, ruta)`. Descarta un frame previo para evitar imágenes viejas del buffer. |

---

### 4.5. `core/gestor_ensayo.py` — Clase `GestorEnsayo`

Gestiona el ciclo de vida de un ensayo: carpetas, datos y reportes.

| Método | Descripción |
|---|---|
| `_cargar_ruta_base()` | Lee la ruta base desde `config.json`. Si no existe, usa `software/ensayos_banco_caudal/`. |
| `cambiar_ruta_base(ruta)` | Actualiza la ruta base y la persiste en `config.json`. |
| `iniciar_nuevo_ensayo()` | Crea una carpeta `AAAA-MM-DD_HH-MM-SS`, inicializa el diccionario de datos con la fecha/hora y resetea el contador de imágenes. |
| `registrar_dato(param, valor)` | Agrega un par clave-valor al diccionario de datos del ensayo. |
| `guardar_reporte_csv()` | Genera `mediciones.csv` con encoding `utf-8-sig` (compatible con Excel). |
| `obtener_ruta_siguiente_imagen()` | Devuelve la ruta para la próxima imagen (`img_1.jpg` a `img_6.jpg`). |

---

### 4.6. `core/calculador_caudal.py` — Funciones de cálculo

Funciones puras sin estado ni efectos secundarios.

```python
def calcular_caudal_masico(peso_inicial, peso_final, tiempo) -> float:
    """(peso_final - peso_inicial) / tiempo  [kg/s]"""

def calcular_caudal_volumetrico(peso_inicial, peso_final, tiempo, densidad) -> float:
    """(peso_final - peso_inicial) / (tiempo * densidad)  [m³/s]"""
```

Ambas funciones validan que el tiempo (y la densidad en el caso volumétrico) sea mayor a 0, lanzando `ValueError` en caso contrario.

---

### 4.7. `ui/app_principal.py` — Clase `AppPrincipal`

Es la clase principal de la aplicación. Hereda de `ctk.CTk` y contiene:
- La construcción de toda la interfaz gráfica (`construir_ui()`).
- La lógica de interacción con el usuario.
- La orquestación de los drivers y la lógica de negocio.

#### Variables de estado

| Variable | Tipo | Descripción |
|---|---|---|
| `ensayo_en_curso` | `bool` | Indica si hay un ensayo activo. |
| `retorno_en_curso` | `bool` | Indica si hay un retorno activo. |
| `pendiente_resultados` | `bool` | Indica si se deben calcular resultados antes de iniciar otro ensayo. |
| `peso_inicial_val` | `float \| None` | Último peso inicial válido registrado. |
| `peso_final_val` | `float \| None` | Último peso final válido registrado. |
| `tiempo_final_val` | `float \| None` | Tiempo oficial del ensayo (del banco o manual). |
| `var_modo_peso_ini` | `BooleanVar` | True = Auto, False = Manual (peso inicial). |
| `var_modo_peso_fin` | `BooleanVar` | True = Auto, False = Manual (peso final). |
| `var_modo_tiempo` | `BooleanVar` | True = Auto, False = Manual (tiempo). |
| `_visor_camara` | `CTkToplevel \| None` | Referencia a la ventana del visor de cámara (None si está cerrada). |
| `_visor_activo` | `bool` | Indica si el loop de actualización del visor debe seguir ejecutándose. |

#### Interceptor de advertencias

Se instala un `UILogHandler` que captura todos los logs de nivel `WARNING` o superior y los muestra en el panel de advertencias de la UI. Esto permite que cualquier módulo del sistema emita advertencias visibles para el usuario simplemente usando `logger.warning(...)`.

---

### 4.8. `ui/componentes_ui.py` — Componentes reutilizables

| Clase | Descripción |
|---|---|
| `ContenedorConTitulo` | Frame con borde y título superpuesto (emula `<fieldset>` + `<legend>` de HTML). |
| `IndicadorConexion` | LED visual (canvas oval) que cambia entre rojo (`#5c1c1c`) y verde (`#32CD32`). |
| `PanelImagenes` | Grid 1×6 con placeholders para mostrar las fotos del ensayo. Soporta `actualizar_imagen()` y `reiniciar_panel()`. |
| `ToolTip` | Tooltip que aparece al pasar el mouse sobre un widget, con retardo de 500 ms. |

---

## 5. Diagramas de Flujo del Funcionamiento

Todos los diagramas están escritos en **PlantUML** y se encuentran en la carpeta `docs/diagramas/`. Consulte la [sección 9](#9-renderización-de-diagramas-plantuml) para instrucciones de renderización.

### 5.1. Inicio del programa
**Archivo:** [`diagramas/inicio_programa.puml`](diagramas/inicio_programa.puml)

Describe el flujo desde que se ejecuta `main.py`:
1. Configuración de logging.
2. Creación de instancias (inyección de dependencias).
3. Construcción de la UI.
4. Inicialización de hardware (detección de cámaras y puertos COM, autodetección por VID/PID).
5. Inicio del monitoreo periódico de conexión.
6. Lanzamiento del mainloop.

---

### 5.2. Ensayo de caudal
**Archivo:** [`diagramas/ensayo_caudal.puml`](diagramas/ensayo_caudal.puml)

Cubre el flujo completo del ensayo dividido en tres fases:

1. **Validación de precondiciones:** verifica que no haya resultados pendientes, que no esté en retorno, que haya peso inicial válido (según modo), que no se supere el peso máximo, y que la duración y densidad sean válidas.
2. **Inicio del ensayo:** limpia resultados anteriores, crea carpeta, envía `INICIAR ENSAYO`, captura primera foto, e inicia el bucle temporal.
3. **Bucle del ensayo:** cada ~50 ms verifica el tiempo transcurrido, toma fotos en los intervalos correspondientes, y al alcanzar la duración envía `FINALIZAR ENSAYO`.
4. **Finalización:** recibe el tiempo oficial del banco (o habilita modo manual si hay timeout), marca `pendiente_resultados` y habilita los botones.

---

### 5.3. Retorno de fluido
**Archivo:** [`diagramas/retorno_fluido.puml`](diagramas/retorno_fluido.puml)

Describe:
1. Validación (no puede estar ensayando ni ya en retorno).
2. Envío de `INICIAR RETORNO`.
3. Polling periódico de peso (`MEDICION BALANZA` cada `PERIODO_MEDICION_BALANZA_RETORNO_MS`).
4. Condiciones de parada: peso ≤ `PESO_MINIMO_RETORNO_KG` (automática) o botón "Finalizar Retorno" (manual).
5. Envío de `FINALIZAR RETORNO`.

---

### 5.4. Cálculo de resultados
**Archivo:** [`diagramas/calculo_resultados.puml`](diagramas/calculo_resultados.puml)

Detalla:
1. Lectura de valores según modo (manual o automático) para tiempo y peso final.
2. Validación de datos completos (peso inicial, peso final, tiempo).
3. Cálculos: peso neto, caudal másico, caudal volumétrico.
4. Actualización de indicadores en pantalla.
5. Generación del reporte CSV.
6. Reset del estado: se borra el peso inicial y se desbloquea la posibilidad de un nuevo ensayo.

---

### 5.5. Medición de peso
**Archivo:** [`diagramas/medicion_peso.puml`](diagramas/medicion_peso.puml)

Flujo al presionar "Peso Inicial" o "Peso Final" fuera de un ensayo:
1. Verificación de que no hay ensayo/retorno en curso.
2. Envío de `MEDICION BALANZA` en hilo secundario.
3. Recepción y parsing del valor.
4. Actualización del campo correspondiente.

---

### 5.6. Captura y almacenamiento de imágenes
**Archivo:** [`diagramas/captura_imagenes.puml`](diagramas/captura_imagenes.puml)

Describe el proceso de captura de una foto:
1. Verificación del límite de 6 fotos.
2. Obtención de la ruta de destino del `GestorEnsayo`.
3. Captura en hilo secundario (descarte de frame viejo + lectura del actual).
4. Guardado con `cv2.imwrite`.
5. Callback seguro a la UI para mostrar la imagen.

---

### 5.7. Modos Manual y Automático
**Archivo:** [`diagramas/modos_manual_automatico.puml`](diagramas/modos_manual_automatico.puml)

Flujo al cambiar un slider entre Manual y Automático:
- **Automático:** deshabilita el campo numérico, habilita el botón de medición.
- **Manual:** habilita el campo numérico, deshabilita el botón de medición.

---

### 5.8. Visor de cámara en tiempo real

El botón 📷 junto al título "Imágenes del Ensayo" abre una ventana `CTkToplevel` que muestra la imagen de la cámara en tiempo real (~30 FPS). El flujo es:
1. Si el visor ya está abierto, solo se enfoca la ventana existente.
2. Se crea la ventana con un label de 640×480 px como área de visualización.
3. Se inicia un loop con `after(33ms)` que llama a `obtener_frame()` del driver.
4. Cada frame se convierte de BGR (OpenCV) a RGB (PIL), se escala para caber en 640×480 manteniendo aspecto, y se muestra como `CTkImage`.
5. Si no hay cámara conectada, se muestra el texto "No hay cámara conectada".
6. Al cerrar la ventana (botón X), se detiene el loop y se destruye el `CTkToplevel`.

> **Nota sobre concurrencia:** `obtener_frame()` usa `lock.acquire(blocking=False)`, por lo que si el hilo de captura de fotos del ensayo está usando la cámara, el visor simplemente salta ese frame sin bloquearse.

---

### 5.9. Terminal serie
**Archivo:** [`diagramas/terminal_serie.puml`](diagramas/terminal_serie.puml)

Describe:
1. Autenticación con contraseña.
2. Desbloqueo del panel de terminal.
3. Envío de comandos manuales con terminador seleccionable.
4. Visualización de tramas TX/RX.
5. Opciones de limpiar y bloquear.

---

### 5.10. Comunicación serie (diagrama de secuencia)
**Archivo:** [`diagramas/comunicacion_serie.puml`](diagramas/comunicacion_serie.puml)

Diagrama de secuencia que muestra la interacción entre:
- **UI Principal (Hilo Main):** inicia el comando.
- **ComunicacionSerie:** crea el hilo.
- **Hilo Secundario:** ejecuta TX/RX sin bloquear la UI.
- **Banco de Caudal:** hardware destino.

Se ilustran dos escenarios: envío con respuesta y envío sin respuesta.

---

## 6. Protocolo de Comunicación Serie

### Parámetros de conexión

| Parámetro | Valor |
|---|---|
| Baudrate | 115200 |
| Bits de datos | 8 |
| Paridad | Ninguna |
| Bits de stop | 1 |
| Control de flujo | DTR=Off, RTS=Off |
| Timeout de lectura | 0.5 s (configurable) |

### Autodetección del puerto

El software busca automáticamente un puerto COM cuyo **Vendor ID** y **Product ID** coincidan con los configurados en `config.py`. Esto permite que el usuario no tenga que seleccionar el puerto manualmente en la mayoría de los casos.

### Formato de tramas

**Envío (TX):**
```
[comando ASCII] + [TERMINADOR_TX]
```
Ejemplo: `INICIAR ENSAYO\x00`

**Recepción (RX):**
```
[datos ASCII] + [TERMINADOR_RX]
```
El software lee byte a byte hasta encontrar `TERMINADOR_RX` o agotar el timeout.

### Tabla de comandos y respuestas

| Comando TX | Largo (sin term.) | ¿Espera RX? | Formato RX | Largo RX (sin term.) |
|---|---|---|---|---|
| `INICIAR ENSAYO` | 15 | No | — | — |
| `FINALIZAR ENSAYO` | 16 | Sí | `xxxx.xxx` (tiempo) | 8 |
| `MEDICION BALANZA` | 17 | Sí | `xxx.xxx` (peso) | 7 |
| `MEDICION RELOJ` | 16 | Sí | `xxxx.xxx` (tiempo) | 8 |
| `MEDICION COMPLETA` | 17 | Sí | peso + tiempo (2 strings) | 7 + 8 |
| `INICIAR RETORNO` | — | No | — | — |
| `FINALIZAR RETORNO` | — | No | — | — |

---

## 7. Modelo de Concurrencia

La aplicación utiliza **tres niveles de ejecución:**

### Hilo principal (MainThread)
- Ejecuta el mainloop de CustomTkinter.
- Maneja todos los eventos de la UI.
- **Nunca se bloquea** con operaciones de I/O.

### Hilos secundarios (daemon threads)
- Se crean para cada operación de comunicación serie (`enviar_comando_async`) y cada captura de foto (`tomar_foto`).
- Son threads **daemon** para que se terminen automáticamente al cerrar la aplicación.
- **Nunca actualizan la UI directamente.** En su lugar, usan callbacks que la UI procesa con `self.after(0, callback)`, que es el mecanismo thread-safe de Tkinter.

### Flujo de datos entre hilos

```
 Hilo Secundario                    Hilo Principal (UI)
 ─────────────────                  ────────────────────
 1. Enviar comando TX
 2. Leer respuesta RX
 3. callback(cmd, resp)  ──────►   after(0, _procesar_respuesta_ui)
                                    4. Actualizar widgets
```

### Locks utilizados

| Lock | Ubicación | Protege |
|---|---|---|
| `ComunicacionSerie._lock` | `drivers/comunicacion_serie.py` | Estado de conexión (`_conectado`, `puerto_serial`) |
| `ComunicacionSerie._lock_com` | `drivers/comunicacion_serie.py` | Operaciones de lectura/escritura serie (serialización) |
| `CamaraUSB._lock` | `drivers/camara_usb.py` | Acceso al objeto `VideoCapture` |

### Timers periódicos (after)

| Timer | Intervalo | Propósito |
|---|---|---|
| `monitorear_estado` | 500 ms | Actualizar LEDs de conexión |
| `_verificar_progreso_ensayo_pc` | 50 ms | Bucle del ensayo (tiempo, fotos) |
| `_polling_retorno` | Configurable (`PERIODO_MEDICION_BALANZA_RETORNO_MS`) | Polling de peso durante retorno |
| `_actualizar_visor_camara` | 33 ms (~30 FPS) | Actualizar vista previa de cámara en tiempo real |

---

## 8. Almacenamiento de Datos

### Persistencia de configuración

La ruta base de ensayos se almacena en `software/config.json`:
```json
{
    "carpeta_base": "/home/usuario/mis_ensayos/ensayos_banco_caudal"
}
```

### Estructura de un ensayo

Cada ensayo genera una carpeta con la fecha y hora como nombre:

```
ensayos_banco_caudal/
└── 2026-05-21_14-30-00/
    ├── img_1.jpg      # Foto en T=0
    ├── img_2.jpg      # Foto en T=1/5 de duración
    ├── img_3.jpg      # Foto en T=2/5 de duración
    ├── img_4.jpg      # Foto en T=3/5 de duración
    ├── img_5.jpg      # Foto en T=4/5 de duración
    ├── img_6.jpg      # Foto en T=duración
    └── mediciones.csv  # Reporte de datos
```

### Formato del archivo CSV

El CSV utiliza encoding `utf-8-sig` para compatibilidad con Microsoft Excel. Tiene dos columnas sin encabezado:

| Columna 1 (Variable con unidad) | Columna 2 (Valor) |
|---|---|
| `fecha y hora [hh:mm:ss - dd/mm/aaaa]` | `14:30:00 - 21/05/2026` |
| `Tiempo de ensayo [s]` | `10.000` |
| `Peso inicial [kg]` | `5.000` |
| `Peso final [kg]` | `15.000` |
| `Peso neto [kg]` | `10.000` |
| `Caudal másico [kg/s]` | `1.0000` |
| `Caudal volumétrico [m3/s]` | `0.001002` |
| `Densidad [kg/m3]` | `998.000` |

---

## 9. Renderización de Diagramas PlantUML

Los diagramas se encuentran en `docs/diagramas/*.puml`. Para renderizarlos a imagen:

### Opción 1: Servidor web de PlantUML (sin instalación)
Copiar el contenido del archivo `.puml` y pegarlo en: https://www.plantuml.com/plantuml/uml

### Opción 2: Extensión de VS Code
Instalar la extensión **PlantUML** (`jebbs.plantuml`) en VS Code. Permite previsualizar los diagramas directamente con `Alt+D`.

### Opción 3: Línea de comandos (requiere Java)
```bash
# Instalar PlantUML
sudo apt install plantuml    # Linux (Debian/Ubuntu)

# Renderizar un diagrama
plantuml docs/diagramas/ensayo_caudal.puml

# Renderizar todos los diagramas
plantuml docs/diagramas/*.puml
```

### Opción 4: Docker (sin instalación local)
```bash
docker run --rm -v $(pwd)/docs/diagramas:/data plantuml/plantuml /data/*.puml
```

### Lista de diagramas disponibles

| Archivo | Tipo | Descripción |
|---|---|---|
| `arquitectura.puml` | Diagrama de clases/paquetes | Arquitectura del sistema y dependencias |
| `inicio_programa.puml` | Diagrama de flujo (actividad) | Secuencia de inicio del programa |
| `ensayo_caudal.puml` | Diagrama de flujo (actividad) | Flujo completo del ensayo de caudal |
| `retorno_fluido.puml` | Diagrama de flujo (actividad) | Flujo del retorno de fluido |
| `calculo_resultados.puml` | Diagrama de flujo (actividad) | Flujo del cálculo de resultados |
| `medicion_peso.puml` | Diagrama de flujo (actividad) | Medición de peso fuera de ensayo |
| `captura_imagenes.puml` | Diagrama de flujo (actividad) | Captura y almacenamiento de imágenes |
| `modos_manual_automatico.puml` | Diagrama de flujo (actividad) | Cambio entre modo manual y automático |
| `comunicacion_serie.puml` | Diagrama de secuencia | Interacción entre hilos y hardware |
| `terminal_serie.puml` | Diagrama de flujo (actividad) | Autenticación y uso de la terminal |
