#!/usr/bin/env python3
"""
Script para insertar datos de prueba en la base de datos MU
Crea transacciones de ejemplo para el usuario demo
"""

import sqlite3
from datetime import datetime, timedelta
import random

DB_PATH = 'database/payments.db'

def insert_test_transactions():
    """Inserta transacciones de prueba para demostración"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Obtener ID del usuario demo
    cursor.execute('SELECT id FROM users WHERE username = ?', ('demo',))
    user_result = cursor.fetchone()
    
    if not user_result:
        print("❌ Usuario demo no encontrado. Primero inicia la aplicación.")
        conn.close()
        return
    
    user_id = user_result[0]
    
    # Obtener algunas tarjetas de la base de datos
    cursor.execute('SELECT id, card_number, cardholder_name FROM cards LIMIT 6')
    cards = cursor.fetchall()
    
    if not cards:
        print("❌ No hay tarjetas en la base de datos.")
        conn.close()
        return
    
    print(f"✅ Usuario demo encontrado (ID: {user_id})")
    print(f"✅ Encontradas {len(cards)} tarjetas para pruebas")
    
    # Datos de prueba para transacciones
    test_transactions = [
        # Transacciones autorizadas
        {
            'amount': 1500.00,
            'status': 'autorizado',
            'card_idx': 0,
            'rfc': 'PERJ850101XXX',
            'full_name': 'Juan Pérez García',
            'days_ago': 5,
            'invoice': True
        },
        {
            'amount': 3200.50,
            'status': 'autorizado',
            'card_idx': 1,
            'rfc': 'LOPM900215ABC',
            'full_name': 'María López Martínez',
            'days_ago': 3,
            'invoice': True
        },
        {
            'amount': 850.00,
            'status': 'autorizado',
            'card_idx': 2,
            'rfc': 'ROFR780920XYZ',
            'full_name': 'Carlos Rodríguez Fernández',
            'days_ago': 2,
            'invoice': True
        },
        {
            'amount': 5000.00,
            'status': 'autorizado',
            'card_idx': 3,
            'rfc': 'GOHA850315DEF',
            'full_name': 'Ana González Hernández',
            'days_ago': 1,
            'invoice': True
        },
        {
            'amount': 250.00,
            'status': 'autorizado',
            'card_idx': 4,
            'rfc': 'SARP920710GHI',
            'full_name': 'Pedro Sánchez Ramírez',
            'days_ago': 0,
            'invoice': True
        },
        # Transacciones rechazadas
        {
            'amount': 500.00,
            'status': 'rechazado',
            'card_idx': 5,
            'rfc': 'TOTD880525JKL',
            'full_name': 'Laura Torres Díaz',
            'days_ago': 4,
            'invoice': False,
            'rejection_reason': 'Fondos insuficientes'
        },
        {
            'amount': 2000.00,
            'status': 'rechazado',
            'card_idx': 2,
            'rfc': 'ROFR780920XYZ',
            'full_name': 'Carlos Rodríguez Fernández',
            'days_ago': 6,
            'invoice': False,
            'rejection_reason': 'Fecha de expiración inválida o tarjeta expirada'
        },
    ]
    
    inserted = 0
    
    for i, tx in enumerate(test_transactions):
        try:
            # Calcular timestamp
            timestamp = datetime.now() - timedelta(days=tx['days_ago'])
            
            # Generar número de factura si es autorizada
            invoice_number = None
            if tx['invoice']:
                invoice_number = f"F{timestamp.strftime('%Y%m%d%H%M%S')}{user_id}{i}"
            
            # Obtener card_id
            card_idx = tx['card_idx']
            card_id = cards[card_idx][0] if card_idx < len(cards) else None
            
            # Insertar transacción
            if tx['status'] == 'autorizado':
                cursor.execute('''
                    INSERT INTO transactions (amount, status, card_id, user_id, rfc, full_name, invoice_number, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    tx['amount'],
                    tx['status'],
                    card_id,
                    user_id,
                    tx['rfc'],
                    tx['full_name'],
                    invoice_number,
                    timestamp
                ))
            else:
                cursor.execute('''
                    INSERT INTO transactions (amount, status, rejection_reason, card_id, user_id, rfc, full_name, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    tx['amount'],
                    tx['status'],
                    tx.get('rejection_reason', 'Error desconocido'),
                    card_id,
                    user_id,
                    tx['rfc'],
                    tx['full_name'],
                    timestamp
                ))
            
            inserted += 1
            status_icon = "✅" if tx['status'] == 'autorizado' else "❌"
            print(f"{status_icon} Transacción {tx['status']}: ${tx['amount']:.2f} - {tx['full_name']}")
            
        except Exception as e:
            print(f"❌ Error al insertar transacción {i+1}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✨ ¡Completado! Se insertaron {inserted}/{len(test_transactions)} transacciones de prueba")
    print(f"\n📊 Resumen:")
    print(f"   • Transacciones autorizadas: {sum(1 for tx in test_transactions if tx['status'] == 'autorizado')}")
    print(f"   • Transacciones rechazadas: {sum(1 for tx in test_transactions if tx['status'] == 'rechazado')}")
    print(f"\n🔗 Ahora puedes ver el historial en: http://127.0.0.1:5000/history")

if __name__ == '__main__':
    print("🔄 Insertando datos de prueba en la base de datos...")
    print("=" * 60)
    insert_test_transactions()
