import customtkinter as ctk
import logging
import time
from typing import Optional
from ui.componentes_ui import IndicadorConexion, PanelImagenes, ContenedorConTitulo
from drivers.comunicacion_serie import ComunicacionSerie
from drivers.camara_usb import CamaraUSB
from core.gestor_ensayo import GestorEnsayo
from core.calculador_caudal import calcular_caudal_masico, calcular_caudal_volumetrico

logger = logging.getLogger(__name__)

# Macros configurables para el retorno
DURACION_ENSAYO_POR_DEFECTO_S = 10.0
PERIODO_POLLING_RETORNO_MS = 1000
PESO_MINIMO_RETORNO_KG = 5.0

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
        
        self.construir_ui()
        
        # Registrar el callback para la terminal serie
        self.driver_serie.set_terminal_callback(self._on_terminal_data)
        
        self.inicializar_hardware()
        self.monitorear_estado()

    def construir_ui(self):
        self.configure(fg_color="#242424")
        
        # --- Bloque 1: Configuración de Puertos ---
        self.frame_config = ContenedorConTitulo(self, titulo="Configuración de Puertos")
        self.frame_config.pack(padx=20, pady=(15, 5), fill="x")
        
        self.lbl_banco = ctk.CTkLabel(self.frame_config, text="Banco de Caudal", font=("Inter", 14), text_color="#FFFFFF")
        self.lbl_banco.grid(row=0, column=0, padx=(15, 5), pady=15, sticky="w")
        
        self.cmb_puertos = ctk.CTkComboBox(self.frame_config, values=["Buscando..."], fg_color="#D3D3D3", text_color="#000000")
        self.cmb_puertos.configure(command=self.cambiar_puerto_serie)
        self.cmb_puertos.grid(row=0, column=1, padx=(0, 10), pady=15)
        
        self.ind_banco = IndicadorConexion(self.frame_config, "")
        self.ind_banco.grid(row=0, column=2, padx=(0, 20), pady=15)
        
        self.lbl_camara = ctk.CTkLabel(self.frame_config, text="Cámara", font=("Inter", 14), text_color="#FFFFFF")
        self.lbl_camara.grid(row=0, column=3, padx=(20, 5), pady=15, sticky="w")
        
        self.cmb_camaras = ctk.CTkComboBox(self.frame_config, values=["Buscando..."], fg_color="#D3D3D3", text_color="#000000")
        self.cmb_camaras.configure(command=self.cambiar_camara)
        self.cmb_camaras.grid(row=0, column=4, padx=(0, 10), pady=15)
        
        self.ind_camara = IndicadorConexion(self.frame_config, "")
        self.ind_camara.grid(row=0, column=5, padx=(0, 20), pady=15)
        
        self.btn_refrescar = ctk.CTkButton(self.frame_config, text="🔄", width=40, font=("Inter", 18), fg_color="#1976D2", hover_color="#2196F3", command=self.refrescar_hardware)
        self.btn_refrescar.grid(row=0, column=6, padx=(10, 15), pady=15)

        # Variables para mostrar resultados
        self.var_tiempo = ctk.StringVar(value="0.00")
        self.var_peso_ini = ctk.StringVar(value="---")
        self.var_peso_fin = ctk.StringVar(value="---")
        self.var_peso_neto = ctk.StringVar(value="---")
        self.var_c_masico = ctk.StringVar(value="---")
        self.var_c_volumetrico = ctk.StringVar(value="---")

        # --- Bloque 2: Panel Central ---
        self.frame_medio = ctk.CTkFrame(self, fg_color="transparent")
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
        self.ent_duracion = ctk.CTkEntry(frame_inputs, fg_color="#D3D3D3", text_color="#000000")
        self.ent_duracion.insert(0, str(DURACION_ENSAYO_POR_DEFECTO_S))
        self.ent_duracion.grid(row=1, column=0, padx=(0, 5), sticky="ew")
        
        lbl_den = ctk.CTkLabel(frame_inputs, text="Densidad del Fluido [kg/m³]", text_color="#FFFFFF")
        lbl_den.grid(row=0, column=1, sticky="w")
        self.ent_densidad = ctk.CTkEntry(frame_inputs, fg_color="#D3D3D3", text_color="#000000")
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
        self.frame_med_inner.pack(padx=15, pady=20, fill="both", expand=True)
        self.frame_med_inner.grid_columnconfigure(1, weight=1)
        
        self.btn_peso_ini = ctk.CTkButton(self.frame_med_inner, text="Peso Inicial [kg]", command=self.tomar_peso_inicial, fg_color="#424242", hover_color="#545454", width=120)
        self.btn_peso_ini.grid(row=0, column=0, pady=10, sticky="w")
        ent_peso_ini = ctk.CTkEntry(self.frame_med_inner, textvariable=self.var_peso_ini, state="disabled", fg_color="#D3D3D3", text_color="#000000", width=80)
        ent_peso_ini.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        
        self.btn_peso_fin = ctk.CTkButton(self.frame_med_inner, text="Peso Final [kg]", command=self.tomar_peso_final, fg_color="#424242", hover_color="#545454", width=120)
        self.btn_peso_fin.grid(row=1, column=0, pady=10, sticky="w")
        ent_peso_fin = ctk.CTkEntry(self.frame_med_inner, textvariable=self.var_peso_fin, state="disabled", fg_color="#D3D3D3", text_color="#000000", width=80)
        ent_peso_fin.grid(row=1, column=1, padx=10, pady=10, sticky="e")
        
        # Columna 3: Resultados
        self.frame_resultados = ctk.CTkFrame(self.frame_medio, fg_color="#2b2b2b", border_width=1, border_color="#555555", corner_radius=8)
        self.frame_resultados.grid(row=0, column=2, padx=(10, 0), sticky="nsew")
        
        self.btn_calcular = ctk.CTkButton(self.frame_resultados, text="Resultados", command=self.calcular_caudales, fg_color="#388E3C", hover_color="#4CAF50", corner_radius=0, font=("Inter", 16, "bold"))
        self.btn_calcular.pack(fill="x", pady=(0, 10))
        
        frame_res_grid = ctk.CTkFrame(self.frame_resultados, fg_color="transparent")
        frame_res_grid.pack(padx=15, pady=5, fill="both", expand=True)
        frame_res_grid.grid_columnconfigure(1, weight=1)
        
        labels_res = ["Tiempo [s]", "Peso Neto [kg]", "Caudal Másico [kg/s]", "Caudal Volumétrico [m³/s]"]
        vars_res = [self.var_tiempo, self.var_peso_neto, self.var_c_masico, self.var_c_volumetrico]
        
        for i, (lbl_txt, var) in enumerate(zip(labels_res, vars_res)):
            ctk.CTkLabel(frame_res_grid, text=lbl_txt, text_color="#FFFFFF").grid(row=i, column=0, pady=4, sticky="w")
            ent = ctk.CTkEntry(frame_res_grid, textvariable=var, state="disabled", fg_color="#D3D3D3", text_color="#000000", width=80)
            ent.grid(row=i, column=1, padx=(10, 0), pady=4, sticky="e")

        # --- Bloque 3: Imágenes del Ensayo ---
        self.frame_imagenes = ContenedorConTitulo(self, titulo="Imágenes del Ensayo")
        self.frame_imagenes.pack(padx=20, pady=(5, 5), fill="both", expand=True)
        self.panel_img = PanelImagenes(self.frame_imagenes)
        self.panel_img.pack(fill="both", expand=True, padx=10, pady=15)

        # --- Bloque 4: Terminal ---
        self.frame_terminal = ContenedorConTitulo(self, titulo="Terminal")
        self.frame_terminal.pack(padx=20, pady=(5, 15), fill="x")
        
        self.txt_terminal = ctk.CTkTextbox(self.frame_terminal, height=120, fg_color="#1e1e1e", text_color="#d4d4d4", font=("Consolas", 12))
        self.txt_terminal.pack(padx=15, pady=(20, 5), fill="x")
        self.txt_terminal.configure(state="disabled")
        
        frame_envio = ctk.CTkFrame(self.frame_terminal, fg_color="transparent")
        frame_envio.pack(padx=15, pady=(5, 15), fill="x")
        
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
            
        except Exception as e:
            logger.error(f"Error calculando caudal: {e}")
