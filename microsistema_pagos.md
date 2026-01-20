# Microsistema de Pago y Facturación

## Arquitectura del Sistema

### Estructura del Proyecto
```
/mnt/okcomputer/output/
├── app.py                 # Aplicación Flask principal
├── database.py            # Gestión de base de datos
├── auth.py               # Sistema de autenticación
├── payment.py            # Lógica de pagos
├── models.py             # Modelos de datos
├── requirements.txt      # Dependencias
├── static/               # Archivos estáticos
│   ├── css/
│   │   └── styles.css    # Estilos principales
│   ├── js/
│   │   └── main.js       # JavaScript
│   └── images/           # Imágenes
├── templates/            # Plantillas HTML
│   ├── base.html         # Base template
│   ├── login.html        # Login
│   ├── dashboard.html    # Panel principal
│   ├── payment.html      # Formulario de pago
│   ├── invoice.html      # Factura
│   └── history.html      # Historial
└── database/
    └── payments.db       # Base de datos SQLite
```

### Modelos de Datos

#### Usuario
- id (clave primaria)
- username
- email
- password_hash
- created_at

#### Tarjeta
- id (clave primaria)
- card_number
- cardholder_name
- expiry_date
- cvv
- balance
- is_verified
- attempts_count
- last_attempt
- user_id (opcional)

#### Transacción
- id (clave primaria)
- amount
- status (autorizado/rechazado)
- rejection_reason
- timestamp
- card_id
- user_id
- rfc

### Reglas de Autorización

1. **Tarjeta verificada**: La tarjeta debe existir en la base de datos
2. **Fecha no expirada**: La fecha de expiración debe ser posterior a la actual
3. **CVV correcto**: El código de seguridad debe coincidir
4. **Intentos no excedidos**: Máximo 3 intentos por tarjeta
5. **Fondos suficientes**: El balance debe cubrir el monto del pago
6. **Límite de transacción**: Máximo $10,000 por transacción
7. **Verificación de velocidad**: Máximo 5 transacciones por tarjeta en 1 hora
8. **RFC válido**: Formato correcto de RFC (13 caracteres para personas, 12 para empresas)
9. **Nombre coincidente**: El nombre debe coincidir con el titular de la tarjeta

### Funcionalidades Adicionales

1. **Sistema de Login**: Autenticación segura con hash de contraseñas
2. **Historial de Transacciones**: Visualización de pagos anteriores
3. **Generación de Facturas**: PDF con datos del pago y RFC
4. **Validaciones en Tiempo Real**: Feedback inmediato en el formulario
5. **Diseño Responsivo**: Compatible con dispositivos móviles
6. **Logs de Auditoría**: Registro de todos los intentos de pago
7. **Bloqueo de Tarjetas**: Suspensión tras múltiples intentos fallidos

### Base de Datos de Tarjetas Preexistentes (10 tarjetas)

Crear tarjetas de prueba con:
- Números válidos (pasando algoritmo de Luhn)
- Fechas de expiración variadas (algunas expiradas)
- Balances diferentes
- Estados verified/unverified
- Diferentes números de intentos

### Seguridad

- Hash de contraseñas con werkzeug
- Validación de tarjetas con algoritmo de Luhn
- Sanitización de entrada de datos
- Protección CSRF
- Límites de intentos
- Encriptación de datos sensibles en la base de datos