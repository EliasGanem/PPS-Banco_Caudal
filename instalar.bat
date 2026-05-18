@echo off
setlocal enabledelayedexpansion

echo ==============================================
echo   Instalador de Software - Banco de Caudal
echo ==============================================
echo.

:: 1. Verificar si Python esta instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Python no detectado en el sistema.
    echo [INFO] Descargando instalador oficial de Python 3.11...
    echo.
    :: Utilizamos curl (integrado en Windows 10/11) que muestra una barra de progreso nativa (-#)
    curl -# -o python_installer.exe https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe
    
    echo.
    echo [INFO] Instalando Python silenciosamente. Por favor espere, esto puede demorar unos minutos...
    :: Instalacion silenciosa agregando Python a las variables de entorno (PATH)
    start /wait python_installer.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
    
    echo [INFO] Python instalado correctamente.
    del python_installer.exe
    
    :: Refrescamos la variable PATH para esta sesion de consola para poder usar 'python' enseguida
    set PATH=%LocalAppData%\Programs\Python\Python311\Scripts\;%LocalAppData%\Programs\Python\Python311\;%PATH%
) else (
    echo [INFO] Python ya se encuentra instalado.
)

:: 2. Verificar que Python responde a los comandos
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] No se pudo ejecutar Python. Es posible que deba reiniciar su computadora para que se apliquen los cambios en el sistema.
    pause
    exit /b
)

:: 3. Crear entorno virtual
echo.
echo [INFO] Creando entorno virtual aislado (venv)...
python -m venv venv

:: 4. Activar e instalar dependencias
echo [INFO] Instalando librerias y requerimientos (esto puede demorar unos minutos)...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requerimientos.txt

:: 5. Crear lanzador de inicio rapido
echo.
echo [INFO] Creando archivo de inicio rapido "iniciar_banco.bat"...
echo @echo off > iniciar_banco.bat
echo call venv\Scripts\activate.bat >> iniciar_banco.bat
echo start python main.py >> iniciar_banco.bat
echo exit >> iniciar_banco.bat

echo.
echo ==============================================
echo   Instalacion completada con exito.
echo ==============================================
echo Ya puede abrir el programa en cualquier momento haciendo doble clic en el archivo "iniciar_banco.bat" que se acaba de crear en esta misma carpeta.
echo.
pause
