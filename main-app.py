import os
import sys
import logging
import json
import tkinter as tk

class NullWriter:
    """Evita 'NoneType has no attribute write' en aplicaciones congeladas sin consola."""
    def write(self, s):
        return len(s) if s else 0
    def flush(self):
        pass

if sys.stdout is None:
    sys.stdout = NullWriter()
if sys.stderr is None:
    sys.stderr = NullWriter()
from tkinter import filedialog, messagebox, ttk
from datetime import datetime

# --- Configuración de BASE_DIR compatible con PyInstaller / ejecutable ---
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Configurar logging seguro hacia archivo
_log_handlers = []
try:
    _log_file = os.path.join(BASE_DIR, 'app.log')
    _log_handlers.append(logging.FileHandler(_log_file, encoding='utf-8', mode='a'))
except Exception:
    pass
if sys.stdout is not None and hasattr(sys.stdout, 'write'):
    _log_handlers.append(logging.StreamHandler(sys.stdout))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=_log_handlers if _log_handlers else None
)

def _safe_report_callback_exception(self, exc, val, tb):
    import traceback
    err_str = "".join(traceback.format_exception(exc, val, tb))
    logging.error(f"Excepcion en Tkinter:\n{err_str}")
    try:
        from tkinter import messagebox
        messagebox.showerror("Error", f"Ocurrió un error inesperado:\n\n{val}")
    except Exception:
        pass

tk.Tk.report_callback_exception = _safe_report_callback_exception

# Importar módulos refactorizados (ajustar según necesidad)
from core.xml_processor import XMLProcessor
from core.document_generator import DocumentGenerator
from utils.file_utils import FileUtils
from ui.date_selector import DateSelector
from ui.config_personal_tab import ConfigPersonalTab
from utils.formatters import convert_fecha_to_texto, formatear_combustible
from tkinter import simpledialog

