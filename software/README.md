# Software de Control: Banco de Caudal

Este software permite controlar un banco de caudal mediante USB COM y registrar imágenes a través de una cámara USB sincronizada con el ensayo. 

El proyecto fue desarrollado para ser **multiplataforma** (Linux y Windows). Para evitar conflictos de librerías con el sistema operativo y asegurar la portabilidad, se debe utilizar un entorno virtual (`venv`).

## Instalación y Configuración del Entorno (venv)

Antes de comenzar, abrí una terminal (en Linux) o una ventana de PowerShell/CMD (en Windows) en el directorio raíz de este proyecto.

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

---

## Ejecución del Programa

Siempre asegurate de **tener activado el entorno virtual** antes de correr el programa.

Para iniciar la aplicación, ejecutá:
```bash
python main.py
```

## Configuración para Desarrolladores

Si sos diseñador de hardware y necesitás modificar los parámetros de la placa para que la aplicación autodetecte el puerto automáticamente, abrí el archivo `main.py` y modificá las constantes ubicadas en la función principal:

```python
VID_DEFECTO = "2341"  # Modificar por el Vendor ID de tu placa
PID_DEFECTO = "0043"  # Modificar por el Product ID de tu placa
```
