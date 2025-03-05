import os
import docx2pdf
from utils.file_utils import convert_to_pdf
from utils.web_utils import descargar_verificacion

class DocumentGenerator:
    """
    Clase para generar todos los documentos necesarios a partir de los datos XML.
    """
    
    def __init__(self):
        # Rutas de plantillas
        self.path_general = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates")
        self.path_legalizacionFactura = os.path.join(self.path_general, "legalizacion_factura.docx")
        self.path_legalizacionVerificacion = os.path.join(self.path_general, "legalizacion_verificacion.docx")
        self.path_legalizacionXml = os.path.join(self.path_general, "legalizacion_xml.docx")
        self.path_crearXml = os.path.join(self.path_general, "xml.docx")
        self.path_oficioRemision = os.path.join(self.path_general, "oficio_remision.docx")
    
    def generate_all_documents(self, data, output_dir, partida):
        """
        Genera todos los documentos necesarios para una factura.
        
        Args:
            data (dict): Datos extraídos del XML
            output_dir (str): Directorio de salida
            partida (dict): Información de la partida
            
        Returns:
            bool: True si la generación fue exitosa
        """
        try:
            # 1. Generar Oficio de Remisión
            self._generate_oficio_remision(data, output_dir)
            
            # 2. Generar Legalización de Factura
            self._generate_legalizacion_factura(data, output_dir)
            
            # 3. Descargar Verificación SAT
            self._download_sat_verification(data, output_dir)
            
            # 4. Generar Legalización de Verificación
            self._generate_legalizacion_verificacion(data, output_dir)
            
            # 5. Generar XML
            self._generate_xml_document(data, output_dir)
            
            # 6. Generar Legalización de XML
            self._generate_legalizacion_xml(data, output_dir)
            
            # 7. Generar Relación de Facturas
            self._generate_relacion_facturas(data, output_dir, partida['monto'])
            
            return True
        except Exception as e:
            raise Exception(f"Error al generar documentos: {str(e)}")
    
    def _generate_oficio_remision(self, data, output_dir):
        """
        Genera el oficio de remisión.
        """
        from generators.oficio_de_remision import create_of_remision
        
        try:
            # Generar documento DOCX
            docx_path = create_of_remision(output_dir, data)
            
            # Convertir a PDF
            pdf_path = os.path.join(output_dir, "oficio_de_remision.pdf")
            convert_to_pdf(docx_path, pdf_path)
            
            return pdf_path
        except Exception as e:
            raise Exception(f"Error al generar oficio de remisión: {str(e)}")
    
    def _generate_legalizacion_factura(self, data, output_dir):
        """
        Genera la legalización de factura.
        """
        from generators.legalizacionFactura import legalizacionFactura
        from generators.plantillas_pdf import createLegalizacionFactura
        
        try:
            # Generar documento DOCX
            docx_path = legalizacionFactura(self.path_legalizacionFactura, output_dir, data)
            
            # Generar PDF directamente
            pdf_path = os.path.join(output_dir, "legalizacion_factura.pdf")
            createLegalizacionFactura(data, pdf_path)
            
            return pdf_path
        except Exception as e:
            raise Exception(f"Error al generar legalización de factura: {str(e)}")
    
    def _download_sat_verification(self, data, output_dir):
        """
        Descarga la verificación del SAT.
        """
        try:
            # Descargar verificación
            verificacion_path = descargar_verificacion(data, output_dir)
            
            return verificacion_path
        except Exception as e:
            raise Exception(f"Error al descargar verificación del SAT: {str(e)}")
    
    def _generate_legalizacion_verificacion(self, data, output_dir):
        """
        Genera la legalización de verificación.
        """
        from generators.legalizacionVerificacion import legalizacionVerificacion
        from generators.plantillas_pdf import createLegalizacionVerificacionSAT
        
        try:
            # Generar documento DOCX
            docx_path = legalizacionVerificacion(self.path_legalizacionVerificacion, output_dir, data)
            
            # Generar PDF directamente
            pdf_path = os.path.join(output_dir, "legalizacion_verificacion.pdf")
            createLegalizacionVerificacionSAT(data, pdf_path)
            
            return pdf_path
        except Exception as e:
            raise Exception(f"Error al generar legalización de verificación: {str(e)}")
    
    def _generate_xml_document(self, data, output_dir):
        """
        Genera el documento XML.
        """
        from generators.crearDocXml import crearXML
        from generators.plantillas_pdf import createXMLenPDF
        
        try:
            # Generar documento DOCX
            docx_path = crearXML(self.path_crearXml, output_dir, data)
            
            # Convertir a PDF
            pdf_path = os.path.join(output_dir, "xml.pdf")
            convert_to_pdf(docx_path, pdf_path)
            
            # También generar PDF directamente
            createXMLenPDF(data, pdf_path)
            
            return pdf_path
        except Exception as e:
            raise Exception(f"Error al generar documento XML: {str(e)}")
    
    def _generate_legalizacion_xml(self, data, output_dir):
        """
        Genera la legalización de XML.
        """
        from generators.legalizacionXml import legalizacionXml
        from generators.plantillas_pdf import cretaeLegalizacionXML
        
        try:
            # Generar documento DOCX
            docx_path = legalizacionXml(self.path_legalizacionXml, output_dir, data)
            
            # Generar PDF directamente
            pdf_path = os.path.join(output_dir, "legalizacion_xml.pdf")
            cretaeLegalizacionXML(data, pdf_path)
            
            return pdf_path
        except Exception as e:
            raise Exception(f"Error al generar legalización de XML: {str(e)}")
    
    def _generate_relacion_facturas(self, data, output_dir, monto):
        """
        Genera la relación de facturas.
        """
        from generators.createRelacionFacturas import create_relacion_de_facturas_excel
        
        try:
            # Generar documento Excel
            excel_path = create_relacion_de_facturas_excel(data, output_dir, monto)
            
            return excel_path
        except Exception as e:
            raise Exception(f"Error al generar relación de facturas: {str(e)}")
