from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import sqlite3
import os
import re
from functools import wraps

from models import Database, Validator, PaymentRules
from invoice_generator import InvoiceGenerator
from email_sender import EmailSender

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

db = Database()
validator = Validator()
payment_rules = PaymentRules(db)
invoice_generator = InvoiceGenerator()
email_sender = EmailSender()

# Decorador para requerir login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor inicia sesión para continuar', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Rutas de autenticación
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Por favor completa todos los campos', 'error')
            return render_template('login.html')
        
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, username))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['email'] = user[2]
            
            # Crear usuario de prueba si no existe
            if username == 'demo' and check_password_hash(user[3], 'demo123'):
                flash('Bienvenido al sistema de pagos. Usa el usuario: demo y contraseña: demo123', 'success')
            else:
                flash(f'Bienvenido, {user[1]}!', 'success')
            
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validaciones
        if not all([username, email, password, confirm_password]):
            flash('Por favor completa todos los campos', 'error')
            return render_template('login.html')
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'error')
            return render_template('login.html')
        
        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres', 'error')
            return render_template('login.html')
        
        # Validar formato de email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            flash('Por favor ingresa un email válido', 'error')
            return render_template('login.html')
        
        password_hash = generate_password_hash(password)
        
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
            ''', (username, email, password_hash))
            conn.commit()
            conn.close()
            
            flash('Usuario registrado exitosamente. Por favor inicia sesión.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            flash('El usuario o email ya existe', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada exitosamente', 'success')
    return redirect(url_for('login'))

# Rutas principales
@app.route('/dashboard')
@login_required
def dashboard():
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    
    # Estadísticas del usuario
    cursor.execute('''
        SELECT COUNT(*), COALESCE(SUM(amount), 0)
        FROM transactions 
        WHERE user_id = ? AND status = 'autorizado'
    ''', (session['user_id'],))
    stats = cursor.fetchone()
    
    # Últimas transacciones
    cursor.execute('''
        SELECT t.*, c.card_number, c.cardholder_name
        FROM transactions t
        LEFT JOIN cards c ON t.card_id = c.id
        WHERE t.user_id = ?
        ORDER BY t.timestamp DESC
        LIMIT 10
    ''', (session['user_id'],))
    transactions = cursor.fetchall()
    
    conn.close()
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         transactions=transactions,
                         username=session['username'])

@app.route('/payment')
@login_required
def payment():
    return render_template('payment.html', username=session['username'])

@app.route('/history')
@login_required
def history():
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT t.*, c.card_number, c.cardholder_name
        FROM transactions t
        LEFT JOIN cards c ON t.card_id = c.id
        WHERE t.user_id = ?
        ORDER BY t.timestamp DESC
    ''', (session['user_id'],))
    transactions = cursor.fetchall()
    
    conn.close()
    
    return render_template('history.html', transactions=transactions, username=session['username'])

# API endpoints
@app.route('/api/validate-card', methods=['POST'])
@login_required
def validate_card():
    data = request.get_json()
    card_number = data.get('card_number', '').replace(' ', '')
    
    is_valid = validator.validate_card_number(card_number)
    
    # Detectar tipo de tarjeta
    card_type = 'unknown'
    if card_number.startswith('4'):
        card_type = 'visa'
    elif card_number.startswith('5'):
        card_type = 'mastercard'
    elif card_number.startswith('3'):
        card_type = 'amex'
    elif card_number.startswith('6'):
        card_type = 'discover'
    
    return jsonify({
        'valid': is_valid,
        'card_type': card_type,
        'masked': '**** **** **** ' + card_number[-4:] if len(card_number) >= 4 else card_number
    })

