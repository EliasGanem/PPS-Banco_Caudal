@echo off

echo ==============================================
echo   Instalador de Software - Banco de Caudal
echo ==============================================
echo.

:: 1. Verificar si Python esta instalado correctamente
python -c "print('ok')" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Python no fue detectado o no esta configurado.
    echo [INFO] Descargando instalador oficial de Python 3.11...
    echo.
    curl -# -o python_installer.exe https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe
    
    echo.
    echo [INFO] Iniciando el instalador de Python... 
    echo [INFO] Se abrira una ventana mostrando el progreso de instalacion.
    :: Instalacion pasiva (muestra barra de progreso) agregando Python al PATH
    start /wait python_installer.exe /passive InstallAllUsers=0 PrependPath=1 Include_test=0
    
    echo [INFO] Instalacion finalizada.
    del python_installer.exe
    
    :: Refrescamos la variable PATH en esta consola para usar python inmediatamente
    set "PATH=%LocalAppData%\Programs\Python\Python311\Scripts\;%LocalAppData%\Programs\Python\Python311\;%PATH%"
) else (
    echo [INFO] Python ya se encuentra instalado y funcionando.
)

:: 2. Verificar ejecucion final
python -c "print('ok')" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] CRITICO: Python se instalo pero el sistema no lo reconoce.
    echo Por favor reinicie la computadora y vuelva a ejecutar este archivo.
    pause
    exit /b
)

:: 3. Crear entorno virtual dentro de software
echo.
echo [INFO] Creando entorno virtual aislado (venv)...
cd software
python -m venv venv

:: 4. Activar e instalar dependencias
echo [INFO] Instalando librerias y requerimientos (esto demorara unos minutos)...
echo.
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requerimientos.txt
cd ..

:: 5. Crear lanzador de inicio rapido en la raiz
echo.
echo [INFO] Creando archivo de inicio rapido "BC-Windows.bat"...
(
echo @echo off
echo echo Iniciando Software del Banco de Caudal...
echo cd software
echo call venv\Scripts\activate.bat
echo start python main.py
echo exit
) > BC-Windows.bat

echo.
echo ==============================================
echo   Instalacion completada con exito.
echo ==============================================
echo Ya puede abrir el programa haciendo doble clic en "BC-Windows.bat".
echo.
pause
