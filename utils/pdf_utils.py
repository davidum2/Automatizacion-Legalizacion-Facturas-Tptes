import os
from PyPDF2 import PdfReader, PdfWriter

def contar_paginas(pdf_path):
    """Cuenta el número de páginas de un PDF."""
    with open(pdf_path, 'rb') as f:
        reader = PdfReader(f)
        return len(reader.pages)

def intercalar_pdf(base_pdf, intercalar_pdf, output_pdf):
    """
    Intercala una copia de intercalar_pdf después de cada página de base_pdf.
    """
    writer = PdfWriter()
    with open(base_pdf, 'rb') as f_base, open(intercalar_pdf, 'rb') as f_inter:
        base_reader = PdfReader(f_base)
        inter_reader = PdfReader(f_inter)
        for page in base_reader.pages:
            writer.add_page(page)
            # Agrega una copia de la hoja de legalización después de cada página
            for inter_page in inter_reader.pages:
                writer.add_page(inter_page)
        with open(output_pdf, 'wb') as f_out:
            writer.write(f_out)

def unir_pdfs(lista_pdfs, output_pdf):
    """
    Une una lista de PDFs en un solo archivo.
    """
    writer = PdfWriter()
    for pdf_path in lista_pdfs:
        with open(pdf_path, 'rb') as f:
            reader = PdfReader(f)
            for page in reader.pages:
                writer.add_page(page)
    with open(output_pdf, 'wb') as f_out:
        writer.write(f_out)