class DocumentosXMLApp:
    def ask_empleo_recurso(self, conceptos):
        initial_value = formatear_combustible(conceptos)
        new_value = simpledialog.askstring("Empleo del Recurso", "Por favor, verifique y edite si es necesario:", initialvalue=initial_value)
        return new_value if new_value is not None else initial_value
    def mostrar_info_personal_seleccionado(self):
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
    def __init__(self, root):
        """
        Inicializa la aplicación para generar documentos desde XML.
        
        Args:
            root: Ventana principal de Tkinter
        """
        self.root = root
        self.root.title("Generador de Documentos desde XML")
        self.root.geometry("800x700")
        
        icon_path = os.path.join(BASE_DIR, "app_icon.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                pass

        # Cargar configuración desde JSON ANTES de crear widgets
        self.cargar_configuracion_personal()

        # Inicializar componentes
        self.xml_processor = XMLProcessor()
        self.document_generator = DocumentGenerator()
        self.file_utils = FileUtils()

        # Crear la interfaz
        self.create_widgets()

    def cargar_configuracion_personal(self):
        config_file = os.path.join(BASE_DIR, 'config_personal.json')
        
        # Valores por defecto en caso de que el archivo no exista
        default_recibe = [{
            'Grado_recibio_la_compra': "Cor. Cab. E.M., Subjefe Admtvo.",
            'Nombre_recibio_la_compra': "Rafael López Rodríguez.",
            'Matricula_recibio_la_compra': "B-5767973"
        }]
        default_visto_bueno = [
            {
                'Grado_Vo_Bo': "Gral. Bgda. E.M., Cmte. C.N.A.",
                'Nombre_Vo_Bo': "Sergio Ángel Sánchez García.",
                'Matricula_Vo_Bo': "B-3628676"
            },
            {
                'Grado_Vo_Bo': "Garl. Brig. E.M., Jefe Edo. Myr.",
                'Nombre_Vo_Bo': "Samuel Javier Carreño.",
                'Matricula_Vo_Bo': "B-7094414"
            },
            {
                'Grado_Vo_Bo': "Cor. Cab. E.M., Subjefe Admtvo.",
                'Nombre_Vo_Bo': "Rafael López Rodríguez.",
                'Matricula_Vo_Bo': "B-5767973"
            }
        ]

        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.lista_personal_recibe = config.get('lista_personal_recibe', default_recibe)
                    self.lista_personal_visto_bueno = config.get('lista_personal_visto_bueno', default_visto_bueno)
            except Exception as e:
                print(f"Error al leer la configuración de personal: {e}")
                self.lista_personal_recibe = default_recibe
                self.lista_personal_visto_bueno = default_visto_bueno
        else:
            self.lista_personal_recibe = default_recibe
            self.lista_personal_visto_bueno = default_visto_bueno
            try:
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'lista_personal_recibe': self.lista_personal_recibe,
                        'lista_personal_visto_bueno': self.lista_personal_visto_bueno
                    }, f, indent=4, ensure_ascii=False)
            except Exception as e:
                print(f"Error al crear el archivo de configuración: {e}")

    def recargar_configuracion(self):
        self.cargar_configuracion_personal()
        
        # Actualizar los combo box
        etiquetas_recibe = [f"{p.get('Grado_recibio_la_compra', '')} {p.get('Nombre_recibio_la_compra', '')} ({p.get('Matricula_recibio_la_compra', '')})" for p in self.lista_personal_recibe]
        self.combo_personal_recibe['values'] = etiquetas_recibe
        if etiquetas_recibe:
            self.combo_personal_recibe.current(0)
            self.indice_persona_recibe.set(0)
            
        etiquetas_vobo = [f"{p.get('Grado_Vo_Bo', '')} {p.get('Nombre_Vo_Bo', '')} ({p.get('Matricula_Vo_Bo', '')})" for p in self.lista_personal_visto_bueno]
        self.combo_personal_visto_bueno['values'] = etiquetas_vobo
        if etiquetas_vobo:
            self.combo_personal_visto_bueno.current(0)
            self.indice_persona_visto_bueno.set(0)
            
        self.mostrar_info_personal_seleccionado()
    
    def create_widgets(self):
        """Crea y configura todos los widgets de la interfaz de usuario (versión moderna con ttk)."""
        from tkinter import ttk
        self.root.style = ttk.Style()
        self.root.style.theme_use('clam')

        # Control de pestañas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Pestaña Principal
        self.tab_principal = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_principal, text="Generador de Documentos")
        
        # Pestaña Configuración
        self.tab_config = ConfigPersonalTab(self.notebook, config_file=os.path.join(BASE_DIR, 'config_personal.json'), on_save_callback=self.recargar_configuracion)
        self.notebook.add(self.tab_config, text="Configuración Personal")

        self.tab_principal.columnconfigure(0, weight=1)
        self.tab_principal.columnconfigure(1, weight=1)
        self.tab_principal.columnconfigure(2, minsize=120)

        # ==== SECCIÓN DE SELECCIÓN DE ARCHIVO XML ====
        frame_xml = ttk.LabelFrame(self.tab_principal, text="Archivo XML de Factura")
        frame_xml.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky='ew')
        ttk.Label(frame_xml, text="Ruta:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.entry_ruta_xml = ttk.Entry(frame_xml, width=50)
        self.entry_ruta_xml.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        ttk.Button(frame_xml, text="Seleccionar", command=self.seleccionar_archivo_xml).grid(row=0, column=2, padx=5, pady=5)
        frame_xml.columnconfigure(1, weight=1)

        # ==== SECCIÓN DE INFORMACIÓN DEL DOCUMENTO ====
        frame_doc = ttk.LabelFrame(self.tab_principal, text="Información del Documento")
        frame_doc.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky='ew')
        ttk.Label(frame_doc, text="Número de mensaje de asignación:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.entry_numero_mensaje = ttk.Entry(frame_doc)
        self.entry_numero_mensaje.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        ttk.Label(frame_doc, text="Fecha del mensaje de asignación:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.entry_fecha_mensaje = ttk.Entry(frame_doc)
        self.entry_fecha_mensaje.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        ttk.Button(frame_doc, text="Seleccionar", command=lambda: self.seleccionar_fecha(self.entry_fecha_mensaje)).grid(row=1, column=2, padx=5, pady=5)
        ttk.Label(frame_doc, text="Monto asignado:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.entry_monto_asignado = ttk.Entry(frame_doc)
        self.entry_monto_asignado.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        ttk.Label(frame_doc, text="Fecha de elaboración del documento:").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.entry_fecha_elaboracion = ttk.Entry(frame_doc)
        self.entry_fecha_elaboracion.grid(row=3, column=1, padx=5, pady=5, sticky='ew')
        ttk.Button(frame_doc, text="Seleccionar", command=lambda: self.seleccionar_fecha(self.entry_fecha_elaboracion)).grid(row=3, column=2, padx=5, pady=5)
        ttk.Label(frame_doc, text="Mes de comprobación:").grid(row=4, column=0, padx=5, pady=5, sticky='w')
        self.combo_mes_comprobacion = tk.StringVar(self.root)
        meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
        self.combo_mes_comprobacion.set(meses[datetime.now().month - 1])
        mes_combo = ttk.Combobox(frame_doc, textvariable=self.combo_mes_comprobacion, values=meses, state="readonly")
        mes_combo.grid(row=4, column=1, padx=5, pady=5, sticky='ew')
        frame_doc.columnconfigure(1, weight=1)

        # ==== SECCIÓN DE INFORMACIÓN DEL PERSONAL ====
        frame_personal = ttk.LabelFrame(self.tab_principal, text="Información del Personal")
        frame_personal.grid(row=2, column=0, columnspan=3, padx=10, pady=5, sticky='ew')
        ttk.Label(frame_personal, text="Recibió la compra:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.indice_persona_recibe = tk.IntVar(self.root, value=0)
        etiquetas_personal_recibe = [f"{p['Grado_recibio_la_compra']} {p['Nombre_recibio_la_compra']} ({p['Matricula_recibio_la_compra']})" for p in self.lista_personal_recibe]
        self.combo_personal_recibe = ttk.Combobox(frame_personal, values=etiquetas_personal_recibe, state="readonly")
        self.combo_personal_recibe.current(0)
        self.combo_personal_recibe.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        def on_recibe_selected(event):
            idx = self.combo_personal_recibe.current()
            self.indice_persona_recibe.set(idx)
            self.mostrar_info_personal_seleccionado()
        self.combo_personal_recibe.bind("<<ComboboxSelected>>", on_recibe_selected)

        ttk.Label(frame_personal, text="Visto bueno:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.indice_persona_visto_bueno = tk.IntVar(self.root, value=0)
        etiquetas_personal_visto_bueno = [f"{p['Grado_Vo_Bo']} {p['Nombre_Vo_Bo']} ({p['Matricula_Vo_Bo']})" for p in self.lista_personal_visto_bueno]
        self.combo_personal_visto_bueno = ttk.Combobox(frame_personal, values=etiquetas_personal_visto_bueno, state="readonly")
        self.combo_personal_visto_bueno.current(0)
        self.combo_personal_visto_bueno.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        def on_visto_bueno_selected(event):
            idx = self.combo_personal_visto_bueno.current()
            self.indice_persona_visto_bueno.set(idx)
            self.mostrar_info_personal_seleccionado()
        self.combo_personal_visto_bueno.bind("<<ComboboxSelected>>", on_visto_bueno_selected)

        # Área para mostrar información del personal seleccionado
        self.frame_info_personal = ttk.LabelFrame(frame_personal, text="Información del Personal Seleccionado")
        self.frame_info_personal.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky='ew')
        self.texto_info_personal = tk.Text(self.frame_info_personal, height=5, width=70)
        self.texto_info_personal.pack(padx=5, pady=5, fill='both', expand=True)
        frame_personal.columnconfigure(1, weight=1)

        # ==== SECCIÓN DE PROGRESO Y PROCESAMIENTO ====
        frame_progreso = ttk.LabelFrame(self.tab_principal, text="Progreso y Procesamiento")
        frame_progreso.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky='ew')
        ttk.Label(frame_progreso, text="Progreso:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.barra_progreso = ttk.Progressbar(frame_progreso, length=400, mode='determinate')
        self.barra_progreso.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        ttk.Button(frame_progreso, text="Procesar", command=self.procesar_datos).grid(row=1, column=0, columnspan=3, pady=10, sticky='ew', padx=5)
        frame_progreso.columnconfigure(1, weight=1)

        # ==== SECCIÓN DE REGISTRO DE ACTIVIDAD ====
        frame_log = ttk.LabelFrame(self.tab_principal, text="Registro de Actividad")
        frame_log.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')
        self.texto_registro_actividad = tk.Text(frame_log, height=12, width=70)
        self.texto_registro_actividad.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        scrollbar = ttk.Scrollbar(frame_log, command=self.texto_registro_actividad.yview)
        scrollbar.pack(side='right', fill='y')
        self.texto_registro_actividad.config(yscrollcommand=scrollbar.set)
        self.tab_principal.rowconfigure(4, weight=1)
        
        # Ocultar botones que no estaban en uso y asegurar redimensionamiento
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    
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
            self.actualizar_progreso(10)
            self.root.update_idletasks()  # Actualizar la interfaz

            # Obtener directorio de salida (mismo directorio que el XML)
            directorio_salida = os.path.dirname(ruta_xml)

            # PRIMERO: Buscar el PDF de la factura y guardar la ruta
            factura_pdf = self.file_utils.find_pdf_for_xml(ruta_xml)
            if not factura_pdf or not os.path.exists(factura_pdf):
                self.actualizar_registro("❌ No se encontró el PDF de la factura. Procesamiento cancelado.")
                messagebox.showerror("Error", "No se encontró el PDF de la factura correspondiente al XML seleccionado.\n\nAsegúrate de que el PDF esté en la misma carpeta y con el nombre correcto.")
                return
            self.actualizar_registro(f"PDF de la factura encontrado: {factura_pdf}")


            # SEGUNDO: Procesar el archivo XML para obtener datos_xml
            self.actualizar_registro(f"Procesando archivo XML: {os.path.basename(ruta_xml)}...")
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

                # Solicitar al usuario que verifique el empleo del recurso
                empleo_recurso = self.ask_empleo_recurso(datos_xml['Conceptos'])
                datos_xml['Empleo_recurso'] = empleo_recurso

                # Validar claves requeridas para SAT
                if not datos_xml.get('Serie') or not datos_xml.get('Numero'):
                    self.actualizar_registro("❌ El XML no contiene los campos 'Serie' y/o 'Numero'. Procesamiento cancelado.")
                    messagebox.showerror("Error", "El XML no contiene los campos 'Serie' y/o 'Numero' requeridos para la verificación SAT.\n\nVerifica el archivo XML.")
                    return

                # Ahora sí, descargar la verificación del SAT
                self.actualizar_registro("Descargando verificación del SAT...")
                from utils.web_utils import descargarVerificacion
                sat_pdf = descargarVerificacion(datos_xml, directorio_salida)
                if not sat_pdf or not os.path.exists(sat_pdf):
                    self.actualizar_registro("❌ No se pudo descargar la verificación del SAT. Procesamiento cancelado.")
                    messagebox.showerror("Error", "No se pudo descargar la verificación del SAT.\n\nVerifica tu conexión y los datos de la factura.")
                    return
                self.actualizar_registro(f"PDF de verificación SAT descargado: {sat_pdf}")

                self.actualizar_progreso(40)
                self.root.update_idletasks()  # Actualizar la interfaz

                # Generar documentos
                self.actualizar_registro("Generando documentos...")

                # Generar los documentos usando el DocumentGenerator
                # 1. Generar los documentos Word y obtener rutas
                generated_files = self.document_generator.generate_all_documents(
                    datos_xml,
                    directorio_salida,
                )

                self.actualizar_progreso(60)
                self.root.update_idletasks()

                # 2. Convertir los DOCX generados a PDF
                from utils.file_utils import convert_to_pdf
                pdf_paths = {}
                for key, docx_path in generated_files.items():
                    pdf_path = os.path.splitext(docx_path)[0] + ".pdf"
                    convert_to_pdf(docx_path, pdf_path)
                    pdf_paths[key] = pdf_path

                self.actualizar_registro("PDFs generados a partir de los DOCX.")
                self.actualizar_progreso(70)
                self.root.update_idletasks()

                # 3. Procesamiento de PDFs según el flujo solicitado
                from utils.pdf_utils import contar_paginas, unir_pdfs
                legalizacion_factura_pdf = pdf_paths.get("legalizacion_factura")
                factura_legalizada_pdf = os.path.join(directorio_salida, "facturalegalizada.pdf")

                if factura_pdf and legalizacion_factura_pdf:
                    # Intercalar manualmente: factura, legalización, factura, legalización...
                    from PyPDF2 import PdfReader, PdfWriter
                    writer = PdfWriter()
                    with open(factura_pdf, 'rb') as f_factura, open(legalizacion_factura_pdf, 'rb') as f_leg:
                        factura_reader = PdfReader(f_factura)
                        legalizacion_reader = PdfReader(f_leg)
                        num_paginas = len(factura_reader.pages)
                        for i in range(num_paginas):
                            writer.add_page(factura_reader.pages[i])
                            for leg_page in legalizacion_reader.pages:
                                writer.add_page(leg_page)
                    with open(factura_legalizada_pdf, 'wb') as f_out:
                        writer.write(f_out)
                    self.actualizar_registro(f"Factura legalizada generada: {os.path.basename(factura_legalizada_pdf)}")
                else:
                    factura_legalizada_pdf = factura_pdf  # fallback


                # Paso 2: Intercalar la verificación SAT descargada con legalizacion_verificacion.pdf
                from utils.pdf_utils import intercalar_pdf
                legalizacion_verificacion_pdf = pdf_paths.get("legalizacion_verificacion")
                sat_intercalado = os.path.join(directorio_salida, "verificacionlegalizada.pdf")
                if sat_pdf and legalizacion_verificacion_pdf:
                    intercalar_pdf(sat_pdf, legalizacion_verificacion_pdf, sat_intercalado)
                    self.actualizar_registro(f"Verificación SAT legalizada generada: {os.path.basename(sat_intercalado)}")
                else:
                    sat_intercalado = sat_pdf  # fallback

                # Paso 3: Intercalar xml.pdf con legalizacion_xml.pdf
                xml_pdf = pdf_paths.get("xml")
                legalizacion_xml_pdf = pdf_paths.get("legalizacion_xml")
                xml_intercalado = os.path.join(directorio_salida, "xmllegalizado.pdf")
                if xml_pdf and legalizacion_xml_pdf:
                    intercalar_pdf(xml_pdf, legalizacion_xml_pdf, xml_intercalado)
                    self.actualizar_registro(f"XML legalizado generado: {os.path.basename(xml_intercalado)}")
                else:
                    xml_intercalado = xml_pdf  # fallback

                # Paso 4: Unir todos los archivos en uno solo
                pdfs_a_unir = [p for p in [factura_legalizada_pdf, sat_intercalado, xml_intercalado] if p]
                pdf_final = os.path.join(directorio_salida, "documento_final.pdf")
                unir_pdfs(pdfs_a_unir, pdf_final)

                self.actualizar_registro(f"✅ Documentos generados y PDF final creado: {os.path.basename(pdf_final)}")
                self.actualizar_progreso(100)
                self.root.update_idletasks()
                messagebox.showinfo("Éxito", f"Documentos generados correctamente. PDF final: {os.path.basename(pdf_final)}")

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