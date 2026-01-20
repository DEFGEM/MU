from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfgen import canvas
import qrcode
from io import BytesIO
from datetime import datetime
import os


class InvoiceGenerator:
    """Generador de facturas en PDF con formato profesional"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configura estilos personalizados para el documento"""
        # Estilo para el título
        self.styles.add(ParagraphStyle(
            name='InvoiceTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1c3d5a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='InvoiceSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1c3d5a'),
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para texto normal
        self.styles.add(ParagraphStyle(
            name='InvoiceNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#495057')
        ))
        
        # Estilo para texto pequeño
        self.styles.add(ParagraphStyle(
            name='InvoiceSmall',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#6c757d')
        ))
    
    def generate_qr_code(self, data):
        """Genera un código QR y lo retorna como imagen"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir a BytesIO para usarlo con ReportLab
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return Image(buffer, width=1.5*inch, height=1.5*inch)
    
    def generate_invoice_pdf(self, transaction_data, output_path=None):
        """
        Genera una factura en PDF
        
        Args:
            transaction_data: Diccionario con los datos de la transacción
            output_path: Ruta donde guardar el PDF (opcional)
        
        Returns:
            BytesIO con el PDF generado
        """
        # Crear buffer para el PDF
        buffer = BytesIO()
        
        # Crear el documento
        if output_path:
            doc = SimpleDocTemplate(output_path, pagesize=letter,
                                   rightMargin=72, leftMargin=72,
                                   topMargin=72, bottomMargin=72)
        else:
            doc = SimpleDocTemplate(buffer, pagesize=letter,
                                   rightMargin=72, leftMargin=72,
                                   topMargin=72, bottomMargin=72)
        
        # Contenedor para los elementos del documento
        elements = []
        
        # Encabezado
        elements.append(Paragraph("FACTURA DE PAGO", self.styles['InvoiceTitle']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Información de la empresa y número de factura
        company_data = [
            [Paragraph("<b>MU S.A. de C.V.</b>", self.styles['InvoiceNormal']),
             Paragraph(f"<b>FACTURA</b><br/>{transaction_data.get('invoice_number', 'N/A')}", 
                      self.styles['InvoiceNormal'])]
        ]
        company_table = Table(company_data, colWidths=[4*inch, 2.5*inch])
        company_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        elements.append(company_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Información del emisor y receptor
        info_data = [
            [Paragraph("<b>EMISOR</b>", self.styles['InvoiceSubtitle']),
             Paragraph("<b>RECEPTOR</b>", self.styles['InvoiceSubtitle'])],
            [Paragraph("MU S.A. de C.V.<br/>Av. Tecnología #123, Col. Digital<br/>Ciudad de México, CDMX 06600<br/>RFC: PSE123456ABC<br/>Tel: +52 55 1234 5678<br/>Email: facturacion@mu.com", 
                      self.styles['InvoiceSmall']),
             Paragraph(f"{transaction_data.get('full_name', 'N/A')}<br/>RFC: {transaction_data.get('rfc', 'N/A')}<br/>Fecha: {transaction_data.get('date', 'N/A')}<br/>Hora: {transaction_data.get('time', 'N/A')}", 
                      self.styles['InvoiceSmall'])]
        ]
        info_table = Table(info_data, colWidths=[3.25*inch, 3.25*inch])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#dee2e6')),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')),
            ('PADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Detalles de la transacción
        elements.append(Paragraph("DETALLES DE LA TRANSACCIÓN", self.styles['InvoiceSubtitle']))
        elements.append(Spacer(1, 0.1*inch))
        
        transaction_details = [
            ['ID de Transacción:', f"TXN-{transaction_data.get('id', 'N/A')}"],
            ['Método de Pago:', 'Tarjeta de Crédito/Débito'],
            ['Tarjeta:', f"**** **** **** {transaction_data.get('card_last4', 'N/A')}"],
            ['Titular:', transaction_data.get('cardholder_name', 'N/A')],
            ['Estado:', transaction_data.get('status', 'N/A')],
        ]
        
        transaction_table_data = [[Paragraph(key, self.styles['InvoiceNormal']),
                                  Paragraph(str(value), self.styles['InvoiceNormal'])] 
                                 for key, value in transaction_details]
        
        transaction_table = Table(transaction_table_data, colWidths=[2.5*inch, 4*inch])
        transaction_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(transaction_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Desglose de montos
        elements.append(Paragraph("DESGLOSE DE MONTOS", self.styles['InvoiceSubtitle']))
        elements.append(Spacer(1, 0.1*inch))
        
        amount = float(transaction_data.get('amount', 0))
        commission = amount * 0.029
        total = amount + commission
        
        amounts_data = [
            ['Concepto', 'Monto'],
            ['Monto del Pago:', f"${amount:.2f}"],
            ['Comisión (2.9%):', f"${commission:.2f}"],
            ['TOTAL:', f"${total:.2f}"],
        ]
        
        amounts_table_data = [[Paragraph(str(item[0]), self.styles['InvoiceNormal']),
                              Paragraph(str(item[1]), self.styles['InvoiceNormal'])] 
                             for item in amounts_data]
        
        amounts_table = Table(amounts_table_data, colWidths=[4.5*inch, 2*inch])
        amounts_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1c3d5a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f4f8')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
        ]))
        elements.append(amounts_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Información fiscal adicional
        fiscal_data = [
            ['Forma de Pago', 'Uso de CFDI'],
            ['01 - Efectivo (Tarjeta)<br/>Único pago', 'P01 - Por definir'],
        ]
        
        fiscal_table_data = [[Paragraph(str(item[0]), self.styles['InvoiceSmall']),
                             Paragraph(str(item[1]), self.styles['InvoiceSmall'])] 
                            for item in fiscal_data]
        
        fiscal_table = Table(fiscal_table_data, colWidths=[3.25*inch, 3.25*inch])
        fiscal_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(fiscal_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Generar código QR con información de verificación
        qr_data = f"MU-{transaction_data.get('invoice_number', 'N/A')}-{transaction_data.get('id', 'N/A')}"
        qr_image = self.generate_qr_code(qr_data)
        
        # Tabla con QR y información del sello
        qr_info_data = [
            [qr_image, 
             Paragraph("<b>Código QR de Verificación</b><br/><br/>Escanea este código para verificar la autenticidad de la factura.<br/><br/><b>Sello Digital:</b> XXX1234567890<br/><b>Cadena Original:</b> ||1.0|PSE123456ABC|...<br/><b>UUID:</b> " + qr_data, 
                      self.styles['InvoiceSmall'])]
        ]
        
        qr_table = Table(qr_info_data, colWidths=[2*inch, 4.5*inch])
        qr_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e8f4f8')),
            ('PADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(qr_table)
        elements.append(Spacer(1, 0.4*inch))
        
        # Pie de página
        footer_text = f"<i>Esta factura es un comprobante de pago generado por MU.<br/>Para dudas o aclaraciones, contacte a facturacion@mu.com<br/>Documento generado el {transaction_data.get('timestamp', 'N/A')} - MU S.A. de C.V.</i>"
        elements.append(Paragraph(footer_text, self.styles['InvoiceSmall']))
        
        # Construir el PDF
        doc.build(elements)
        
        # Si se proporcionó output_path, retornar el path, sino retornar el buffer
        if output_path:
            return output_path
        else:
            buffer.seek(0)
            return buffer
