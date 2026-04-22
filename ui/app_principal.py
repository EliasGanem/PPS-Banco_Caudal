import customtkinter as ctk
import logging
from typing import Optional
from ui.componentes_ui import IndicadorConexion, PanelImagenes
from drivers.comunicacion_serie import ComunicacionSerie
from drivers.camara_usb import CamaraUSB
from core.gestor_ensayo import GestorEnsayo
from core.calculador_caudal import calcular_caudal_masico, calcular_caudal_volumetrico

logger = logging.getLogger(__name__)

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
        self.tiempo_ensayo_objetivo = 10.0
        self.fotos_tomadas = 0
        self.peso_inicial_val: Optional[float] = None
        self.peso_final_val: Optional[float] = None
        self.tiempo_final_val: Optional[float] = None
        
        self.construir_ui()
        self.inicializar_hardware()
        self.monitorear_estado()

    def construir_ui(self):
        # --- Frame Configuración ---
        self.frame_config = ctk.CTkFrame(self)
        self.frame_config.pack(padx=20, pady=10, fill="x")
        
        self.lbl_titulo_config = ctk.CTkLabel(self.frame_config, text="Configuración de Puertos", font=("Inter", 16, "bold"))
        self.lbl_titulo_config.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.cmb_puertos = ctk.CTkComboBox(self.frame_config, values=["Buscando..."], command=self.cambiar_puerto_serie)
        self.cmb_puertos.grid(row=1, column=0, padx=10, pady=5)
        
        self.cmb_camaras = ctk.CTkComboBox(self.frame_config, values=["Buscando..."], command=self.cambiar_camara)
        self.cmb_camaras.grid(row=1, column=1, padx=10, pady=5)
        
        self.ind_banco = IndicadorConexion(self.frame_config, "Conexión Banco")
        self.ind_banco.grid(row=1, column=2, padx=20, pady=5)
        
        self.ind_camara = IndicadorConexion(self.frame_config, "Conexión Cámara")
        self.ind_camara.grid(row=1, column=3, padx=20, pady=5)

        # --- Contenedor Medio ---
        self.frame_medio = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_medio.pack(padx=20, pady=10, fill="x")
        self.frame_medio.grid_columnconfigure(0, weight=1)
        self.frame_medio.grid_columnconfigure(1, weight=1)

        # Parámetros Ensayo
        self.frame_params = ctk.CTkFrame(self.frame_medio)
        self.frame_params.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        
        ctk.CTkLabel(self.frame_params, text="Parámetros Ensayo", font=("Inter", 16, "bold")).pack(pady=5)
        
        frame_duracion = ctk.CTkFrame(self.frame_params, fg_color="transparent")
        frame_duracion.pack(pady=5, fill="x", padx=10)
        ctk.CTkLabel(frame_duracion, text="Duración Ensayo (s):").pack(side="left")
        self.ent_duracion = ctk.CTkEntry(frame_duracion)
        self.ent_duracion.insert(0, "10.0")
        self.ent_duracion.pack(side="right")
        
        frame_densidad = ctk.CTkFrame(self.frame_params, fg_color="transparent")
        frame_densidad.pack(pady=5, fill="x", padx=10)
        ctk.CTkLabel(frame_densidad, text="Densidad (kg/m³):").pack(side="left")
        self.ent_densidad = ctk.CTkEntry(frame_densidad)
        self.ent_densidad.insert(0, "998.0")
        self.ent_densidad.pack(side="right")

        self.btn_iniciar = ctk.CTkButton(self.frame_params, text="Iniciar Ensayo", command=self.iniciar_ensayo, height=40, font=("Inter", 16, "bold"), fg_color="#2c6b3c", hover_color="#3b8c4f")
        self.btn_iniciar.pack(pady=15, padx=20, fill="x")

        # Resultados y Botones Operativos
        self.frame_resultados = ctk.CTkFrame(self.frame_medio)
        self.frame_resultados.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        
        ctk.CTkLabel(self.frame_resultados, text="Mediciones y Resultados", font=("Inter", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=5)
        
        # Botones para mediciones manuales
        frame_botones_med = ctk.CTkFrame(self.frame_resultados, fg_color="transparent")
        frame_botones_med.grid(row=1, column=0, columnspan=2, pady=5)
        self.btn_peso_ini = ctk.CTkButton(frame_botones_med, text="Tomar Peso Inicial", command=self.tomar_peso_inicial)
        self.btn_peso_ini.pack(side="left", padx=5)
        self.btn_peso_fin = ctk.CTkButton(frame_botones_med, text="Tomar Peso Final", command=self.tomar_peso_final)
        self.btn_peso_fin.pack(side="left", padx=5)
        self.btn_calcular = ctk.CTkButton(frame_botones_med, text="Calcular Caudal", command=self.calcular_caudales)
        self.btn_calcular.pack(side="left", padx=5)

        # Variables para mostrar resultados
        self.var_tiempo = ctk.StringVar(value="Tiempo: 0.0 s")
        self.var_balanza = ctk.StringVar(value="Balanza: 0.000 kg")
        self.var_peso_ini = ctk.StringVar(value="Peso Inicial: ---")
        self.var_peso_fin = ctk.StringVar(value="Peso Final: ---")
        self.var_peso_neto = ctk.StringVar(value="Peso Neto: ---")
        self.var_c_masico = ctk.StringVar(value="C. Másico: ---")
        self.var_c_volumetrico = ctk.StringVar(value="C. Volumétrico: ---")

        # Grilla de resultados
        row_res = 2
        for var in [self.var_tiempo, self.var_balanza, self.var_peso_ini, self.var_peso_fin, 
                    self.var_peso_neto, self.var_c_masico, self.var_c_volumetrico]:
            ctk.CTkLabel(self.frame_resultados, textvariable=var, font=("Inter", 14)).grid(row=row_res, column=0, columnspan=2, pady=2, sticky="w", padx=20)
            row_res += 1

        # --- Panel de Imágenes ---
        self.frame_imagenes = ctk.CTkFrame(self)
        self.frame_imagenes.pack(padx=20, pady=10, fill="both", expand=True)
        ctk.CTkLabel(self.frame_imagenes, text="Secuencia de Imágenes del Ensayo", font=("Inter", 16, "bold")).pack(anchor="w", padx=10, pady=5)
        self.panel_img = PanelImagenes(self.frame_imagenes)
        self.panel_img.pack(fill="both", expand=True, padx=10, pady=5)

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

    # --- Lógica de Ensayo ---
    def procesar_respuesta_serie(self, comando: str, respuesta: str):
        # Este callback es llamado por el hilo secundario
        # Usamos .after() para procesar de forma segura en la UI principal
        self.after(0, self._procesar_respuesta_ui, comando, respuesta)

    def _procesar_respuesta_ui(self, comando: str, respuesta: str):
        if not respuesta:
            return
            
        try:
            if comando == "MEDICION BALANZA":
                # Formato xxx.xxx
                peso = float(respuesta)
                self.var_balanza.set(f"Balanza: {peso:.3f} kg")
                
                # Si fue solicitada manualemente para el inicio o fin
                if hasattr(self, '_esperando_peso_ini') and self._esperando_peso_ini:
                    self.peso_inicial_val = peso
                    self.var_peso_ini.set(f"Peso Inicial: {peso:.3f} kg")
                    self._esperando_peso_ini = False
                elif hasattr(self, '_esperando_peso_fin') and self._esperando_peso_fin:
                    self.peso_final_val = peso
                    self.var_peso_fin.set(f"Peso Final: {peso:.3f} kg")
                    self._esperando_peso_fin = False
                    
            elif comando == "MEDICION RELOJ":
                # Formato xxxx.xxx
                tiempo = float(respuesta)
                self.var_tiempo.set(f"Tiempo: {tiempo:.3f} s")
                
                if self.ensayo_en_curso:
                    self._verificar_progreso_ensayo(tiempo)
                    
            elif comando == "FINALIZAR ENSAYO":
                tiempo_total = float(respuesta)
                self.tiempo_final_val = tiempo_total
                self.var_tiempo.set(f"Tiempo Total: {tiempo_total:.3f} s")
                self.ensayo_en_curso = False
                self.btn_iniciar.configure(state="normal")
                logger.info(f"Ensayo finalizado. Tiempo: {tiempo_total}s")
                
        except ValueError:
            logger.error(f"Respuesta inválida para '{comando}': '{respuesta}'")

    def tomar_peso_inicial(self):
        if self.ensayo_en_curso: return
        self._esperando_peso_ini = True
        self.driver_serie.enviar_comando_async("MEDICION BALANZA", callback=self.procesar_respuesta_serie)

    def tomar_peso_final(self):
        if self.ensayo_en_curso: return
        self._esperando_peso_fin = True
        self.driver_serie.enviar_comando_async("MEDICION BALANZA", callback=self.procesar_respuesta_serie)

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
        
        # Iniciar ciclo de polling del reloj
        self._polling_reloj()

    def _polling_reloj(self):
        if self.ensayo_en_curso:
            self.driver_serie.enviar_comando_async("MEDICION RELOJ", callback=self.procesar_respuesta_serie)
            self.after(100, self._polling_reloj)

    def _verificar_progreso_ensayo(self, tiempo_actual: float):
        # Verificar si hay que tomar foto
        # Si fotos_tomadas es N, la siguiente debe tomarse en N * (Tiempo_Objetivo / 5)
        # La 1ra (0) ya se tomó al inicio. La 6ta (5) se toma al final.
        siguiente_objetivo = self.fotos_tomadas * (self.tiempo_ensayo_objetivo / 5.0)
        
        if tiempo_actual >= siguiente_objetivo and self.fotos_tomadas <= 5:
            self._capturar_y_mostrar_foto()

        if tiempo_actual >= self.tiempo_ensayo_objetivo:
            self.driver_serie.enviar_comando_async("FINALIZAR ENSAYO", callback=self.procesar_respuesta_serie)
            # Asegurar la última foto
            if self.fotos_tomadas <= 5:
                self._capturar_y_mostrar_foto()

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
            
            self.var_peso_neto.set(f"Peso Neto: {peso_neto:.3f} kg")
            self.var_c_masico.set(f"C. Másico: {c_masico:.4f} kg/s")
            self.var_c_volumetrico.set(f"C. Volumétrico: {c_vol:.6f} m³/s")
            
            # Guardar reporte
            self.gestor.registrar_dato("Tiempo Total [s]", f"{self.tiempo_final_val:.3f}")
            self.gestor.registrar_dato("Peso Inicial [kg]", f"{self.peso_inicial_val:.3f}")
            self.gestor.registrar_dato("Peso Final [kg]", f"{self.peso_final_val:.3f}")
            self.gestor.registrar_dato("Peso Neto [kg]", f"{peso_neto:.3f}")
            self.gestor.registrar_dato("Caudal Másico [kg/s]", f"{c_masico:.4f}")
            self.gestor.registrar_dato("Caudal Volumétrico [m^3/s]", f"{c_vol:.6f}")
            self.gestor.guardar_reporte_csv()
            
        except Exception as e:
            logger.error(f"Error calculando caudal: {e}")
