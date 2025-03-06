import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime

# Importar módulos refactorizados (ajustar según necesidad)
from core.xml_processor import XMLProcessor
from core.document_generator import DocumentGenerator
from utils.file_utils import FileUtils
from ui.date_selector import DateSelector
from utils.formatters import convert_fecha_to_texto

class DocumentosXMLApp:
    def __init__(self, root):
        """
        Inicializa la aplicación para generar documentos desde XML.
        
        Args:
            root: Ventana principal de Tkinter
        """
        self.root = root
        self.root.title("Generador de Documentos desde XML")
        self.root.geometry("800x700")
        
        # Inicializar componentes
        self.xml_processor = XMLProcessor()
        self.document_generator = DocumentGenerator()
        self.file_utils = FileUtils()
        
        # Crear la interfaz
        self.create_widgets()
    
    def create_widgets(self):
        """Crea y configura todos los widgets de la interfaz de usuario."""
        # Configurar grid
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, minsize=120)
        
        # ==== SECCIÓN DE SELECCIÓN DE ARCHIVO XML ====
        self._create_xml_file_selection_section()
        
        # Separador
        ttk.Separator(self.root, orient='horizontal').grid(row=1, column=0, columnspan=3, sticky='ew', pady=10)
        
        # ==== SECCIÓN DE INFORMACIÓN DEL DOCUMENTO ====
        self._create_document_info_section()
        
        # Separador
        ttk.Separator(self.root, orient='horizontal').grid(row=8, column=0, columnspan=3, sticky='ew', pady=10)
        
        # ==== SECCIÓN DE INFORMACIÓN DEL PERSONAL ====
        self._create_personnel_section()
        
        # Separador
        ttk.Separator(self.root, orient='horizontal').grid(row=13, column=0, columnspan=3, sticky='ew', pady=10)
        
        # ==== SECCIÓN DE PROGRESO Y PROCESAMIENTO ====
        self._create_progress_section()
        
        # ==== SECCIÓN DE REGISTRO DE ACTIVIDAD ====
        self._create_activity_log_section()
    
    def _create_xml_file_selection_section(self):
        """Crea la sección para seleccionar el archivo XML."""
        tk.Label(self.root, text="Archivo XML de Factura:", anchor='w').grid(row=0, column=0, padx=10, pady=5, sticky='ew')
        self.entry_ruta_xml = tk.Entry(self.root, width=50)
        self.entry_ruta_xml.grid(row=0, column=1, padx=10, pady=5, sticky='ew')
        tk.Button(self.root, text="Seleccionar", command=self.seleccionar_archivo_xml).grid(row=0, column=2, padx=10, pady=5)
    
    def _create_document_info_section(self):
        """Crea la sección de información del documento."""
        tk.Label(self.root, text="Información del Documento", font=('Helvetica', 10, 'bold')).grid(row=2, column=0, columnspan=3, sticky='w', padx=5)
        
        # Número de mensaje
        tk.Label(self.root, text="Número de mensaje de asignación:", anchor='w').grid(row=3, column=0, padx=10, pady=5, sticky='ew')
        self.entry_numero_mensaje = tk.Entry(self.root)
        self.entry_numero_mensaje.grid(row=3, column=1, padx=10, pady=5, sticky='ew')
        
        # Fecha del mensaje
        tk.Label(self.root, text="Fecha del mensaje de asignación:", anchor='w').grid(row=4, column=0, padx=10, pady=5, sticky='ew')
        self.entry_fecha_mensaje = tk.Entry(self.root)
        self.entry_fecha_mensaje.grid(row=4, column=1, padx=10, pady=5, sticky='ew')
        tk.Button(self.root, text="Seleccionar", command=lambda: self.seleccionar_fecha(self.entry_fecha_mensaje)).grid(row=4, column=2, padx=10, pady=5)
        
        # Monto asignado
        tk.Label(self.root, text="Monto asignado:", anchor='w').grid(row=5, column=0, padx=10, pady=5, sticky='ew')
        self.entry_monto_asignado = tk.Entry(self.root)
        self.entry_monto_asignado.grid(row=5, column=1, padx=10, pady=5, sticky='ew')
        
        # Fecha del documento
        tk.Label(self.root, text="Fecha de elaboración del documento:", anchor='w').grid(row=6, column=0, padx=10, pady=5, sticky='ew')
        self.entry_fecha_elaboracion = tk.Entry(self.root)
        self.entry_fecha_elaboracion.grid(row=6, column=1, padx=10, pady=5, sticky='ew')
        tk.Button(self.root, text="Seleccionar", command=lambda: self.seleccionar_fecha(self.entry_fecha_elaboracion)).grid(row=6, column=2, padx=10, pady=5)
        
        # Mes asignado
        tk.Label(self.root, text="Mes de comprobación:", anchor='w').grid(row=7, column=0, padx=10, pady=5, sticky='ew')
        self.combo_mes_comprobacion = tk.StringVar(self.root)
        meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", 
                "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
        self.combo_mes_comprobacion.set(meses[datetime.now().month - 1])  # Mes actual como predeterminado
        option_menu_meses = tk.OptionMenu(self.root, self.combo_mes_comprobacion, *meses)
        option_menu_meses.grid(row=7, column=1, padx=10, pady=5, sticky='ew')
    
    def _create_personnel_section(self):
        """Crea la sección de información del personal."""
        tk.Label(self.root, text="Información del Personal", font=('Helvetica', 10, 'bold')).grid(row=9, column=0, columnspan=3, sticky='w', padx=5)
        
        # Define el personal estructurado
        self.lista_personal_recibe = [
            {
                'Grado_recibio_la_compra': "Cap. Enc. Tptes", 
                'Nombre_recibio_la_compra': "Juan Pérez Rodríguez",
                'Matricula_recibio_la_compra': "123456"
            },
            {
                'Grado_recibio_la_compra': "Tte. Adm.", 
                'Nombre_recibio_la_compra': "María Gómez López",
                'Matricula_recibio_la_compra': "234567"
            },
            {
                'Grado_recibio_la_compra': "Sgto. Log.", 
                'Nombre_recibio_la_compra': "Carlos López Martínez",
                'Matricula_recibio_la_compra': "345678"
            }
        ]
        
        self.lista_personal_visto_bueno = [
            {
                'Grado_Vo_Bo': "Cor. Inf.", 
                'Nombre_Vo_Bo': "Roberto Sánchez Torres",
                'Matricula_Vo_Bo': "456789"
            },
            {
                'Grado_Vo_Bo': "Myr. Art.", 
                'Nombre_Vo_Bo': "Patricia Navarro Ruiz",
                'Matricula_Vo_Bo': "567890"
            },
            {
                'Grado_Vo_Bo': "Cap. San.", 
                'Nombre_Vo_Bo': "Fernando Jiménez Castro",
                'Matricula_Vo_Bo': "678901"
            }
        ]
        
        # Persona que recibe la compra
        tk.Label(self.root, text="Recibió la compra:", anchor='w').grid(row=10, column=0, padx=10, pady=5, sticky='ew')
        self.indice_persona_recibe = tk.IntVar(self.root, value=0)
        
        # Crear descripciones para mostrar en el menú
        etiquetas_personal_recibe = []
        for persona in self.lista_personal_recibe:
            etiqueta = f"{persona['Grado_recibio_la_compra']} {persona['Nombre_recibio_la_compra']} ({persona['Matricula_recibio_la_compra']})"
            etiquetas_personal_recibe.append(etiqueta)
        
        # Función para actualizar el índice cuando se selecciona una opción
        def al_seleccionar_receptor(*args):
            self.mostrar_info_personal_seleccionado()
        
        dropdown_receptor = tk.OptionMenu(self.root, self.indice_persona_recibe, 
                                           *range(len(etiquetas_personal_recibe)), 
                                           command=al_seleccionar_receptor)
        dropdown_receptor.grid(row=10, column=1, padx=10, pady=5, sticky='ew')
        
        # Actualizar el texto del menú
        menu = dropdown_receptor['menu']
        menu.delete(0, 'end')
        for i, etiqueta in enumerate(etiquetas_personal_recibe):
            menu.add_command(label=etiqueta, 
                            command=tk._setit(self.indice_persona_recibe, i, al_seleccionar_receptor))
        
        # Persona que da visto bueno
        tk.Label(self.root, text="Visto bueno:", anchor='w').grid(row=11, column=0, padx=10, pady=5, sticky='ew')
        self.indice_persona_visto_bueno = tk.IntVar(self.root, value=0)
        
        # Crear descripciones para mostrar en el menú
        etiquetas_personal_visto_bueno = []
        for persona in self.lista_personal_visto_bueno:
            etiqueta = f"{persona['Grado_Vo_Bo']} {persona['Nombre_Vo_Bo']} ({persona['Matricula_Vo_Bo']})"
            etiquetas_personal_visto_bueno.append(etiqueta)
        
        # Función para actualizar el índice cuando se selecciona una opción
        def al_seleccionar_visto_bueno(*args):
            self.mostrar_info_personal_seleccionado()
        
        dropdown_visto_bueno = tk.OptionMenu(self.root, self.indice_persona_visto_bueno, 
                                              *range(len(etiquetas_personal_visto_bueno)), 
                                              command=al_seleccionar_visto_bueno)
        dropdown_visto_bueno.grid(row=11, column=1, padx=10, pady=5, sticky='ew')
        
        # Actualizar el texto del menú
        menu = dropdown_visto_bueno['menu']
        menu.delete(0, 'end')
        for i, etiqueta in enumerate(etiquetas_personal_visto_bueno):
            menu.add_command(label=etiqueta, 
                            command=tk._setit(self.indice_persona_visto_bueno, i, 
                                            al_seleccionar_visto_bueno))
        
        # Añadir área para mostrar información del personal seleccionado
        self.frame_info_personal = tk.LabelFrame(self.root, text="Información del Personal Seleccionado")
        self.frame_info_personal.grid(row=12, column=0, columnspan=3, padx=10, pady=5, sticky='ew')
        
        self.texto_info_personal = tk.Text(self.frame_info_personal, height=5, width=70)
        self.texto_info_personal.pack(padx=5, pady=5, fill='both', expand=True)
        
    
    
    def _create_progress_section(self):
        """Crea la sección de progreso y botón de procesamiento."""
        tk.Label(self.root, text="Progreso:", anchor='w').grid(row=14, column=0, padx=10, pady=5, sticky='ew')
        self.barra_progreso = ttk.Progressbar(self.root, length=400, mode='determinate')
        self.barra_progreso.grid(row=14, column=1, columnspan=2, padx=10, pady=5, sticky='ew')
        
        # Botón de procesamiento
        tk.Button(self.root, text="Procesar", command=self.procesar_datos, 
                 bg='#4CAF50', fg='white', height=2).grid(row=15, column=0, 
                                                       columnspan=3, pady=20, 
                                                       sticky='ew', padx=20)
    
    def _create_activity_log_section(self):
        """Crea la sección de registro de actividad."""
        tk.Label(self.root, text="Registro de Actividad:", anchor='w').grid(row=16, column=0, columnspan=3, sticky='w', padx=10, pady=5)
        self.texto_registro_actividad = tk.Text(self.root, height=12, width=70)
        self.texto_registro_actividad.grid(row=17, column=0, columnspan=3, padx=10, pady=5, sticky='nsew')
        
        # Agregar scrollbar
        scrollbar = tk.Scrollbar(self.root, command=self.texto_registro_actividad.yview)
        scrollbar.grid(row=17, column=3, sticky='ns')
        self.texto_registro_actividad.config(yscrollcommand=scrollbar.set)
        
        # Configurar fila para expandir texto de estado
        self.root.rowconfigure(17, weight=1)
    

        """
        Muestra la información del personal seleccionado en el área de información.
        """
        # Limpiar el área de texto
        self.texto_info_personal.delete(1.0, tk.END)
        
        # Obtener la información del personal seleccionado
        indice_receptor = self.indice_persona_recibe.get()
        indice_visto_bueno = self.indice_persona_visto_bueno.get()
        
        info_receptor = self.lista_personal_recibe[indice_receptor]
        info_visto_bueno = self.lista_personal_visto_bueno[indice_visto_bueno]
        
        # Mostrar información estructurada
        info_text = "recibeCompra={\n"
        info_text += f"    Grado_recibio_la_compra: \"{info_receptor['Grado_recibio_la_compra']}\",\n"
        info_text += f"    Nombre_recibio_la_compra: \"{info_receptor['Nombre_recibio_la_compra']}\",\n"
        info_text += f"    Matricula_recibio_la_compra: \"{info_receptor['Matricula_recibio_la_compra']}\"\n"
        info_text += "}\n\n"
        
        info_text += "vistoBueno={\n"
        info_text += f"    Grado_Vo_Bo: \"{info_visto_bueno['Grado_Vo_Bo']}\",\n"
        info_text += f"    Nombre_Vo_Bo: \"{info_visto_bueno['Nombre_Vo_Bo']}\",\n"
        info_text += f"    Matricula_Vo_Bo: \"{info_visto_bueno['Matricula_Vo_Bo']}\"\n"
        info_text += "}"
        
        self.texto_info_personal.insert(tk.END, info_text)
    
    def seleccionar_archivo_xml(self):
        """Abre un diálogo para seleccionar un archivo XML."""
        ruta_archivo = filedialog.askopenfilename(filetypes=[("Archivos XML", "*.xml")])
        if ruta_archivo:
            self.entry_ruta_xml.delete(0, tk.END)
            self.entry_ruta_xml.insert(0, ruta_archivo)
    
    def seleccionar_fecha(self, campo_entrada):
        """Abre el selector de fechas para un campo de entrada."""
        DateSelector(self.root, campo_entrada)
    
    def actualizar_registro(self, mensaje):
        """Actualiza el registro de actividad con un nuevo mensaje."""
        self.texto_registro_actividad.insert(tk.END, f"{mensaje}\n")
        self.texto_registro_actividad.see(tk.END)  # Auto-scroll al final
        self.root.update_idletasks()
    
    def actualizar_progreso(self, valor, maximo=100):
        """Actualiza la barra de progreso."""
        self.barra_progreso['value'] = (valor / maximo) * 100
        self.root.update_idletasks()
    
    def procesar_datos(self):
        """Procesa los datos ingresados en la interfaz."""
        # Obtener parámetros de la interfaz
        ruta_xml = self.entry_ruta_xml.get()
        numero_mensaje = self.entry_numero_mensaje.get()
        fecha_mensaje = self.entry_fecha_mensaje.get()
        monto_asignado = self.entry_monto_asignado.get()
        fecha_elaboracion = self.entry_fecha_elaboracion.get()
        mes_comprobacion = self.combo_mes_comprobacion.get()
        
        # Obtener información del personal seleccionado
        indice_receptor = self.indice_persona_recibe.get()
        indice_visto_bueno = self.indice_persona_visto_bueno.get()
        
        info_receptor = self.lista_personal_recibe[indice_receptor]
        info_visto_bueno = self.lista_personal_visto_bueno[indice_visto_bueno]
        
        # Validar campos requeridos
        if not ruta_xml:
            messagebox.showerror("Error", "Por favor, seleccione un archivo XML.")
            return
        
        if not numero_mensaje or not fecha_mensaje or not monto_asignado or not fecha_elaboracion:
            messagebox.showerror("Error", "Todos los campos de información son obligatorios.")
            return
        
        # Convertir fechas a formato de texto
        try:
            fecha_mensaje_texto = convert_fecha_to_texto(fecha_mensaje)
            fecha_elaboracion_texto = convert_fecha_to_texto(fecha_elaboracion)
        except ValueError:
            messagebox.showerror("Error", "El formato de fecha debe ser YYYY-MM-DD")
            return
        
        # Formatear monto
        try:
            # Limpiar el monto de cualquier carácter no numérico excepto punto decimal
            monto_limpio = monto_asignado.replace(',', '').replace('$', '').strip()
            monto_float = float(monto_limpio)
            monto_formateado = "$ {:,.2f}".format(monto_float)
        except ValueError:
            messagebox.showerror("Error", "El monto debe ser un número válido")
            return
        
        # Limpiar texto de registro
        self.texto_registro_actividad.delete(1.0, tk.END)
        
        # Llamar a la función de procesamiento
        self.procesar_archivo(
            ruta_xml, 
            numero_mensaje, 
            fecha_mensaje, 
            fecha_mensaje_texto,
            fecha_elaboracion_texto, 
            monto_formateado, 
            mes_comprobacion,
            info_receptor, 
            info_visto_bueno
        )
    
    def procesar_archivo(self, ruta_xml, numero_mensaje, fecha_mensaje_original, 
                      fecha_mensaje_formateada, fecha_elaboracion_formateada, 
                      monto_formateado, mes_comprobacion, info_receptor, 
                      info_visto_bueno):
        """
        Procesa un archivo XML y genera los documentos correspondientes.
        
        Args:
            ruta_xml: Ruta al archivo XML
            numero_mensaje: Número del mensaje de asignación
            fecha_mensaje_original: Fecha del mensaje en formato original
            fecha_mensaje_formateada: Fecha del mensaje formateada en texto
            fecha_elaboracion_formateada: Fecha de elaboración formateada en texto
            monto_formateado: Monto formateado como moneda
            mes_comprobacion: Mes de comprobación
            info_receptor: Información de la persona que recibe
            info_visto_bueno: Información de la persona que da visto bueno
        """
        try:
            self.actualizar_registro("Iniciando procesamiento...")
            
            # Actualizar progreso
            self.actualizar_progreso(10)
            self.root.update_idletasks()  # Actualizar la interfaz
            
            # Obtener directorio de salida (mismo directorio que el XML)
            directorio_salida = os.path.dirname(ruta_xml)
            
            # Procesar el archivo XML
            self.actualizar_registro(f"Procesando archivo: {os.path.basename(ruta_xml)}...")
            self.root.update_idletasks()  # Actualizar la interfaz
            
            try:
                             
                datos_xml = self.xml_processor.read_xml(
                    ruta_xml,
                    numero_mensaje,
                    fecha_mensaje_original,
                    mes_comprobacion,
                    monto_formateado,
                    fecha_elaboracion_formateada,
                )

                datos_xml['Fecha_mensaje'] = fecha_mensaje_formateada
                
                # Agregar información de personal
                for clave, valor in info_receptor.items():
                    datos_xml[clave] = valor
                
                for clave, valor in info_visto_bueno.items():
                    datos_xml[clave] = valor
                
                self.actualizar_progreso(40)
                self.root.update_idletasks()  # Actualizar la interfaz
                
                # Generar documentos
                self.actualizar_registro("Generando documentos...")
                
                # Generar los documentos usando el DocumentGenerator
                self.document_generator.generate_all_documents(
                    datos_xml,
                    directorio_salida,
                )
                
                self.actualizar_progreso(90)
                self.root.update_idletasks()  # Actualizar la interfaz
                
                # Finalizar
                self.actualizar_progreso(100)
                self.root.update_idletasks()  # Actualizar la interfaz
                
                self.actualizar_registro(f"✅ Documentos generados correctamente para {os.path.basename(ruta_xml)}.")
                messagebox.showinfo("Éxito", "Documentos generados correctamente")
                
            except Exception as e:
                self.actualizar_registro(f"❌ ERROR al procesar {os.path.basename(ruta_xml)}: {str(e)}")
                messagebox.showerror("Error", f"Error al procesar el archivo: {str(e)}")
            
        except Exception as e:
            self.actualizar_registro(f"ERROR: {str(e)}")
            messagebox.showerror("Error", f"Error durante el procesamiento: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = DocumentosXMLApp(root)
    root.mainloop()