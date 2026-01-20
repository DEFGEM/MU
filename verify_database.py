#!/usr/bin/env python3
"""
Script de verificación de guardado de transacciones
"""

import sqlite3
from datetime import datetime

def check_database():
    """Verifica el estado de la base de datos"""
    db_path = 'database/payments.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=" * 60)
        print("VERIFICACIÓN DE BASE DE DATOS - TRANSACCIONES")
        print("=" * 60)
        
        # Verificar usuarios
        cursor.execute('SELECT COUNT(*) FROM users')
        user_count = cursor.fetchone()[0]
        print(f"\n✓ Usuarios registrados: {user_count}")
        
        # Verificar tarjetas
        cursor.execute('SELECT COUNT(*) FROM cards')
        card_count = cursor.fetchone()[0]
        print(f"✓ Tarjetas en sistema: {card_count}")
        
        # Verificar transacciones totales
        cursor.execute('SELECT COUNT(*) FROM transactions')
        total_transactions = cursor.fetchone()[0]
        print(f"✓ Total de transacciones: {total_transactions}")
        
        # Transacciones autorizadas
        cursor.execute('SELECT COUNT(*) FROM transactions WHERE status = "autorizado"')
        authorized = cursor.fetchone()[0]
        print(f"  - Autorizadas: {authorized}")
        
        # Transacciones rechazadas
        cursor.execute('SELECT COUNT(*) FROM transactions WHERE status = "rechazado"')
        rejected = cursor.fetchone()[0]
        print(f"  - Rechazadas: {rejected}")
        
        # Últimas 5 transacciones
        print("\n" + "=" * 60)
        print("ÚLTIMAS 5 TRANSACCIONES")
        print("=" * 60)
        
        cursor.execute('''
            SELECT t.id, t.amount, t.status, t.timestamp, t.invoice_number, t.rfc, t.full_name
            FROM transactions t
            ORDER BY t.timestamp DESC
            LIMIT 5
        ''')
        
        transactions = cursor.fetchall()
        
        if transactions:
            for idx, txn in enumerate(transactions, 1):
                print(f"\n{idx}. Transacción ID: {txn[0]}")
                print(f"   Monto: ${txn[1]:.2f}")
                print(f"   Estado: {txn[2].upper()}")
                print(f"   Fecha: {txn[3]}")
                print(f"   Factura: {txn[4] or 'N/A'}")
                print(f"   RFC: {txn[5] or 'N/A'}")
                print(f"   Cliente: {txn[6] or 'N/A'}")
        else:
            print("\n⚠ No hay transacciones registradas")
        
        # Verificar integridad de datos
        print("\n" + "=" * 60)
        print("VERIFICACIÓN DE INTEGRIDAD")
        print("=" * 60)
        
        cursor.execute('''
            SELECT COUNT(*) FROM transactions 
            WHERE card_id IS NULL AND status = 'autorizado'
        ''')
        orphan_authorized = cursor.fetchone()[0]
        
        if orphan_authorized > 0:
            print(f"⚠ Transacciones autorizadas sin tarjeta asociada: {orphan_authorized}")
        else:
            print("✓ Todas las transacciones autorizadas tienen tarjeta asociada")
        
        cursor.execute('''
            SELECT COUNT(*) FROM transactions 
            WHERE invoice_number IS NULL AND status = 'autorizado'
        ''')
        no_invoice = cursor.fetchone()[0]
        
        if no_invoice > 0:
            print(f"⚠ Transacciones autorizadas sin número de factura: {no_invoice}")
        else:
            print("✓ Todas las transacciones autorizadas tienen número de factura")
        
        # Montos totales
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE status = 'autorizado'
        ''')
        total_amount = cursor.fetchone()[0]
        print(f"\n💰 Monto total procesado (autorizadas): ${total_amount:.2f}")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("VERIFICACIÓN COMPLETADA")
        print("=" * 60 + "\n")
        
    except sqlite3.Error as e:
        print(f"❌ Error al conectar con la base de datos: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == '__main__':
    check_database()
