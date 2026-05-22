# Software de Control: Banco de Caudal

Este software permite controlar un banco de caudal mediante USB COM y registrar imágenes a través de una cámara USB sincronizada con el ensayo. 

El proyecto fue desarrollado para ser **multiplataforma** (Linux y Windows). Para evitar conflictos de librerías con el sistema operativo y asegurar la portabilidad, se utiliza un entorno virtual (`venv`).

---

## Instalación Rápida (Recomendado)

El repositorio incluye **instaladores automáticos** que se encargan de todo: verificar/instalar Python, crear el entorno virtual, instalar las dependencias y generar un lanzador de inicio rápido.

### En Linux

1. Abrí una terminal en el directorio raíz del proyecto (donde está `instalador_linux.sh`).
2. Dale permisos de ejecución (solo la primera vez) y ejecutalo:
   ```bash
   chmod +x instalador_linux.sh
   ./instalador_linux.sh
   ```
   > **Nota:** El script puede solicitar permisos de administrador (`sudo`) para instalar paquetes del sistema como `python3`, `python3-pip`, `python3-venv` y `python3-tk` si no están presentes.
3. Al finalizar, se creará un lanzador **`BC-Linux.sh`** en la raíz del proyecto. Para abrir el programa simplemente ejecutá:
   ```bash
   ./BC-Linux.sh
   ```
   También podés hacer doble clic sobre `BC-Linux.sh` desde el explorador de archivos.

### En Windows

1. Navegá al directorio raíz del proyecto (donde está `instalador_windows.bat`).
2. Hacé doble clic en **`instalador_windows.bat`**.
   > **Nota:** Si Python no está instalado, el script lo descargará e instalará automáticamente (Python 3.11). Si el sistema no reconoce Python luego de la instalación, reiniciá la computadora y volvé a ejecutar el instalador.
3. Al finalizar, se creará un lanzador **`BC-Windows.bat`** en la raíz del proyecto. Para abrir el programa simplemente hacé doble clic sobre él.

---

## Ejecución del Programa

Si ya se completó la instalación (ya sea con el instalador automático o de forma manual), podés iniciar la aplicación de las siguientes formas:

| Plataforma | Método rápido | Método manual |
|---|---|---|
| **Linux** | Doble clic o ejecutar `./BC-Linux.sh` | Activar venv y correr `python main.py` (ver abajo) |
| **Windows** | Doble clic en `BC-Windows.bat` | Activar venv y correr `python main.py` (ver abajo) |

---

## Configuración para Desarrolladores

Si sos diseñador de hardware y necesitás modificar los parámetros de la placa para que la aplicación autodetecte el puerto automáticamente, abrí el archivo `main.py` y modificá las constantes ubicadas en la función principal:

```python
VID_DEFECTO = "2341"  # Modificar por el Vendor ID de tu placa
PID_DEFECTO = "0043"  # Modificar por el Product ID de tu placa
```

---

## Instalación Manual (Paso a Paso)

> Si los instaladores automáticos funcionaron correctamente, **no necesitás seguir estos pasos**. Esta sección existe como referencia para diagnóstico o para realizar la instalación de forma manual en caso de que algo falle.

Antes de comenzar, abrí una terminal (en Linux) o una ventana de PowerShell/CMD (en Windows) en el directorio `software/` de este proyecto.

### 1. Crear el Entorno Virtual

**En Windows:**
```cmd
python -m venv venv
```

**En Linux (Ubuntu/Debian):**
*(Si no tenés `venv` instalado, corré primero `sudo apt install python3-venv`)*
```bash
python3 -m venv venv
```

### 2. Activar el Entorno Virtual

**En Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```
**En Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**En Linux:**
```bash
source venv/bin/activate
```
*(Sabrás que estás dentro del entorno virtual porque el prompt de tu consola empezará con `(venv)`).*

### 3. Instalar Dependencias

Con el entorno virtual activado, instalá las librerías necesarias:

```bash
pip install -r requerimientos.txt
```

> **Dependencias Adicionales en Linux:** 
> Para que OpenCV (`cv2`) y CustomTkinter funcionen correctamente en Linux, es probable que necesites instalar algunas librerías del sistema si no las tenés:
> ```bash
> sudo apt-get update
> sudo apt-get install python3-tk libgl1 libglib2.0-0
> ```

### 4. Ejecutar el Programa

Siempre asegurate de **tener activado el entorno virtual** antes de correr el programa.

Para iniciar la aplicación, ejecutá:
```bash
python main.py
```
