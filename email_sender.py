import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os


class EmailSender:
    """Servicio para envío de emails con facturas adjuntas"""
    
    def __init__(self, smtp_host=None, smtp_port=None, smtp_user=None, smtp_password=None):
        """
        Inicializa el servicio de email
        
        Args:
            smtp_host: Host del servidor SMTP (por defecto usa Gmail)
            smtp_port: Puerto del servidor SMTP
            smtp_user: Usuario para autenticación SMTP
            smtp_password: Contraseña para autenticación SMTP
        """
        self.smtp_host = smtp_host or os.environ.get('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = smtp_port or int(os.environ.get('SMTP_PORT', 587))
        self.smtp_user = smtp_user or os.environ.get('SMTP_USER', '')
        self.smtp_password = smtp_password or os.environ.get('SMTP_PASSWORD', '')
        self.from_email = os.environ.get('FROM_EMAIL', 'facturacion@mu.com')
        self.from_name = 'MU - Sistema de Facturación'
    
    def send_invoice_email(self, to_email, invoice_number, pdf_buffer, transaction_data):
        """
        Envía un email con la factura adjunta en PDF
        
        Args:
            to_email: Email del destinatario
            invoice_number: Número de factura
            pdf_buffer: BytesIO con el contenido del PDF
            transaction_data: Datos de la transacción para personalizar el email
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        try:
            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = f'Factura MU - {invoice_number}'
            
            # Cuerpo del email en HTML
            html_body = self._create_email_body(invoice_number, transaction_data)
            msg.attach(MIMEText(html_body, 'html'))
            
            # Adjuntar PDF
            pdf_attachment = MIMEBase('application', 'pdf')
            pdf_attachment.set_payload(pdf_buffer.read())
            encoders.encode_base64(pdf_attachment)
            pdf_attachment.add_header(
                'Content-Disposition',
                f'attachment; filename=factura-{invoice_number}.pdf'
            )
            msg.attach(pdf_attachment)
            
            # Enviar email
            if self.smtp_user and self.smtp_password:
                # Configuración real de SMTP
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
                server.quit()
                
                return {
                    'success': True,
                    'message': f'Factura enviada exitosamente a {to_email}'
                }
            else:
                # Modo simulación (desarrollo)
                print(f"[MODO DESARROLLO] Email simulado a {to_email}")
                print(f"Asunto: {msg['Subject']}")
                print(f"Adjunto: factura-{invoice_number}.pdf ({len(pdf_buffer.getvalue())} bytes)")
                
                return {
                    'success': True,
                    'message': f'Factura enviada a {to_email} (modo de desarrollo)',
                    'development_mode': True
                }
                
        except smtplib.SMTPAuthenticationError:
            return {
                'success': False,
                'message': 'Error de autenticación con el servidor de email. Verifica las credenciales SMTP.'
            }
        except smtplib.SMTPException as e:
            return {
                'success': False,
                'message': f'Error al enviar el email: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error inesperado: {str(e)}'
            }
    
    def _create_email_body(self, invoice_number, transaction_data):
        """Crea el cuerpo HTML del email"""
        amount = float(transaction_data.get('amount', 0))
        total = amount * 1.029
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #1c3d5a 0%, #2c5f7d 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 8px 8px 0 0;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                }}
                .content {{
                    background: #ffffff;
                    padding: 30px;
                    border: 1px solid #e0e0e0;
                }}
                .invoice-box {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 20px 0;
                }}
                .invoice-box h2 {{
                    color: #1c3d5a;
                    margin-top: 0;
                }}
                .detail-row {{
                    display: flex;
                    justify-content: space-between;
                    padding: 8px 0;
                    border-bottom: 1px solid #e0e0e0;
                }}
                .detail-row:last-child {{
                    border-bottom: none;
                    font-weight: bold;
                    font-size: 18px;
                    color: #1c3d5a;
                }}
                .footer {{
                    background: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    border-radius: 0 0 8px 8px;
                    font-size: 12px;
                    color: #6c757d;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background: #e8b923;
                    color: #1c3d5a;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                    margin: 15px 0;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🧾 Factura de Pago</h1>
                <p>MU - Sistema de Pagos y Facturación</p>
            </div>
            
            <div class="content">
                <p>Estimado/a <strong>{transaction_data.get('full_name', 'Cliente')}</strong>,</p>
                
                <p>Nos complace informarle que su pago ha sido procesado exitosamente. Adjunto a este correo encontrará su factura en formato PDF.</p>
                
                <div class="invoice-box">
                    <h2>Detalles de la Factura</h2>
                    <div class="detail-row">
                        <span>Número de Factura:</span>
                        <span><strong>{invoice_number}</strong></span>
                    </div>
                    <div class="detail-row">
                        <span>Fecha:</span>
                        <span>{transaction_data.get('date', 'N/A')}</span>
                    </div>
                    <div class="detail-row">
                        <span>ID de Transacción:</span>
                        <span>TXN-{transaction_data.get('id', 'N/A')}</span>
                    </div>
                    <div class="detail-row">
                        <span>Monto del Pago:</span>
                        <span>${amount:.2f}</span>
                    </div>
                    <div class="detail-row">
                        <span>Comisión (2.9%):</span>
                        <span>${(amount * 0.029):.2f}</span>
                    </div>
                    <div class="detail-row">
                        <span>Total:</span>
                        <span>${total:.2f}</span>
                    </div>
                </div>
                
                <p>La factura adjunta se ha generado automáticamente y es válida para efectos fiscales. Conserve este documento para sus registros.</p>
                
                <p style="text-align: center;">
                    <a href="#" class="button">Ver Factura Adjunta</a>
                </p>
                
                <p><strong>Nota importante:</strong> Si no solicitó esta factura o tiene alguna duda sobre esta transacción, por favor contacte a nuestro equipo de soporte inmediatamente.</p>
            </div>
            
            <div class="footer">
                <p><strong>MU S.A. de C.V.</strong></p>
                <p>Av. Tecnología #123, Col. Digital<br>
                Ciudad de México, CDMX 06600<br>
                RFC: PSE123456ABC</p>
                <p>Tel: +52 55 1234 5678 | Email: facturacion@mu.com</p>
                <p style="margin-top: 15px; font-size: 11px;">
                    Este es un correo automático, por favor no responda a este mensaje.<br>
                    Para consultas, escriba a facturacion@mu.com
                </p>
            </div>
        </body>
        </html>
        """
        
        return html
