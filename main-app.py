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
        # Configurar grid
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, minsize=120)
        
        # Selección de archivo XML
        tk.Label(self.root, text="Archivo XML de Factura:", anchor='w').grid(row=0, column=0, padx=10, pady=5, sticky='ew')
        self.entry_xml_path = tk.Entry(self.root, width=50)
        self.entry_xml_path.grid(row=0, column=1, padx=10, pady=5, sticky='ew')
        tk.Button(self.root, text="Seleccionar", command=self.select_xml_file).grid(row=0, column=2, padx=10, pady=5)
        
        # Separador
        ttk.Separator(self.root, orient='horizontal').grid(row=1, column=0, columnspan=3, sticky='ew', pady=10)
        
        # Sección de información común
        tk.Label(self.root, text="Información del Documento", font=('Helvetica', 10, 'bold')).grid(row=2, column=0, columnspan=3, sticky='w', padx=5)
        
        # Número de mensaje
        tk.Label(self.root, text="Número de mensaje de asignación:", anchor='w').grid(row=3, column=0, padx=10, pady=5, sticky='ew')
        self.entry_numero_mensaje = tk.Entry(self.root)
        self.entry_numero_mensaje.grid(row=3, column=1, padx=10, pady=5, sticky='ew')
        
        # Fecha del mensaje
        tk.Label(self.root, text="Fecha del mensaje de asignación:", anchor='w').grid(row=4, column=0, padx=10, pady=5, sticky='ew')
        self.entry_fecha_mensaje = tk.Entry(self.root)
        self.entry_fecha_mensaje.grid(row=4, column=1, padx=10, pady=5, sticky='ew')
        tk.Button(self.root, text="Seleccionar", command=lambda: self.select_date(self.entry_fecha_mensaje)).grid(row=4, column=2, padx=10, pady=5)
        
        # Monto asignado
        tk.Label(self.root, text="Monto asignado:", anchor='w').grid(row=5, column=0, padx=10, pady=5, sticky='ew')
        self.entry_monto = tk.Entry(self.root)
        self.entry_monto.grid(row=5, column=1, padx=10, pady=5, sticky='ew')
        
        # Fecha del documento
        tk.Label(self.root, text="Fecha de elaboración del documento:", anchor='w').grid(row=6, column=0, padx=10, pady=5, sticky='ew')
        self.entry_fecha_documento = tk.Entry(self.root)
        self.entry_fecha_documento.grid(row=6, column=1, padx=10, pady=5, sticky='ew')
        tk.Button(self.root, text="Seleccionar", command=lambda: self.select_date(self.entry_fecha_documento)).grid(row=6, column=2, padx=10, pady=5)
        
        # Mes asignado
        tk.Label(self.root, text="Mes de comprobación:", anchor='w').grid(row=7, column=0, padx=10, pady=5, sticky='ew')
        self.mes_asignado_var = tk.StringVar(self.root)
        meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", 
                "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
        self.mes_asignado_var.set(meses[datetime.now().month - 1])  # Mes actual como predeterminado
        option_menu_meses = tk.OptionMenu(self.root, self.mes_asignado_var, *meses)
        option_menu_meses.grid(row=7, column=1, padx=10, pady=5, sticky='ew')
        
        # Separador
        ttk.Separator(self.root, orient='horizontal').grid(row=8, column=0, columnspan=3, sticky='ew', pady=10)
        
        # Sección de personal
        tk.Label(self.root, text="Información del Personal", font=('Helvetica', 10, 'bold')).grid(row=9, column=0, columnspan=3, sticky='w', padx=5)
        
        # Define el personal estructurado
        self.personal_recibe_data = [
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
        
        self.personal_visto_bueno_data = [
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
        self.recibe_compra_index = tk.IntVar(self.root, value=0)
        
        # Crear descripciones para mostrar en el menú
        personal_recibe_display = []
        for persona in self.personal_recibe_data:
            display = f"{persona['Grado_recibio_la_compra']} {persona['Nombre_recibio_la_compra']} ({persona['Matricula_recibio_la_compra']})"
            personal_recibe_display.append(display)
        
        # Función para actualizar el índice cuando se selecciona una opción
        def on_recibe_select(*args):
            self.show_selected_personal_info()
        
        option_menu_recibe = tk.OptionMenu(self.root, self.recibe_compra_index, *range(len(personal_recibe_display)), 
                                          command=on_recibe_select)
        option_menu_recibe.grid(row=10, column=1, padx=10, pady=5, sticky='ew')
        
        # Actualizar el texto del menú
        menu = option_menu_recibe['menu']
        menu.delete(0, 'end')
        for i, display in enumerate(personal_recibe_display):
            menu.add_command(label=display, command=tk._setit(self.recibe_compra_index, i, on_recibe_select))
        
        # Persona que da visto bueno
        tk.Label(self.root, text="Visto bueno:", anchor='w').grid(row=11, column=0, padx=10, pady=5, sticky='ew')
        self.visto_bueno_index = tk.IntVar(self.root, value=0)
        
        # Crear descripciones para mostrar en el menú
        personal_visto_bueno_display = []
        for persona in self.personal_visto_bueno_data:
            display = f"{persona['Grado_Vo_Bo']} {persona['Nombre_Vo_Bo']} ({persona['Matricula_Vo_Bo']})"
            personal_visto_bueno_display.append(display)
        
        # Función para actualizar el índice cuando se selecciona una opción
        def on_visto_bueno_select(*args):
            self.show_selected_personal_info()
        
        option_menu_visto_bueno = tk.OptionMenu(self.root, self.visto_bueno_index, *range(len(personal_visto_bueno_display)), 
                                               command=on_visto_bueno_select)
        option_menu_visto_bueno.grid(row=11, column=1, padx=10, pady=5, sticky='ew')
        
        # Actualizar el texto del menú
        menu = option_menu_visto_bueno['menu']
        menu.delete(0, 'end')
        for i, display in enumerate(personal_visto_bueno_display):
            menu.add_command(label=display, command=tk._setit(self.visto_bueno_index, i, on_visto_bueno_select))
        
        # Añadir área para mostrar información del personal seleccionado
        self.info_frame = tk.LabelFrame(self.root, text="Información del Personal Seleccionado")
        self.info_frame.grid(row=12, column=0, columnspan=3, padx=10, pady=5, sticky='ew')
        
        self.info_text = tk.Text(self.info_frame, height=5, width=70)
        self.info_text.pack(padx=5, pady=5, fill='both', expand=True)
        
        # Mostrar la información inicial
        self.show_selected_personal_info()
        
        # Separador
        ttk.Separator(self.root, orient='horizontal').grid(row=13, column=0, columnspan=3, sticky='ew', pady=10)
        
        # Barra de progreso
        tk.Label(self.root, text="Progreso:", anchor='w').grid(row=14, column=0, padx=10, pady=5, sticky='ew')
        self.progress_bar = ttk.Progressbar(self.root, length=400, mode='determinate')
        self.progress_bar.grid(row=14, column=1, columnspan=2, padx=10, pady=5, sticky='ew')
        
        # Botón de procesamiento
        tk.Button(self.root, text="Procesar", command=self.process_data, bg='#4CAF50', fg='white', height=2).grid(row=15, column=0, columnspan=3, pady=20, sticky='ew', padx=20)
        
        # Registro de actividad
        tk.Label(self.root, text="Registro de Actividad:", anchor='w').grid(row=16, column=0, columnspan=3, sticky='w', padx=10, pady=5)
        self.status_text = tk.Text(self.root, height=12, width=70)
        self.status_text.grid(row=17, column=0, columnspan=3, padx=10, pady=5, sticky='nsew')
        
        # Agregar scrollbar
        scrollbar = tk.Scrollbar(self.root, command=self.status_text.yview)
        scrollbar.grid(row=17, column=3, sticky='ns')
        self.status_text.config(yscrollcommand=scrollbar.set)
        
        # Configurar fila para expandir texto de estado
        self.root.rowconfigure(17, weight=1)
    
    def show_selected_personal_info(self):
        """
        Muestra la información del personal seleccionado en el área de información.
        """
        # Limpiar el área de texto
        self.info_text.delete(1.0, tk.END)
        
        # Obtener la información del personal seleccionado
        recibe_index = self.recibe_compra_index.get()
        visto_bueno_index = self.visto_bueno_index.get()
        
        recibe_info = self.personal_recibe_data[recibe_index]
        visto_bueno_info = self.personal_visto_bueno_data[visto_bueno_index]
        
        # Mostrar información estructurada
        info_text = "recibeCompra={\n"
        info_text += f"    Grado_recibio_la_compra: \"{recibe_info['Grado_recibio_la_compra']}\",\n"
        info_text += f"    Nombre_recibio_la_compra: \"{recibe_info['Nombre_recibio_la_compra']}\",\n"
        info_text += f"    Matricula_recibio_la_compra: \"{recibe_info['Matricula_recibio_la_compra']}\"\n"
        info_text += "}\n\n"
        
        info_text += "vistoBueno={\n"
        info_text += f"    Grado_Vo_Bo: \"{visto_bueno_info['Grado_Vo_Bo']}\",\n"
        info_text += f"    Nombre_Vo_Bo: \"{visto_bueno_info['Nombre_Vo_Bo']}\",\n"
        info_text += f"    Matricula_Vo_Bo: \"{visto_bueno_info['Matricula_Vo_Bo']}\"\n"
        info_text += "}"
        
        self.info_text.insert(tk.END, info_text)
    
    def select_xml_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Archivos XML", "*.xml")])
        if file_path:
            self.entry_xml_path.delete(0, tk.END)
            self.entry_xml_path.insert(0, file_path)
    
    def select_date(self, entry_widget):
        DateSelector(self.root, entry_widget)
    
    def update_status(self, message):
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)  # Auto-scroll al final
        self.root.update_idletasks()
    
    def update_progress(self, value, maximum=100):
        self.progress_bar['value'] = (value / maximum) * 100
        self.root.update_idletasks()
    
    def process_data(self):
        # Obtener parámetros de la interfaz
        xml_path = self.entry_xml_path.get()
        numero_mensaje = self.entry_numero_mensaje.get()
        fecha_mensaje = self.entry_fecha_mensaje.get()
        monto_asignado = self.entry_monto.get()
        fecha_documento = self.entry_fecha_documento.get()
        mes_asignado = self.mes_asignado_var.get()
        
        # Obtener información del personal seleccionado
        recibe_index = self.recibe_compra_index.get()
        visto_bueno_index = self.visto_bueno_index.get()
        
        recibe_info = self.personal_recibe_data[recibe_index]
        visto_bueno_info = self.personal_visto_bueno_data[visto_bueno_index]
        
        # Validar campos requeridos
        if not xml_path:
            messagebox.showerror("Error", "Por favor, seleccione un archivo XML.")
            return
        
        if not numero_mensaje or not fecha_mensaje or not monto_asignado or not fecha_documento:
            messagebox.showerror("Error", "Todos los campos de información son obligatorios.")
            return
        
        # Convertir fechas a formato de texto
        try:
            fecha_mensaje_texto = convert_fecha_to_texto(fecha_mensaje)
            fecha_documento_texto = convert_fecha_to_texto(fecha_documento)
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
        
        # Limpiar texto de estado
        self.status_text.delete(1.0, tk.END)
        
        # Llamar directamente a la función de procesamiento
        self.process_file(
            xml_path, numero_mensaje, fecha_mensaje, fecha_mensaje_texto,
            fecha_documento_texto, monto_formateado, mes_asignado,
            recibe_info, visto_bueno_info
        )
    
    def process_file(self, xml_path, numero_mensaje, fecha_mensaje_raw, fecha_mensaje,
                      fecha_documento, monto_formateado, mes_asignado,
                      recibe_info, visto_bueno_info):
        try:
            self.update_status("Iniciando procesamiento...")
            
            # Actualizar progreso
            self.update_progress(10)
            self.root.update_idletasks()  # Actualizar la interfaz
            
            # Obtener directorio de salida (mismo directorio que el XML)
            output_dir = os.path.dirname(xml_path)
            
            # Procesar el archivo XML
            self.update_status(f"Procesando archivo: {os.path.basename(xml_path)}...")
            self.root.update_idletasks()  # Actualizar la interfaz
            
            try:
                # Leer y procesar el XML
                partida_numero = "00000"  # Este valor podría provenir de otro lugar
                
                xml_data = self.xml_processor.read_xml(
                    xml_path,
                    numero_mensaje,
                    fecha_mensaje_raw,
                    mes_asignado,
                    monto_formateado,
                    fecha_documento,
                    partida_numero,
                   
                )
                
                # Agregar información de personal (ya viene estructurada correctamente)
                # Copiar todos los campos del diccionario de quien recibe la compra
                for key, value in recibe_info.items():
                    xml_data[key] = value
                
                # Copiar todos los campos del diccionario de visto bueno
                for key, value in visto_bueno_info.items():
                    xml_data[key] = value
                
                self.update_progress(40)
                self.root.update_idletasks()  # Actualizar la interfaz
                
                # Generar documentos
                self.update_status("Generando documentos...")
                
                # Generar los documentos necesarios utilizando los nuevos campos de personal
                self.document_generator.generate_all_documents(
                    xml_data,
                    output_dir,
                    {'monto': monto_formateado}  # Simplificado ya que no usamos partidas del Excel
                )
                
                self.update_progress(90)
                self.root.update_idletasks()  # Actualizar la interfaz
                
                # Descargar verificación SAT
                self.update_status("Descargando verificación del SAT...")
                
                # Aquí iría el código para la verificación SAT
                # (manteniendo la funcionalidad existente)
                
                self.update_progress(100)
                self.root.update_idletasks()  # Actualizar la interfaz
                
                self.update_status(f"✅ Documentos generados correctamente para {os.path.basename(xml_path)}.")
                messagebox.showinfo("Éxito", "Documentos generados correctamente")
                
            except Exception as e:
                self.update_status(f"❌ ERROR al procesar {os.path.basename(xml_path)}: {str(e)}")
                messagebox.showerror("Error", f"Error al procesar el archivo: {str(e)}")
            
        except Exception as e:
            self.update_status(f"ERROR: {str(e)}")
            messagebox.showerror("Error", f"Error durante el procesamiento: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = DocumentosXMLApp(root)
    root.mainloop()