@app.route('/api/process-payment', methods=['POST'])
@login_required
def process_payment():
    data = request.get_json()
    
    # Extraer datos
    full_name = data.get('full_name', '').strip()
    rfc = data.get('rfc', '').strip()
    card_number = data.get('card_number', '').replace(' ', '')
    expiry_date = data.get('expiry_date', '').strip()
    cvv = data.get('cvv', '').strip()
    amount = data.get('amount', 0)
    
    # Validaciones básicas
    errors = []
    
    # Validar que el nombre no esté vacío y tenga al menos 2 palabras (nombre y apellido)
    if not full_name:
        errors.append('El nombre completo es requerido')
    elif len(full_name.split()) < 2:
        errors.append('Ingresa tu nombre completo (nombre y apellido)')
    elif not validator.validate_name(full_name):
        errors.append('El nombre solo debe contener letras y espacios')
    
    if not rfc:
        errors.append('El RFC es requerido')
    elif not validator.validate_rfc(rfc):
        errors.append('RFC inválido. Debe tener el formato correcto (12 o 13 caracteres)')
    
    if not card_number:
        errors.append('El número de tarjeta es requerido')
    elif len(card_number) < 13 or len(card_number) > 19:
        errors.append('Número de tarjeta debe tener entre 13 y 19 dígitos')
    elif not card_number.isdigit():
        errors.append('Número de tarjeta debe contener solo dígitos')
    
    if not expiry_date:
        errors.append('La fecha de expiración es requerida')
    elif not validator.validate_expiry_date(expiry_date):
        errors.append('Fecha de expiración inválida o tarjeta expirada')
    
    if not cvv:
        errors.append('El código CVV es requerido')
    elif not validator.validate_cvv(cvv, card_number):
        errors.append('CVV inválido')
    
    if not amount or amount == 0:
        errors.append('El monto es requerido')
    elif not validator.validate_amount(amount):
        errors.append('Monto inválido. Debe ser mayor a 0 y menor a $10,000')
    
    if errors:
        return jsonify({
            'success': False,
            'errors': errors
        }), 400
    
    # Manejo de excepciones para guardado de datos
    try:
        # Buscar o crear la tarjeta
        card = get_or_create_card(card_number, full_name, expiry_date, cvv)
        
        # Abrir conexión a la base de datos
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        if card and card[0]:  # Si la tarjeta existe en BD con ID
            # Verificar reglas de autorización
            auth_result = payment_rules.check_authorization(card_number, expiry_date, cvv, amount, rfc)
        else:
            # Para tarjetas nuevas/inventadas, autorizar automáticamente
            auth_result = {'authorized': True, 'reason': None}
        
        if auth_result['authorized']:
            # Generar número de factura antes de insertar
            invoice_num = generate_invoice_number()
            
            # Procesar pago exitoso
            cursor.execute('''
                INSERT INTO transactions (amount, status, card_id, user_id, rfc, full_name, invoice_number)
                VALUES (?, 'autorizado', ?, ?, ?, ?, ?)
            ''', (
                float(amount),
                card[0] if card else None,
                session['user_id'],
                rfc,
                full_name,
                invoice_num
            ))
            
            # Obtener el ID de la transacción ANTES de cerrar la conexión
            transaction_id = cursor.lastrowid
            
            # Actualizar balance de la tarjeta si existe en BD
            if card and card[0]:
                new_balance = card[5] - float(amount)
                cursor.execute('UPDATE cards SET balance = ?, attempts_count = 0 WHERE id = ?', 
                             (new_balance, card[0]))
            
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': 'Pago autorizado exitosamente',
                'transaction_id': transaction_id,
                'invoice_number': invoice_num
            })
        else:
            # Registrar transacción fallida
            cursor.execute('''
                INSERT INTO transactions (amount, status, rejection_reason, card_id, user_id, rfc, full_name)
                VALUES (?, 'rechazado', ?, ?, ?, ?, ?)
            ''', (
                float(amount),
                auth_result['reason'],
                card[0] if card else None,
                session['user_id'],
                rfc,
                full_name
            ))
            
            # Obtener el ID de la transacción ANTES de cerrar la conexión
            transaction_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': False,
                'errors': [auth_result['reason']],
                'transaction_id': transaction_id
            }), 400
    
    except sqlite3.Error as e:
        # Manejo de errores de base de datos
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return jsonify({
            'success': False,
            'errors': [f'Error al procesar la transacción: {str(e)}']
        }), 500
    except Exception as e:
        # Manejo de cualquier otro error
        if 'conn' in locals() and conn:
            conn.rollback()
            conn.close()
        return jsonify({
            'success': False,
            'errors': [f'Error inesperado: {str(e)}']
        }), 500

