#!/bin/bash

echo "=============================================="
echo "  Instalador de Software - Banco de Caudal"
echo "=============================================="
echo ""

# 1. Verificar dependencias del sistema
echo "[INFO] Verificando dependencias del sistema (python3, pip, venv)..."
if ! command -v python3 &> /dev/null || ! command -v pip3 &> /dev/null || ! python3 -m venv -h &> /dev/null; then
    echo "[INFO] Faltan paquetes base de Python."
    echo "[INFO] Se solicitaran permisos de administrador (sudo) para instalarlos mediante apt..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv python3-tk
    echo "[INFO] Dependencias de SO instaladas."
else
    echo "[INFO] Dependencias base ya se encuentran instaladas."
fi

# 2. Crear entorno virtual
echo ""
echo "[INFO] Creando entorno virtual aislado (venv)..."
python3 -m venv venv

# 3. Activar e instalar requerimientos
echo "[INFO] Instalando requerimientos (esto puede demorar unos minutos)..."
source venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requerimientos.txt

# 4. Crear lanzador de inicio rápido
echo ""
echo "[INFO] Creando archivo de inicio rapido 'iniciar_banco.sh'..."
cat << 'EOF' > iniciar_banco.sh
#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"
source venv/bin/activate
python3 main.py
EOF
chmod +x iniciar_banco.sh

echo ""
echo "=============================================="
echo "  Instalacion completada con exito."
echo "=============================================="
echo "Ya puede abrir el programa haciendo doble clic o ejecutando desde la terminal el archivo './iniciar_banco.sh' que se acaba de crear."
echo ""
read -p "Presione [Enter] para salir..."
