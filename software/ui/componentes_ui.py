import customtkinter as ctk
from PIL import Image
import os
import logging

logger = logging.getLogger(__name__)

class ContenedorConTitulo(ctk.CTkFrame):
    def __init__(self, master, titulo: str, **kwargs):
        super().__init__(master, fg_color="#2b2b2b", border_width=1, border_color="#555555", corner_radius=8, **kwargs)
        # Añadir un margen interno superior para dejar lugar al título
        self.lbl_titulo = ctk.CTkLabel(self, text=titulo, font=("Inter", 14, "bold"), text_color="#FFFFFF", fg_color="#2b2b2b")
        self.lbl_titulo.place(x=15, y=8) # Ubicamos el texto adentro para evitar que se recorte


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
        self.labels_textos = []
        
        for i in range(6):
            frame_img = ctk.CTkFrame(self, fg_color="transparent")
            frame_img.grid(row=0, column=i, padx=5, pady=5)
            
            # Placeholder gris claro con un ícono unicode de cámara 📷 o simplemente gris
            lbl = ctk.CTkLabel(frame_img, text="📷", font=("Inter", 40), text_color="#555555", width=120, height=120, corner_radius=8, fg_color="#e0e0e0")
            lbl.pack(pady=(0, 5))
            
            lbl_texto = ctk.CTkLabel(frame_img, text=f"Imagen {i+1}", font=("Inter", 12), text_color="#FFFFFF")
            lbl_texto.pack()
            
            self.labels_imagenes.append(lbl)
            self.labels_textos.append(lbl_texto)
            
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
            self.labels_imagenes[i].configure(image="", text="---")

class ToolTip:
    """Clase simple para mostrar tooltips al pasar el mouse por un widget."""
    def __init__(self, widget, text_func):
        self.widget = widget
        self.text_func = text_func
        self.tipwindow = None
        self.id = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(500, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tipwindow = tw = ctk.CTkToplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = ctk.CTkLabel(tw, text=self.text_func(), justify="left",
                             fg_color="#333333", text_color="#FFFFFF", corner_radius=4)
        label.pack(ipadx=10, ipady=5)
    
    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()
