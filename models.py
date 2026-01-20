from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import re

class Database:
    def __init__(self, db_path='database/payments.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de tarjetas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_number TEXT UNIQUE NOT NULL,
                cardholder_name TEXT NOT NULL,
                expiry_date TEXT NOT NULL,
                cvv TEXT NOT NULL,
                balance REAL NOT NULL DEFAULT 0.0,
                is_verified BOOLEAN DEFAULT TRUE,
                attempts_count INTEGER DEFAULT 0,
                last_attempt TIMESTAMP,
                is_blocked BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de transacciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                status TEXT NOT NULL,
                rejection_reason TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                card_id INTEGER,
                user_id INTEGER,
                rfc TEXT,
                full_name TEXT,
                invoice_number TEXT,
                FOREIGN KEY (card_id) REFERENCES cards (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Insertar tarjetas de prueba
        self.insert_test_cards()
    
    def insert_test_cards(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Verificar si ya existen tarjetas
        cursor.execute('SELECT COUNT(*) FROM cards')
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        # Tarjetas de prueba (números válidos usando algoritmo de Luhn)
        test_cards = [
            {
                'card_number': '4532015112830366',  # Visa válida
                'cardholder_name': 'Juan Pérez García',
                'expiry_date': '12/26',
                'cvv': '123',
                'balance': 5000.00,
                'is_verified': True,
                'attempts_count': 0,
                'is_blocked': False
            },
            {
                'card_number': '5425233430109903',  # Mastercard válida
                'cardholder_name': 'María López Martínez',
                'expiry_date': '08/25',
                'cvv': '456',
                'balance': 12500.50,
                'is_verified': True,
                'attempts_count': 1,
                'is_blocked': False
            },
            {
                'card_number': '4000056655665556',  # Visa válida
                'cardholder_name': 'Carlos Rodríguez Fernández',
                'expiry_date': '03/24',  # Expirada
                'cvv': '789',
                'balance': 3000.00,
                'is_verified': True,
                'attempts_count': 2,
                'is_blocked': False
            },
            {
                'card_number': '5555555555554444',  # Mastercard válida
                'cardholder_name': 'Ana González Hernández',
                'expiry_date': '11/27',
                'cvv': '321',
                'balance': 800.00,  # Balance insuficiente
                'is_verified': True,
                'attempts_count': 0,
                'is_blocked': False
            },
            {
                'card_number': '4111111111111111',  # Visa válida
                'cardholder_name': 'Pedro Sánchez Ramírez',
                'expiry_date': '06/26',
                'cvv': '654',
                'balance': 15000.00,
                'is_verified': False,  # No verificada
                'attempts_count': 0,
                'is_blocked': False
            },
            {
                'card_number': '378282246310005',   # American Express válida
                'cardholder_name': 'Laura Torres Díaz',
                'expiry_date': '09/25',
                'cvv': '9876',
                'balance': 7500.00,
                'is_verified': True,
                'attempts_count': 3,  # Intentos excedidos
                'is_blocked': True
            },
            {
                'card_number': '6011000990139424',  # Discover válida
                'cardholder_name': 'Diego Morales Flores',
                'expiry_date': '01/28',
                'cvv': '147',
                'balance': 22000.00,
                'is_verified': True,
                'attempts_count': 0,
                'is_blocked': False
            },
            {
                'card_number': '3530111333300000',  # JCB válida
                'cardholder_name': 'Sofía Vargas Cruz',
                'expiry_date': '05/27',
                'cvv': '258',
                'balance': 9500.00,
                'is_verified': True,
                'attempts_count': 1,
                'is_blocked': False
            },
            {
                'card_number': '4916487051416887',  # Visa válida
                'cardholder_name': 'Ricardo Mendoza Silva',
                'expiry_date': '10/24',  # Expirada
                'cvv': '369',
                'balance': 4500.00,
                'is_verified': True,
                'attempts_count': 2,
                'is_blocked': False
            },
            {
                'card_number': '5105105105105100',  # Mastercard válida
                'cardholder_name': 'Valeria Aguilar Ortega',
                'expiry_date': '12/29',
                'cvv': '741',
                'balance': 18000.00,
                'is_verified': True,
                'attempts_count': 0,
                'is_blocked': False
            }
        ]
        
        for card in test_cards:
            cursor.execute('''
                INSERT INTO cards (card_number, cardholder_name, expiry_date, cvv, 
                                 balance, is_verified, attempts_count, is_blocked)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                card['card_number'],
                card['cardholder_name'],
                card['expiry_date'],
                card['cvv'],
                card['balance'],
                card['is_verified'],
                card['attempts_count'],
                card['is_blocked']
            ))
        
        conn.commit()
        conn.close()

class Validator:
    @staticmethod
    def validate_card_number(card_number):
        """Valida el número de tarjeta usando el algoritmo de Luhn"""
        if not card_number or not card_number.isdigit():
            return False
        
        digits = [int(d) for d in card_number]
        check_digit = digits.pop()
        digits.reverse()
        
        for i in range(0, len(digits), 2):
            digits[i] *= 2
            if digits[i] > 9:
                digits[i] -= 9
        
        total = sum(digits) + check_digit
        return total % 10 == 0
    
    @staticmethod
    def validate_expiry_date(expiry_date):
        """Valida que la fecha de expiración no haya pasado"""
        try:
            month, year = map(int, expiry_date.split('/'))
            current_year = datetime.now().year % 100
            current_month = datetime.now().month
            
            if year < current_year or (year == current_year and month < current_month):
                return False
            return True
        except:
            return False
    
    @staticmethod
    def validate_cvv(cvv, card_number):
        """Valida el formato del CVV"""
        if not cvv or not cvv.isdigit():
            return False
        
        # American Express tiene CVV de 4 dígitos
        if card_number.startswith('34') or card_number.startswith('37'):
            return len(cvv) == 4
        else:
            return len(cvv) == 3
    
    @staticmethod
    def validate_rfc(rfc):
        """Valida el formato del RFC (13 caracteres para personas físicas, 12 para morales)"""
        if not rfc:
            return False
        
        rfc = rfc.strip().upper()
        
        # RFC de persona física: 4 letras + 6 números + 3 caracteres
        pattern_pf = r'^[A-Z]{4}[0-9]{6}[A-Z0-9]{3}$'
        
        # RFC de persona moral: 3 letras + 6 números + 3 caracteres
        pattern_pm = r'^[A-Z]{3}[0-9]{6}[A-Z0-9]{3}$'
        
        return bool(re.match(pattern_pf, rfc)) or bool(re.match(pattern_pm, rfc))
    
    @staticmethod
    def validate_amount(amount):
        """Valida el monto de la transacción"""
        try:
            amount = float(amount)
            return 0 < amount <= 10000  # Límite de $10,000
        except:
            return False
    
    @staticmethod
    def validate_email(email):
        """Valida el formato del correo electrónico"""
        if not email:
            return False
        
        email = email.strip()
        # Patrón de regex para validar email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))
    
    @staticmethod
    def validate_name(name):
        """Valida que el nombre solo contenga letras y espacios"""
        if not name:
            return False
        
        name = name.strip()
        # Solo letras (incluyendo acentos y ñ), espacios y guiones
        name_pattern = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s-]+$'
        return bool(re.match(name_pattern, name)) and len(name) >= 3

class PaymentRules:
    def __init__(self, db):
        self.db = db
        self.validator = Validator()
    
    def check_authorization(self, card_number, expiry_date, cvv, amount, rfc=""):
        """Aplica todas las reglas de autorización"""
        # Buscar tarjeta en la base de datos
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM cards WHERE card_number = ?', (card_number,))
        card = cursor.fetchone()
        
        if not card:
            conn.close()
            return {
                'authorized': False,
                'reason': 'Tarjeta no verificada o no existe en el sistema'
            }
        
        card_dict = {
            'id': card[0],
            'card_number': card[1],
            'cardholder_name': card[2],
            'expiry_date': card[3],
            'cvv': card[4],
            'balance': card[5],
            'is_verified': card[6],
            'attempts_count': card[7],
            'last_attempt': card[8],
            'is_blocked': card[9]
        }
        
        # Aplicar reglas de autorización
        rules = [
            (self._check_card_verified, card_dict),
            (self._check_expiry_date, expiry_date),
            (self._check_cvv, cvv, card_dict),
            (self._check_attempts, card_dict),
            (self._check_balance, card_dict, amount),
            (self._check_transaction_limit, amount),
            (self._check_velocity, card_dict)
        ]
        
        for rule in rules:
            result = rule[0](*rule[1:])
            if not result['authorized']:
                # Incrementar intentos fallidos
                cursor.execute('''
                    UPDATE cards 
                    SET attempts_count = attempts_count + 1, 
                        last_attempt = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (card_dict['id'],))
                conn.commit()
                conn.close()
                return result
        
        # Si pasa todas las reglas, autorizar
        conn.close()
        return {'authorized': True, 'reason': None}
    
    def _check_card_verified(self, card):
        """Regla 1: Tarjeta verificada"""
        if not card['is_verified']:
            return {
                'authorized': False,
                'reason': 'Tarjeta no verificada en el sistema'
            }
        return {'authorized': True}
    
    def _check_expiry_date(self, expiry_date):
        """Regla 2: Fecha de expiración válida"""
        if not self.validator.validate_expiry_date(expiry_date):
            return {
                'authorized': False,
                'reason': 'Fecha de expiración inválida o tarjeta expirada'
            }
        return {'authorized': True}
    
    def _check_cvv(self, cvv, card):
        """Regla 3: CVV correcto"""
        if cvv != card['cvv'] or not self.validator.validate_cvv(cvv, card['card_number']):
            return {
                'authorized': False,
                'reason': 'Código de seguridad (CVV) incorrecto'
            }
        return {'authorized': True}
    
    def _check_attempts(self, card):
        """Regla 4: Intentos no excedidos"""
        if card['attempts_count'] >= 3:
            return {
                'authorized': False,
                'reason': 'Límite de intentos excedido. Tarjeta bloqueada temporalmente'
            }
        return {'authorized': True}
    
    def _check_balance(self, card, amount):
        """Regla 5: Fondos suficientes"""
        if card['balance'] < float(amount):
            return {
                'authorized': False,
                'reason': f'Fondos insuficientes. Balance disponible: ${card["balance"]:.2f}'
            }
        return {'authorized': True}
    
    def _check_transaction_limit(self, amount):
        """Regla 6: Límite de transacción"""
        if float(amount) > 10000:
            return {
                'authorized': False,
                'reason': 'Monto excede el límite máximo de transacción ($10,000)'
            }
        return {'authorized': True}
    
    def _check_velocity(self, card):
        """Regla 7: Verificación de velocidad (máximo 5 transacciones por hora)"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        one_hour_ago = datetime.now() - timedelta(hours=1)
        cursor.execute('''
            SELECT COUNT(*) FROM transactions 
            WHERE card_id = ? AND timestamp > ? AND status = 'autorizado'
        ''', (card['id'], one_hour_ago.isoformat()))
        
        transaction_count = cursor.fetchone()[0]
        conn.close()
        
        if transaction_count >= 5:
            return {
                'authorized': False,
                'reason': 'Límite de transacciones por hora excedido (máximo 5)'
            }
        return {'authorized': True}