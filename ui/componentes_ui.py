import customtkinter as ctk
from PIL import Image
import os
import logging

logger = logging.getLogger(__name__)

class IndicadorConexion(ctk.CTkFrame):
    def __init__(self, master, texto: str, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.label = ctk.CTkLabel(self, text=texto, font=("Inter", 16))
        self.label.pack(side="left", padx=(0, 10))
        
        self.canvas = ctk.CTkCanvas(self, width=20, height=20, bg="#2b2b2b", highlightthickness=0)
        self.canvas.pack(side="left")
        
        # Color rojo apagado por defecto
        self.ovalo = self.canvas.create_oval(2, 2, 18, 18, fill="#5c1c1c", outline="#111111")
        
    def set_estado(self, conectado: bool):
        """Actualiza el color del indicador."""
        if conectado:
            self.canvas.itemconfig(self.ovalo, fill="#32CD32") # Verde brillante
        else:
            self.canvas.itemconfig(self.ovalo, fill="#5c1c1c") # Rojo oscuro

class PanelImagenes(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(list(range(6)), weight=1)
        self.labels_imagenes = []
        
        for i in range(6):
            lbl = ctk.CTkLabel(self, text=f"Captura {i+1}", width=120, height=120, 
                               corner_radius=8, fg_color="#3b3b3b")
            lbl.grid(row=0, column=i, padx=5, pady=5)
            self.labels_imagenes.append(lbl)
            
    def actualizar_imagen(self, indice: int, ruta_imagen: str):
        """Carga y muestra una imagen en el recuadro especificado."""
        if 0 <= indice < 6 and os.path.exists(ruta_imagen):
            try:
                img = Image.open(ruta_imagen)
                img_ctk = ctk.CTkImage(light_image=img, dark_image=img, size=(120, 120))
                self.labels_imagenes[indice].configure(image=img_ctk, text="")
            except Exception as e:
                logger.error(f"Error cargando imagen en UI: {e}")

    def reiniciar_panel(self):
        """Limpia las imágenes para un nuevo ensayo."""
        for i in range(6):
            self.labels_imagenes[i].configure(image="", text=f"Captura {i+1}")
