import customtkinter as ctk
import logging
import time
from typing import Optional
from tkinter import filedialog
from ui.componentes_ui import IndicadorConexion, PanelImagenes, ContenedorConTitulo, ToolTip
from drivers.comunicacion_serie import ComunicacionSerie
from drivers.camara_usb import CamaraUSB
from core.gestor_ensayo import GestorEnsayo
from core.calculador_caudal import calcular_caudal_masico, calcular_caudal_volumetrico

class UILogHandler(logging.Handler):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
    def emit(self, record):
        if record.levelno >= logging.WARNING:
            msg = self.format(record)
            self.callback(msg)

logger = logging.getLogger(__name__)

# Macros configurables para el retorno
DURACION_ENSAYO_POR_DEFECTO_S = 10.0
PERIODO_POLLING_RETORNO_MS = 1000
PESO_MINIMO_RETORNO_KG = 5.0
PASSWORD_TERMINAL = "1234"

class AppPrincipal(ctk.CTk):
    def __init__(self, driver_serie: ComunicacionSerie, driver_camara: CamaraUSB, gestor: GestorEnsayo):
        super().__init__()
        
        self.driver_serie = driver_serie
        self.driver_camara = driver_camara
        self.gestor = gestor
        
        self.title("Control de Banco de Caudal")
        self.geometry("1100x700")
        ctk.set_appearance_mode("dark")
        
        # Variables de estado del ensayo
        self.ensayo_en_curso = False
        self.retorno_en_curso = False
        self.tiempo_ensayo_objetivo = DURACION_ENSAYO_POR_DEFECTO_S
        self.fotos_tomadas = 0
        self.peso_inicial_val: Optional[float] = None
        self.peso_final_val: Optional[float] = None
        self.tiempo_final_val: Optional[float] = None
        
        self.var_modo_peso_ini = ctk.BooleanVar(value=True) # True = Auto, False = Manual
        self.var_modo_peso_fin = ctk.BooleanVar(value=True)
        self.var_modo_tiempo = ctk.BooleanVar(value=True)
        
        self.pendiente_resultados = False
        
        self.construir_ui()
        
        # Configurar interceptor de logs para Advertencias
        self.ui_log_handler = UILogHandler(self._mostrar_advertencia)
        self.ui_log_handler.setFormatter(logging.Formatter('%(message)s')) # Mostramos solo el mensaje
        logging.getLogger().addHandler(self.ui_log_handler)
        
        # Registrar el callback para la terminal serie
        self.driver_serie.set_terminal_callback(self._on_terminal_data)
        
        self.inicializar_hardware()
        self.monitorear_estado()

    def construir_ui(self):
        self.configure(fg_color="#242424")
        
        # Comando de validación para cajas de texto numéricas
        vcmd = (self.register(self._validar_numero_flotante), '%P')
        
        # Contenedor principal scrolleable para adaptarse a pantallas chicas
        self.main_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)
        
        # Contenedor superior para Puertos y Advertencias
        self.frame_top = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.frame_top.pack(padx=20, pady=(15, 5), fill="x")
        self.frame_top.grid_columnconfigure(0, weight=3, uniform="top_cols") # Ocupa 3/5
        self.frame_top.grid_columnconfigure(1, weight=2, uniform="top_cols") # Ocupa 2/5
        
        # --- Bloque 1A: Configuración ---
        self.frame_config = ContenedorConTitulo(self.frame_top, titulo="Configuración")
        self.frame_config.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        
        self.lbl_banco = ctk.CTkLabel(self.frame_config, text="Banco de Caudal", font=("Inter", 14), text_color="#FFFFFF")
        self.lbl_banco.grid(row=0, column=0, padx=(15, 5), pady=(45, 15), sticky="w")
        
        self.cmb_puertos = ctk.CTkComboBox(self.frame_config, values=["Buscando..."], fg_color="#D3D3D3", text_color="#000000")
        self.cmb_puertos.configure(command=self.cambiar_puerto_serie)
        self.cmb_puertos.grid(row=0, column=1, padx=(0, 10), pady=(45, 15))
        
        self.ind_banco = IndicadorConexion(self.frame_config, "")
        self.ind_banco.grid(row=0, column=2, padx=(0, 20), pady=(45, 15))
        
        self.lbl_camara = ctk.CTkLabel(self.frame_config, text="Cámara", font=("Inter", 14), text_color="#FFFFFF")
        self.lbl_camara.grid(row=0, column=3, padx=(20, 5), pady=(45, 15), sticky="w")
        
        self.cmb_camaras = ctk.CTkComboBox(self.frame_config, values=["Buscando..."], fg_color="#D3D3D3", text_color="#000000")
        self.cmb_camaras.configure(command=self.cambiar_camara)
        self.cmb_camaras.grid(row=0, column=4, padx=(0, 10), pady=(45, 15))
        
        self.ind_camara = IndicadorConexion(self.frame_config, "")
        self.ind_camara.grid(row=0, column=5, padx=(0, 20), pady=(45, 15))
        
        self.btn_refrescar = ctk.CTkButton(self.frame_config, text="🔄", width=40, font=("Inter", 18), fg_color="#1976D2", hover_color="#2196F3", command=self.refrescar_hardware)
        self.btn_refrescar.grid(row=0, column=6, padx=(10, 15), pady=(45, 15))
        
        self.btn_carpeta = ctk.CTkButton(self.frame_config, text="📁", width=40, font=("Inter", 18), fg_color="#455A64", hover_color="#607D8B", command=self.cambiar_carpeta_ensayos)
        self.btn_carpeta.grid(row=0, column=7, padx=(0, 15), pady=(45, 15))
        
        # Tooltip para mostrar la ruta actual
        ToolTip(self.btn_carpeta, lambda: f"Ruta actual:\n{self.gestor.carpeta_base}")
        
        # --- Bloque 1B: Advertencias ---
        self.frame_adv = ContenedorConTitulo(self.frame_top, titulo="Advertencias")
        self.frame_adv.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        
        self.var_advertencia = ctk.StringVar(value="")
        # Usamos un textbox deshabilitado o un label wrap para mostrar el texto
        self.lbl_advertencia = ctk.CTkLabel(self.frame_adv, textvariable=self.var_advertencia, font=("Inter", 14), text_color="#FF9800", justify="left", wraplength=420)
        self.lbl_advertencia.pack(padx=15, pady=(45, 15), anchor="w")

        # Variables para mostrar resultados
        self.var_tiempo = ctk.StringVar(value="0.00")
        self.var_peso_ini = ctk.StringVar(value="---")
        self.var_peso_fin = ctk.StringVar(value="---")
        self.var_peso_neto = ctk.StringVar(value="---")
        self.var_c_masico = ctk.StringVar(value="---")
        self.var_c_volumetrico = ctk.StringVar(value="---")

        # --- Bloque 2: Panel Central ---
        self.frame_medio = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.frame_medio.pack(padx=20, pady=5, fill="x")
        self.frame_medio.grid_columnconfigure(0, weight=4)
        self.frame_medio.grid_columnconfigure(1, weight=3)
        self.frame_medio.grid_columnconfigure(2, weight=3)
        
        # Columna 1: Controles de Ensayo
        self.frame_controles = ctk.CTkFrame(self.frame_medio, fg_color="#2b2b2b", border_width=1, border_color="#555555", corner_radius=8)
        self.frame_controles.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        
        frame_inputs = ctk.CTkFrame(self.frame_controles, fg_color="transparent")
        frame_inputs.pack(padx=15, pady=(15, 10), fill="x")
        frame_inputs.grid_columnconfigure(0, weight=1)
        frame_inputs.grid_columnconfigure(1, weight=1)
        
        lbl_dur = ctk.CTkLabel(frame_inputs, text="Duración Ensayo [s]", text_color="#FFFFFF")
        lbl_dur.grid(row=0, column=0, sticky="w")
        self.ent_duracion = ctk.CTkEntry(frame_inputs, fg_color="#D3D3D3", text_color="#000000", validate="key", validatecommand=vcmd)
        self.ent_duracion.insert(0, str(DURACION_ENSAYO_POR_DEFECTO_S))
        self.ent_duracion.grid(row=1, column=0, padx=(0, 5), sticky="ew")
        
        lbl_den = ctk.CTkLabel(frame_inputs, text="Densidad del Fluido [kg/m³]", text_color="#FFFFFF")
        lbl_den.grid(row=0, column=1, sticky="w")
        self.ent_densidad = ctk.CTkEntry(frame_inputs, fg_color="#D3D3D3", text_color="#000000", validate="key", validatecommand=vcmd)
        self.ent_densidad.insert(0, "998.0")
        self.ent_densidad.grid(row=1, column=1, padx=(5, 0), sticky="ew")
        
        self.btn_iniciar = ctk.CTkButton(self.frame_controles, text="Iniciar Ensayo", command=self.iniciar_ensayo, height=40, font=("Inter", 16, "bold"), fg_color="#388E3C", hover_color="#4CAF50")
        self.btn_iniciar.pack(pady=10, padx=15, fill="x")
        
        frame_retornos = ctk.CTkFrame(self.frame_controles, fg_color="transparent")
        frame_retornos.pack(padx=15, pady=(5, 15), fill="x")
        frame_retornos.grid_columnconfigure(0, weight=1)
        frame_retornos.grid_columnconfigure(1, weight=1)
        
        self.btn_ini_retorno = ctk.CTkButton(frame_retornos, text="Iniciar Retorno", command=self.iniciar_retorno, fg_color="#F57C00", hover_color="#FFB300", text_color="#FFFFFF", height=35)
        self.btn_ini_retorno.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        self.btn_fin_retorno = ctk.CTkButton(frame_retornos, text="Finalizar Retorno", command=self.finalizar_retorno, fg_color="#D32F2F", hover_color="#F44336", text_color="#FFFFFF", height=35, state="disabled")
        self.btn_fin_retorno.grid(row=0, column=1, padx=(5, 0), sticky="ew")
        
        # Columna 2: Mediciones
        self.frame_mediciones = ContenedorConTitulo(self.frame_medio, titulo="Mediciones")
        self.frame_mediciones.grid(row=0, column=1, padx=(5, 5), sticky="nsew")
        
        self.frame_med_inner = ctk.CTkFrame(self.frame_mediciones, fg_color="transparent")
        self.frame_med_inner.pack(padx=15, pady=(35, 20), fill="both", expand=True)
        self.frame_med_inner.grid_columnconfigure(1, weight=1)
        self.frame_med_inner.grid_columnconfigure(2, weight=0)
        
        self.btn_peso_ini = ctk.CTkButton(self.frame_med_inner, text="Peso Inicial [kg]", command=self.tomar_peso_inicial, fg_color="#424242", hover_color="#545454", width=120)
        self.btn_peso_ini.grid(row=0, column=0, pady=10, sticky="w")
        self.ent_peso_ini = ctk.CTkEntry(self.frame_med_inner, textvariable=self.var_peso_ini, state="disabled", fg_color="#D3D3D3", text_color="#000000", width=80, validate="key", validatecommand=vcmd)
        self.ent_peso_ini.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        self.sw_modo_ini = ctk.CTkSwitch(self.frame_med_inner, text="A", command=self._toggle_modo_ini, variable=self.var_modo_peso_ini, progress_color="#388E3C", button_color="#FFFFFF", fg_color="#F57C00")
        self.sw_modo_ini.grid(row=0, column=2, padx=(0, 5), pady=10)
        
        self.btn_peso_fin = ctk.CTkButton(self.frame_med_inner, text="Peso Final [kg]", command=self.tomar_peso_final, fg_color="#424242", hover_color="#545454", width=120)
        self.btn_peso_fin.grid(row=1, column=0, pady=10, sticky="w")
        self.ent_peso_fin = ctk.CTkEntry(self.frame_med_inner, textvariable=self.var_peso_fin, state="disabled", fg_color="#D3D3D3", text_color="#000000", width=80, validate="key", validatecommand=vcmd)
        self.ent_peso_fin.grid(row=1, column=1, padx=10, pady=10, sticky="e")
        self.sw_modo_fin = ctk.CTkSwitch(self.frame_med_inner, text="A", command=self._toggle_modo_fin, variable=self.var_modo_peso_fin, progress_color="#388E3C", button_color="#FFFFFF", fg_color="#F57C00")
        self.sw_modo_fin.grid(row=1, column=2, padx=(0, 5), pady=10)
        
        # Columna 3: Resultados
        self.frame_resultados = ctk.CTkFrame(self.frame_medio, fg_color="#2b2b2b", border_width=1, border_color="#555555", corner_radius=8)
        self.frame_resultados.grid(row=0, column=2, padx=(10, 0), sticky="nsew")
        
        self.btn_calcular = ctk.CTkButton(self.frame_resultados, text="Resultados", command=self.calcular_caudales, fg_color="#388E3C", hover_color="#4CAF50", corner_radius=0, font=("Inter", 16, "bold"))
        self.btn_calcular.pack(fill="x", pady=(0, 10))
        
        frame_res_grid = ctk.CTkFrame(self.frame_resultados, fg_color="transparent")
        frame_res_grid.pack(padx=15, pady=5, fill="both", expand=True)
        frame_res_grid.grid_columnconfigure(1, weight=1)
        frame_res_grid.grid_columnconfigure(2, weight=0)
        
        # Tiempo con slider
        ctk.CTkLabel(frame_res_grid, text="Tiempo [s]", text_color="#FFFFFF").grid(row=0, column=0, pady=4, sticky="w")
        self.ent_tiempo = ctk.CTkEntry(frame_res_grid, textvariable=self.var_tiempo, state="disabled", fg_color="#D3D3D3", text_color="#000000", width=80, validate="key", validatecommand=vcmd)
        self.ent_tiempo.grid(row=0, column=1, padx=(10, 0), pady=4, sticky="e")
        self.sw_modo_tiempo = ctk.CTkSwitch(frame_res_grid, text="A", command=self._toggle_modo_tiempo, variable=self.var_modo_tiempo, progress_color="#388E3C", button_color="#FFFFFF", fg_color="#F57C00")
        self.sw_modo_tiempo.grid(row=0, column=2, padx=(5, 0), pady=4)
        
        labels_res = ["Peso Neto [kg]", "Caudal Másico [kg/s]", "Caudal Volumétrico [m³/s]"]
        vars_res = [self.var_peso_neto, self.var_c_masico, self.var_c_volumetrico]
        
        for i, (lbl_txt, var) in enumerate(zip(labels_res, vars_res)):
            ctk.CTkLabel(frame_res_grid, text=lbl_txt, text_color="#FFFFFF").grid(row=i+1, column=0, pady=4, sticky="w")
            ent = ctk.CTkEntry(frame_res_grid, textvariable=var, state="disabled", fg_color="#D3D3D3", text_color="#000000", width=80)
            ent.grid(row=i+1, column=1, padx=(10, 0), pady=4, sticky="e")

        # --- Bloque 3: Imágenes del Ensayo ---
        self.frame_imagenes = ContenedorConTitulo(self.main_container, titulo="Imágenes del Ensayo")
        self.frame_imagenes.pack(padx=20, pady=(5, 5), fill="x")
        self.panel_img = PanelImagenes(self.frame_imagenes)
        self.panel_img.pack(fill="x", padx=10, pady=(35, 15))

        # --- Bloque 4: Terminal ---
        self.frame_terminal = ContenedorConTitulo(self.main_container, titulo="Terminal")
        self.frame_terminal.pack(padx=20, pady=(5, 15), fill="x")
        
        # Frame de autenticación (Visible por defecto)
        self.frame_auth = ctk.CTkFrame(self.frame_terminal, fg_color="transparent")
        self.frame_auth.pack(padx=15, pady=(45, 15), fill="x")
        
        lbl_auth = ctk.CTkLabel(self.frame_auth, text="Ingrese contraseña:", text_color="#FFFFFF")
        lbl_auth.pack(side="left", padx=(0, 10))
        
        self.ent_pass = ctk.CTkEntry(self.frame_auth, show="*", fg_color="#D3D3D3", text_color="#000000", width=150)
        self.ent_pass.pack(side="left", padx=(0, 10))
        self.ent_pass.bind("<Return>", lambda e: self._desbloquear_terminal())
        
        self.btn_desbloquear = ctk.CTkButton(self.frame_auth, text="Desbloquear", command=self._desbloquear_terminal, fg_color="#1976D2", hover_color="#2196F3", width=100)
        self.btn_desbloquear.pack(side="left")

        # Frame de contenido de la terminal (Oculto por defecto)
        self.frame_term_content = ctk.CTkFrame(self.frame_terminal, fg_color="transparent")
        # No le hacemos pack() aquí para que esté oculto al inicio
        
        self.txt_terminal = ctk.CTkTextbox(self.frame_term_content, height=120, fg_color="#1e1e1e", text_color="#d4d4d4", font=("Consolas", 12))
        self.txt_terminal.pack(pady=(0, 5), fill="x")
        self.txt_terminal.configure(state="disabled")
        
        frame_envio = ctk.CTkFrame(self.frame_term_content, fg_color="transparent")
        frame_envio.pack(pady=(5, 0), fill="x")
        
        self.ent_comando = ctk.CTkEntry(frame_envio, placeholder_text="Escriba un comando...", fg_color="#D3D3D3", text_color="#000000")
        self.ent_comando.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.ent_comando.bind("<Return>", lambda e: self.enviar_comando_manual())
        
        self.cmb_terminador = ctk.CTkComboBox(frame_envio, values=["\\0 (Null)", "\\n (LF)", "\\r (CR)", "\\r\\n (CRLF)", "Ninguno"], width=120, fg_color="#D3D3D3", text_color="#000000")
        self.cmb_terminador.set("\\0 (Null)")
        self.cmb_terminador.pack(side="left", padx=5)
        
        self.btn_enviar_cmd = ctk.CTkButton(frame_envio, text="Enviar", command=self.enviar_comando_manual, width=80, fg_color="#1976D2", hover_color="#2196F3")
        self.btn_enviar_cmd.pack(side="left", padx=5)
        
        self.btn_limpiar_term = ctk.CTkButton(frame_envio, text="Limpiar", command=self.limpiar_terminal, width=80, fg_color="#424242", hover_color="#545454")
        self.btn_limpiar_term.pack(side="left", padx=5)

        self.btn_bloquear = ctk.CTkButton(frame_envio, text="🔒 Bloquear", command=self._bloquear_terminal, width=90, fg_color="#D32F2F", hover_color="#F44336")
        self.btn_bloquear.pack(side="left", padx=5)

    def inicializar_hardware(self):
        # Cargar cámaras
        camaras = self.driver_camara.listar_camaras_disponibles()
        if camaras:
            self.cmb_camaras.configure(values=camaras)
            self.cmb_camaras.set(camaras[0])
            self.cambiar_camara(camaras[0])
        else:
            self.cmb_camaras.configure(values=["Ninguna"])
            self.cmb_camaras.set("Ninguna")

        # Cargar puertos COM y auto-detectar
        puertos = self.driver_serie.listar_puertos()
        if puertos:
            self.cmb_puertos.configure(values=puertos)
            puerto_auto = self.driver_serie.autodetectar_puerto()
            if puerto_auto and puerto_auto in puertos:
                self.cmb_puertos.set(puerto_auto)
                self.driver_serie.conectar(puerto_auto)
            else:
                self.cmb_puertos.set(puertos[0])
                self.driver_serie.conectar(puertos[0])
        else:
            self.cmb_puertos.configure(values=["Ninguno"])
            self.cmb_puertos.set("Ninguno")

    def refrescar_hardware(self):
        logger.info("Refrescando lista de dispositivos...")
        # Desconectar actuales si los hubiera para evitar colisiones
        self.driver_serie.desconectar()
        self.driver_camara.desconectar()
        
        self.cmb_puertos.set("Buscando...")
        self.cmb_camaras.set("Buscando...")
        self.update_idletasks()
        
        self.inicializar_hardware()

    def cambiar_puerto_serie(self, puerto: str):
        if puerto and puerto != "Ninguno" and puerto != "Buscando...":
            self.driver_serie.conectar(puerto)

    def cambiar_camara(self, camara_str: str):
        if "Cámara" in camara_str:
            idx = int(camara_str.replace("Cámara ", ""))
            self.driver_camara.conectar(idx)

    def monitorear_estado(self):
        # Actualiza la interfaz visual de los indicadores
        self.ind_banco.set_estado(self.driver_serie.esta_conectado())
        self.ind_camara.set_estado(self.driver_camara.esta_conectada())
        self.after(500, self.monitorear_estado)

    def _toggle_modo_ini(self):
        if self.var_modo_peso_ini.get(): # Auto
            self.sw_modo_ini.configure(text="A")
            self.ent_peso_ini.configure(state="disabled")
            self.btn_peso_ini.configure(state="normal")
        else: # Manual
            self.sw_modo_ini.configure(text="M")
            self.ent_peso_ini.configure(state="normal")
            self.btn_peso_ini.configure(state="disabled")

    def _toggle_modo_fin(self):
        if self.var_modo_peso_fin.get(): # Auto
            self.sw_modo_fin.configure(text="A")
            self.ent_peso_fin.configure(state="disabled")
            self.btn_peso_fin.configure(state="normal")
        else: # Manual
            self.sw_modo_fin.configure(text="M")
            self.ent_peso_fin.configure(state="normal")
            self.btn_peso_fin.configure(state="disabled")

    def _toggle_modo_tiempo(self):
        if self.var_modo_tiempo.get(): # Auto
            self.sw_modo_tiempo.configure(text="A")
            self.ent_tiempo.configure(state="disabled")
        else: # Manual
            self.sw_modo_tiempo.configure(text="M")
            self.ent_tiempo.configure(state="normal")

    def _validar_numero_flotante(self, valor_nuevo):
        if valor_nuevo == "" or valor_nuevo == "-" or valor_nuevo == "---":
            return True
        try:
            float(valor_nuevo)
            return True
        except ValueError:
            return False

    def _desbloquear_terminal(self):
        pwd = self.ent_pass.get()
        if pwd == PASSWORD_TERMINAL:
            self.frame_auth.pack_forget()
            self.ent_pass.delete(0, "end")
            self.frame_term_content.pack(fill="x", padx=15, pady=(45, 15))
            if hasattr(self.frame_terminal, "lbl_titulo"):
                self.frame_terminal.lbl_titulo.lift()
            self.txt_terminal.see("end")
        else:
            self._mostrar_advertencia("Contraseña incorrecta para desbloquear la terminal.")
            self.ent_pass.delete(0, "end")

    def _bloquear_terminal(self):
        self.frame_term_content.pack_forget()
        self.frame_auth.pack(padx=15, pady=(45, 15), fill="x")

    def _mostrar_advertencia(self, mensaje: str):
        # Actualiza el recuadro de advertencias de forma segura
        def update():
            if hasattr(self, 'var_advertencia'):
                self.var_advertencia.set(mensaje)
        self.after(0, update)

    def cambiar_carpeta_ensayos(self):
        """Abre un diálogo para seleccionar la nueva ruta de ensayos."""
        nueva_ruta = filedialog.askdirectory(title="Seleccionar carpeta de ensayos", initialdir=str(self.gestor.carpeta_base))
        if nueva_ruta:
            self.gestor.cambiar_ruta_base(nueva_ruta)
            logger.info(f"Ruta de ensayos actualizada por el usuario a: {nueva_ruta}")

    # --- Lógica de Terminal ---
    def _on_terminal_data(self, direccion: str, datos: bytes):
        # Asegurarse de ejecutar en el hilo principal
        self.after(0, self._actualizar_terminal, direccion, datos)

    def _actualizar_terminal(self, direccion: str, datos: bytes):
        if hasattr(self, 'txt_terminal'):
            # Formatear caracteres no imprimibles como \0 o \r\n para visualizar
            texto = datos.decode('ascii', errors='replace').replace('\x00', '\\0').replace('\r', '\\r').replace('\n', '\\n\n')
            if not texto.endswith('\n'):
                texto += '\n'
            
            self.txt_terminal.configure(state="normal")
            
            if direccion == "TX":
                # Prefix visualmente distinto para transmisión
                self.txt_terminal.insert("end", f"> TX: {texto}")
            else:
                self.txt_terminal.insert("end", f"< RX: {texto}")
                
            self.txt_terminal.see("end")
            self.txt_terminal.configure(state="disabled")

    def enviar_comando_manual(self):
        cmd = self.ent_comando.get()
        if not cmd:
            return
            
        term_str = self.cmb_terminador.get()
        terminador_tx = b""
        if "\\0" in term_str:
            terminador_tx = b"\x00"
        elif "\\r\\n" in term_str:
            terminador_tx = b"\r\n"
        elif "\\n" in term_str:
            terminador_tx = b"\n"
        elif "\\r" in term_str:
            terminador_tx = b"\r"
        
        # Enviar comando manual con su terminador seleccionado en la UI
        self.driver_serie.enviar_comando_async(cmd, espera_respuesta=True, terminador_tx=terminador_tx)
        self.ent_comando.delete(0, "end")

    def limpiar_terminal(self):
        self.txt_terminal.configure(state="normal")
        self.txt_terminal.delete("1.0", "end")
        self.txt_terminal.configure(state="disabled")

    # --- Lógica de Ensayo ---
    def procesar_respuesta_serie(self, comando: str, respuesta: str):
        # Este callback es llamado por el hilo secundario
        # Usamos .after() para procesar de forma segura en la UI principal
        self.after(0, self._procesar_respuesta_ui, comando, respuesta)

    def _procesar_respuesta_ui(self, comando: str, respuesta: str):
        if not respuesta:
            if comando == "FINALIZAR ENSAYO":
                self.var_modo_tiempo.set(False)
                self._toggle_modo_tiempo()
                self.var_tiempo.set("---")
                self.tiempo_final_val = None
                self._mostrar_advertencia("Timeout recibiendo el tiempo final. Ingrese el tiempo manualmente.")
                self.ensayo_en_curso = False
                self.pendiente_resultados = True
                self.btn_iniciar.configure(state="normal")
            # Si no hay respuesta (timeout o desconexión), liberamos estados
            if hasattr(self, '_esperando_peso_ini'): self._esperando_peso_ini = False
            if hasattr(self, '_esperando_peso_fin'): self._esperando_peso_fin = False
            return
            
        try:
            if comando == "MEDICION BALANZA":
                # Formato xxx.xxx
                peso = float(respuesta)
                
                if self.retorno_en_curso:
                    if peso <= PESO_MINIMO_RETORNO_KG:
                        self.finalizar_retorno()
                        
                # Si fue solicitada manualemente para el inicio o fin
                if hasattr(self, '_esperando_peso_ini') and self._esperando_peso_ini:
                    self.peso_inicial_val = peso
                    self.var_peso_ini.set(f"{peso:.2f}")
                    self._esperando_peso_ini = False
                elif hasattr(self, '_esperando_peso_fin') and self._esperando_peso_fin:
                    self.peso_final_val = peso
                    self.var_peso_fin.set(f"{peso:.2f}")
                    self._esperando_peso_fin = False
                    
            elif comando == "MEDICION RELOJ":
                # Formato xxxx.xxx
                tiempo = float(respuesta)
                self.var_tiempo.set(f"{tiempo:.2f}")
                
                if self.ensayo_en_curso:
                    self._verificar_progreso_ensayo(tiempo)
                    
            elif comando == "FINALIZAR ENSAYO":
                tiempo_total = float(respuesta)
                self.tiempo_final_val = tiempo_total
                # Actualizamos la etiqueta con el tiempo oficial del hardware
                self.var_tiempo.set(f"{tiempo_total:.2f}")
                self.ensayo_en_curso = False
                self.pendiente_resultados = True
                self.btn_iniciar.configure(state="normal")
                logger.info(f"Ensayo finalizado. Tiempo oficial: {tiempo_total}s")
                
        except ValueError:
            logger.error(f"Respuesta inválida para '{comando}': '{respuesta}'")

    def tomar_peso_inicial(self):
        if self.ensayo_en_curso or self.retorno_en_curso: return
        self._esperando_peso_ini = True
        self.driver_serie.enviar_comando_async("MEDICION BALANZA", callback=self.procesar_respuesta_serie)

    def tomar_peso_final(self):
        if self.ensayo_en_curso or self.retorno_en_curso: return
        self._esperando_peso_fin = True
        self.driver_serie.enviar_comando_async("MEDICION BALANZA", callback=self.procesar_respuesta_serie)

    def iniciar_retorno(self):
        if self.ensayo_en_curso or self.retorno_en_curso: return
        self.retorno_en_curso = True
        self.btn_ini_retorno.configure(state="disabled")
        self.btn_fin_retorno.configure(state="normal")
        self.driver_serie.enviar_comando_async("INICIAR RETORNO", espera_respuesta=False)
        self._polling_retorno()

    def _polling_retorno(self):
        if self.retorno_en_curso:
            if getattr(self, '_poll_balanza_activo', False):
                self.after(PERIODO_POLLING_RETORNO_MS, self._polling_retorno)
                return
                
            self._poll_balanza_activo = True
            
            def callback_interno(cmd, resp):
                self._poll_balanza_activo = False
                self.procesar_respuesta_serie(cmd, resp)
                
            self.driver_serie.enviar_comando_async("MEDICION BALANZA", callback=callback_interno)
            self.after(PERIODO_POLLING_RETORNO_MS, self._polling_retorno)

    def finalizar_retorno(self):
        if not self.retorno_en_curso: return
        self.retorno_en_curso = False
        self.btn_ini_retorno.configure(state="normal")
        self.btn_fin_retorno.configure(state="disabled")
        self.driver_serie.enviar_comando_async("FINALIZAR RETORNO", espera_respuesta=False)

    def iniciar_ensayo(self):
        if getattr(self, 'pendiente_resultados', False):
            self._mostrar_advertencia("Debe calcular los resultados del ensayo anterior antes de iniciar uno nuevo.")
            return

        if not self.var_modo_peso_ini.get(): # Modo Manual
            try:
                peso_str = self.var_peso_ini.get().strip()
                if not peso_str or peso_str == "---":
                    raise ValueError
                self.peso_inicial_val = float(peso_str)
            except ValueError:
                logger.warning("No se puede iniciar ensayo sin peso inicial válido.")
                return

        if self.peso_inicial_val is None:
            logger.warning("No se puede iniciar ensayo sin peso inicial.")
            # Aquí idealmente se mostraría un popup, pero registramos en log.
            return
            
        try:
            self.tiempo_ensayo_objetivo = float(self.ent_duracion.get())
            densidad = float(self.ent_densidad.get())
            if self.tiempo_ensayo_objetivo <= 0 or densidad <= 0:
                raise ValueError
        except ValueError:
            logger.error("Duración o densidad inválidas.")
            return

        self.ensayo_en_curso = True
        self.fotos_tomadas = 0
        self.panel_img.reiniciar_panel()
        self.btn_iniciar.configure(state="disabled")
        
        # Limpiar resultados visuales del ensayo anterior
        self.peso_final_val = None
        self.tiempo_final_val = None
        self.var_peso_fin.set("---")
        self.var_peso_neto.set("---")
        self.var_c_masico.set("---")
        self.var_c_volumetrico.set("---")
        self.var_tiempo.set("0.00")
        
        self.gestor.iniciar_nuevo_ensayo()
        self.driver_serie.enviar_comando_async("INICIAR ENSAYO", espera_respuesta=False)
        
        # Tomar primera foto en T=0
        self._capturar_y_mostrar_foto()
        
        self.tiempo_inicio_ensayo_pc = time.perf_counter()
        self._verificar_progreso_ensayo_pc()

    def _verificar_progreso_ensayo_pc(self):
        if not self.ensayo_en_curso:
            return
            
        tiempo_transcurrido = time.perf_counter() - self.tiempo_inicio_ensayo_pc
        
        # Actualizar visualmente el tiempo
        self.var_tiempo.set(f"{tiempo_transcurrido:.2f}")
        
        # Verificar si hay que tomar foto
        siguiente_objetivo = self.fotos_tomadas * (self.tiempo_ensayo_objetivo / 5.0)
        if tiempo_transcurrido >= siguiente_objetivo and self.fotos_tomadas <= 5:
            self._capturar_y_mostrar_foto()

        if tiempo_transcurrido >= self.tiempo_ensayo_objetivo:
            # Asegurar la última foto
            if self.fotos_tomadas <= 5:
                self._capturar_y_mostrar_foto()
                
            # Fin del ensayo, solicitar tiempo oficial
            self.driver_serie.enviar_comando_async("FINALIZAR ENSAYO", callback=self.procesar_respuesta_serie)
        else:
            self.after(50, self._verificar_progreso_ensayo_pc)

    def _capturar_y_mostrar_foto(self):
        if self.fotos_tomadas >= 6: return
        
        idx_foto = self.fotos_tomadas
        ruta = self.gestor.obtener_ruta_siguiente_imagen()
        self.fotos_tomadas += 1
        
        def on_foto_tomada(exito, ruta_guardada):
            if exito:
                self.after(0, self.panel_img.actualizar_imagen, idx_foto, ruta_guardada)
                
        self.driver_camara.tomar_foto(ruta, callback=on_foto_tomada)

    def calcular_caudales(self):
        if not self.var_modo_tiempo.get(): # Modo Manual
            try:
                tiempo_str = self.var_tiempo.get().strip()
                if not tiempo_str or tiempo_str == "---":
                    raise ValueError
                self.tiempo_final_val = float(tiempo_str)
            except ValueError:
                logger.warning("Faltan datos (tiempo manual) para calcular caudal.")
                return

        if not self.var_modo_peso_fin.get(): # Modo Manual
            try:
                peso_str = self.var_peso_fin.get().strip()
                if not peso_str or peso_str == "---":
                    raise ValueError
                self.peso_final_val = float(peso_str)
            except ValueError:
                logger.warning("Faltan datos (peso final manual) para calcular caudal.")
                return

        if self.peso_inicial_val is None or self.peso_final_val is None or self.tiempo_final_val is None:
            logger.warning("Faltan datos para calcular caudal.")
            return
            
        try:
            densidad = float(self.ent_densidad.get())
            peso_neto = self.peso_final_val - self.peso_inicial_val
            c_masico = calcular_caudal_masico(self.peso_inicial_val, self.peso_final_val, self.tiempo_final_val)
            c_vol = calcular_caudal_volumetrico(self.peso_inicial_val, self.peso_final_val, self.tiempo_final_val, densidad)
            
            self.var_peso_neto.set(f"{peso_neto:.2f}")
            self.var_c_masico.set(f"{c_masico:.2f}")
            self.var_c_volumetrico.set(f"{c_vol:.2f}")
            
            # Guardar reporte
            self.gestor.registrar_dato("Tiempo de ensayo [s]", f"{self.tiempo_final_val:.3f}")
            self.gestor.registrar_dato("Peso inicial [kg]", f"{self.peso_inicial_val:.3f}")
            self.gestor.registrar_dato("Peso final [kg]", f"{self.peso_final_val:.3f}")
            self.gestor.registrar_dato("Peso neto [kg]", f"{peso_neto:.3f}")
            self.gestor.registrar_dato("Caudal másico [kg/s]", f"{c_masico:.4f}")
            self.gestor.registrar_dato("Caudal volumétrico [m3/s]", f"{c_vol:.6f}")
            self.gestor.registrar_dato("Densidad [kg/m3]", f"{densidad:.3f}")
            self.gestor.guardar_reporte_csv()
            
            self.pendiente_resultados = False
            self.peso_inicial_val = None
            self.var_peso_ini.set("---")
            
        except Exception as e:
            logger.error(f"Error calculando caudal: {e}")
