#!/bin/bash

# Forzar ejecucion en una ventana de terminal si se hizo doble clic
if [ ! -t 0 ]; then
    for term in x-terminal-emulator gnome-terminal konsole xterm; do
        if command -v "$term" >/dev/null 2>&1; then
            if [ "$term" = "gnome-terminal" ]; then
                "$term" -- bash -c "$0; exec bash"
            else
                "$term" -e bash -c "$0; exec bash"
            fi
            exit 0
        fi
    done
fi

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

# Obtener directorio raíz del script (donde está el instalador)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# 2. Crear entorno virtual dentro de software
echo ""
echo "[INFO] Creando entorno virtual aislado (venv)..."
cd "$SCRIPT_DIR/software"
python3 -m venv venv

# 3. Activar e instalar requerimientos
echo ""
echo "[INFO] Instalando requerimientos (esto puede demorar unos minutos)..."
source venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requerimientos.txt
cd "$SCRIPT_DIR"

# 4. Crear lanzador de inicio rápido en la raíz
echo ""
echo "[INFO] Creando archivo de inicio rapido 'BC-Linux.sh'..."
cat << EOF > BC-Linux.sh
#!/bin/bash
DIR="\$( cd "\$( dirname "\${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "\$DIR/software"
source venv/bin/activate
python3 main.py
EOF
chmod +x BC-Linux.sh

echo ""
echo "=============================================="
echo "  Instalacion completada con exito."
echo "=============================================="
echo "Ya puede abrir el programa haciendo doble clic o ejecutando './BC-Linux.sh'."
echo ""
read -p "Presione [Enter] para salir..."