def get_or_create_card(card_number, cardholder_name, expiry_date, cvv):
    """
    Busca una tarjeta en la base de datos. Si no existe, crea una temporal/virtual.
    Esto permite usar tarjetas inventadas para pruebas.
    
    Args:
        card_number: Número de tarjeta
        cardholder_name: Nombre del titular
        expiry_date: Fecha de expiración
        cvv: Código CVV
    
    Returns:
        tuple: Datos de la tarjeta (como una fila de base de datos) o None para tarjeta virtual
    """
    try:
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        # Buscar tarjeta existente
        cursor.execute('SELECT * FROM cards WHERE card_number = ?', (card_number,))
        card = cursor.fetchone()
        conn.close()
        
        if card:
            # Tarjeta encontrada en BD
            return card
        else:
            # Tarjeta no existe - retornar None para indicar que es virtual
            # El flujo de pago autorizar automáticamente sin validar balance
            return None
            
    except Exception as e:
        print(f"Error al buscar tarjeta: {e}")
        return None

def generate_invoice_number():
    """Genera un número de factura único"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return f'F{timestamp}{session["user_id"]}'

@app.route('/api/cards/search')
@login_required
def search_cards():
    query = request.args.get('q', '')
    
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT card_number, cardholder_name, expiry_date, balance, is_verified, is_blocked
        FROM cards
        WHERE cardholder_name LIKE ? OR card_number LIKE ?
        LIMIT 10
    ''', (f'%{query}%', f'%{query}%'))
    
    cards = cursor.fetchall()
    conn.close()
    
    result = []
    for card in cards:
        result.append({
            'card_number': card[0],
            'cardholder_name': card[1],
            'expiry_date': card[2],
            'balance': card[3],
            'is_verified': card[4],
            'is_blocked': card[5],
            'masked': '**** **** **** ' + card[0][-4:]
        })
    
    return jsonify(result)

@app.route('/invoice/<int:transaction_id>')
@login_required
def invoice(transaction_id):
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT t.*, c.card_number, c.cardholder_name
        FROM transactions t
        LEFT JOIN cards c ON t.card_id = c.id
        WHERE t.id = ? AND t.user_id = ?
    ''', (transaction_id, session['user_id']))
    
    transaction = cursor.fetchone()
    conn.close()
    
    if not transaction:
        flash('Transacción no encontrada', 'error')
        return redirect(url_for('history'))
    
    # Solo mostrar factura para transacciones autorizadas
    if transaction[2] != 'autorizado':
        flash('Solo se pueden generar facturas para transacciones autorizadas', 'warning')
        return redirect(url_for('history'))
    
    return render_template('invoice.html', transaction=transaction, username=session['username'])

@app.route('/api/invoice/<int:transaction_id>')
@login_required
def api_invoice(transaction_id):
    """API endpoint para obtener datos de factura en JSON"""
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT t.*, c.card_number, c.cardholder_name
        FROM transactions t
        LEFT JOIN cards c ON t.card_id = c.id
        WHERE t.id = ? AND t.user_id = ?
    ''', (transaction_id, session['user_id']))
    
    transaction = cursor.fetchone()
    conn.close()
    
    if not transaction or transaction[2] != 'autorizado':
        return jsonify({'error': 'Transacción no encontrada o no autorizada'}), 404
    
    return jsonify({
        'id': transaction[0],
        'amount': float(transaction[1]),
        'status': transaction[2],
        'timestamp': transaction[4],
        'card_number': transaction[10],
        'cardholder_name': transaction[11],
        'rfc': transaction[6],
        'full_name': transaction[7],
        'invoice_number': transaction[9],
        'commission': float(transaction[1]) * 0.029,
        'total': float(transaction[1]) * 1.029
    })

@app.route('/api/invoice/<int:transaction_id>/email', methods=['POST'])
@login_required
def email_invoice(transaction_id):
    """Endpoint para enviar factura por email"""
    data = request.get_json()
    email = data.get('email', session.get('email'))
    
    # Validar email
    if not email:
        return jsonify({'error': 'Email no proporcionado'}), 400
    
    if not validator.validate_email(email):
        return jsonify({'error': 'Email inválido. Por favor verifica el formato'}), 400
    
    try:
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT t.*, c.card_number, c.cardholder_name
            FROM transactions t
            LEFT JOIN cards c ON t.card_id = c.id
            WHERE t.id = ? AND t.user_id = ? AND t.status = 'autorizado'
        ''', (transaction_id, session['user_id']))
        
        transaction = cursor.fetchone()
        conn.close()
        
        if not transaction:
            return jsonify({'error': 'Transacción no encontrada'}), 404
        
        # Preparar datos de la transacción
        timestamp = transaction[4]
        date_part = timestamp[:10] if timestamp else 'N/A'
        time_part = timestamp[11:19] if timestamp else 'N/A'
        
        transaction_data = {
            'id': transaction[0],
            'amount': float(transaction[1]),
            'status': 'Autorizado',
            'timestamp': timestamp,
            'date': date_part,
            'time': time_part,
            'card_last4': transaction[10][-4:] if transaction[10] else 'N/A',
            'cardholder_name': transaction[11] or 'N/A',
            'rfc': transaction[6] or 'N/A',
            'full_name': transaction[7] or 'N/A',
            'invoice_number': transaction[9] or 'N/A'
        }
        
        # Generar PDF
        pdf_buffer = invoice_generator.generate_invoice_pdf(transaction_data)
        pdf_buffer.seek(0)
        
        # Enviar email
        result = email_sender.send_invoice_email(
            to_email=email,
            invoice_number=transaction_data['invoice_number'],
            pdf_buffer=pdf_buffer,
            transaction_data=transaction_data
        )
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify({'error': result['message']}), 500
            
    except Exception as e:
        return jsonify({'error': f'Error al enviar factura: {str(e)}'}), 500

@app.route('/api/invoice/<int:transaction_id>/download')
@login_required
def download_invoice(transaction_id):
    """Endpoint para descargar factura en PDF"""
    try:
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT t.*, c.card_number, c.cardholder_name
            FROM transactions t
            LEFT JOIN cards c ON t.card_id = c.id
            WHERE t.id = ? AND t.user_id = ? AND t.status = 'autorizado'
        ''', (transaction_id, session['user_id']))
        
        transaction = cursor.fetchone()
        conn.close()
        
        if not transaction:
            return jsonify({'error': 'Transacción no encontrada'}), 404
        
        # Preparar datos de la transacción
        timestamp = transaction[4]
        date_part = timestamp[:10] if timestamp else 'N/A'
        time_part = timestamp[11:19] if timestamp else 'N/A'
        
        transaction_data = {
            'id': transaction[0],
            'amount': float(transaction[1]),
            'status': 'Autorizado',
            'timestamp': timestamp,
            'date': date_part,
            'time': time_part,
            'card_last4': transaction[10][-4:] if transaction[10] else 'N/A',
            'cardholder_name': transaction[11] or 'N/A',
            'rfc': transaction[6] or 'N/A',
            'full_name': transaction[7] or 'N/A',
            'invoice_number': transaction[9] or 'N/A'
        }
        
        # Generar PDF
        pdf_buffer = invoice_generator.generate_invoice_pdf(transaction_data)
        pdf_buffer.seek(0)
        
        # Enviar el archivo PDF
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'factura-{transaction_data["invoice_number"]}.pdf'
        )
        
    except Exception as e:
        return jsonify({'error': f'Error al generar PDF: {str(e)}'}), 500


# Crear usuario de demo al iniciar
if __name__ == '__main__':
    # Verificar si existe usuario demo
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE username = ?', ('demo',))
    if not cursor.fetchone():
        password_hash = generate_password_hash('demo123')
        cursor.execute('''
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
        ''', ('demo', 'demo@example.com', password_hash))
        conn.commit()
    
    conn.close()
    
    app.run(debug=True, host='0.0.0.0', port=5000)