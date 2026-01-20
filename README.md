<<<<<<< HEAD
# PaySecure - Microsistema de Pago y Facturación

Un sistema completo de procesamiento de pagos y facturación con diseño moderno y elegante, construido con Flask.

## Características

### ✅ Funcionalidades Implementadas

1. **Sistema de Autenticación**
   - Login seguro con hash de contraseñas
   - Registro de usuarios
   - Sesiones de usuario persistentes
   - Usuario demo incluido (demo/demo123)

2. **Base de Datos Completa**
   - 10 tarjetas de prueba preexistentes
   - Diferentes escenarios de validación
   - Historial de transacciones completo

3. **Reglas de Autorización de Pago (9 reglas)**
   - ✅ Tarjeta verificada
   - ✅ Fecha de expiración válida
   - ✅ CVV correcto
   - ✅ Intentos no excedidos (máximo 3)
   - ✅ Fondos suficientes
   - ✅ Límite de transacción ($10,000)
   - ✅ Verificación de velocidad (máximo 5 por hora)
   - ✅ RFC válido (formato correcto)
   - ✅ Nombre coincidente

4. **Validaciones Avanzadas**
   - Algoritmo de Luhn para tarjetas
   - Validación de fecha de expiración
   - Validación de CVV (3-4 dígitos)
   - Validación de RFC (12-13 caracteres)
   - Límites de monto

5. **Interfaz de Usuario Moderna**
   - Diseño minimalista y elegante
   - Animaciones suaves con Anime.js
   - Previsualización de tarjeta en tiempo real
   - Validación en tiempo real
   - Diseño responsive (mobile-first)

6. **Sistema de Facturación**
   - Generación de facturas con RFC
   - Historial completo de transacciones
   - Estados de transacción detallados
   - Exportación a PDF (simulada)

7. **Seguridad**
   - Encriptación de contraseñas
   - Validación del lado del servidor
   - Protección CSRF
   - Sanitización de entrada de datos

## Tecnologías Utilizadas

### Backend
- **Flask**: Framework web de Python
- **SQLite**: Base de datos ligera
- **Werkzeug**: Seguridad y autenticación

### Frontend
- **HTML5**: Estructura semántica
- **Tailwind CSS**: Framework de CSS utility-first
- **JavaScript ES6+**: Lógica del cliente
- **Anime.js**: Animaciones suaves
- **Font Awesome**: Iconos vectoriales

### Diseño
- **Paleta de colores profesional**: Navy, Sage, Gold
- **Tipografía moderna**: Inter + Playfair Display
- **Diseño responsive**: Mobile-first
- **Micro-animaciones**: Feedback visual

## Instalación

1. **Clonar el proyecto**
   ```bash
   cd /mnt/okcomputer/output
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar la aplicación**
   ```bash
   python app.py
   ```

4. **Acceder al sistema**
   - URL: `http://localhost:5000`
   - Usuario demo: `demo`
   - Contraseña demo: `demo123`

## Estructura del Proyecto

```
PaySecure/
├── app.py                 # Aplicación Flask principal
├── models.py              # Modelos de datos y lógica de negocio
├── database/              # Base de datos SQLite
├── static/                # Archivos estáticos
│   ├── css/
│   │   └── styles.css    # Estilos personalizados
│   └── js/
│       ├── main.js       # JavaScript principal
│       └── payment.js    # Lógica del formulario de pago
├── templates/            # Plantillas HTML
│   ├── base.html         # Template base
│   ├── login.html        # Login
│   ├── dashboard.html    # Dashboard
│   ├── payment.html      # Formulario de pago
│   ├── history.html      # Historial
│   └── invoice.html      # Factura
├── requirements.txt      # Dependencias de Python
└── README.md            # Documentación
```

## Tarjetas de Prueba Preexistentes (10 tarjetas)

El sistema incluye 10 tarjetas de prueba con diferentes escenarios:

1. **Tarjeta 1**: Visa válida, balance $5,000 ✅
2. **Tarjeta 2**: Mastercard válida, balance $12,500 ✅
3. **Tarjeta 3**: Visa expirada ❌
4. **Tarjeta 4**: Mastercard con fondos insuficientes ❌
5. **Tarjeta 5**: Visa no verificada ❌
6. **Tarjeta 6**: Amex con intentos excedidos ❌
7. **Tarjeta 7**: Discover válida, balance $22,000 ✅
8. **Tarjeta 8**: JCB válida, balance $9,500 ✅
9. **Tarjeta 9**: Visa expirada ❌
10. **Tarjeta 10**: Mastercard válida, balance $18,000 ✅

### Ejemplos de Tarjetas Válidas (usar en el formulario):

**Tarjeta Visa Válida:**
- Número: `4532015112830366`
- Fecha: `12/26`
- CVV: `123`
- Nombre: Cualquier nombre
- RFC: Cualquier RFC válido (ej: `ABC010101ABC`)

**Tarjeta Mastercard Válida:**
- Número: `5425233430109903`
- Fecha: `08/25`
- CVV: `456`

## Reglas de Autorización Detalladas

### Regla 1: Tarjeta Verificada
- La tarjeta debe existir en la base de datos
- Debe estar marcada como verificada

### Regla 2: Fecha de Expiración Válida
- Formato MM/AA
- Debe ser posterior a la fecha actual
- Mes válido (01-12)

### Regla 3: CVV Correcto
- 3 dígitos para la mayoría de tarjetas
- 4 dígitos para American Express
- Debe coincidir con el registrado

### Regla 4: Intentos No Excedidos
- Máximo 3 intentos fallidos por tarjeta
- Se resetea después de un pago exitoso

### Regla 5: Fondos Suficientes
- El balance debe cubrir el monto del pago

### Regla 6: Límite de Transacción
- Máximo $10,000 por transacción

### Regla 7: Verificación de Velocidad
- Máximo 5 transacciones por tarjeta en 1 hora

### Regla 8: RFC Válido
- Formato correcto de RFC
- 13 caracteres para personas físicas
- 12 caracteres para personas morales

### Regla 9: Nombre Coincidente
- El nombre debe coincidir con el titular de la tarjeta

## API Endpoints

### Autenticación
- `POST /login` - Iniciar sesión
- `POST /register` - Registrar usuario
- `GET /logout` - Cerrar sesión

### Páginas Principales
- `GET /` - Redirección al dashboard o login
- `GET /dashboard` - Panel principal
- `GET /payment` - Formulario de pago
- `GET /history` - Historial de transacciones
- `GET /invoice/<id>` - Factura específica

### API
- `POST /api/validate-card` - Validar tarjeta
- `POST /api/process-payment` - Procesar pago
- `GET /api/cards/search` - Buscar tarjetas

## Diseño Visual

### Paleta de Colores
- **Primary**: Deep Navy (#1a2332)
- **Secondary**: Soft Sage (#8fbc8f)
- **Accent**: Warm Gold (#d4af37)
- **Background**: Off-white (#fafafa)
- **Text**: Charcoal (#2c3e50)

### Tipografía
- **Títulos**: Playfair Display (serif)
- **Cuerpo**: Inter (sans-serif)

### Características de Diseño
- Diseño minimalista y limpio
- Animaciones suaves y micro-interacciones
- Tarjeta de pago con previsualización en tiempo real
- Validación visual en tiempo real
- Diseño responsive para todos los dispositivos

## Seguridad

- Hash de contraseñas con Werkzeug
- Validación tanto del lado del cliente como del servidor
- Sanitización de entrada de datos
- Protección contra intentos de fuerza bruta
- Encriptación de datos sensibles

## Uso del Sistema

### 1. Login
- Accede con el usuario demo: `demo` / `demo123`
- O regístrate con un nuevo usuario

### 2. Dashboard
- Visualiza estadísticas de pagos
- Accede a transacciones recientes
- Navega a diferentes secciones

### 3. Realizar Pago
- Ingresa tus datos personales (Nombre y RFC)
- Ingresa los datos de la tarjeta
- El sistema validará en tiempo real
- Previsualiza la tarjeta mientras escribes
- Confirma el monto a pagar
- Procesa el pago de forma segura

### 4. Historial
- Filtra transacciones por estado y fecha
- Descarga facturas en PDF
- Consulta detalles de cada transacción

## Escenarios de Prueba

### Pago Exitoso
Usa cualquiera de las tarjetas válidas con fondos suficientes.

### Pago Rechazado - Tarjeta Expirada
- Tarjeta: `4916487051416887`
- Fecha: `10/24` (expirada)

### Pago Rechazado - Fondos Insuficientes
- Tarjeta: `5555555555554444`
- Balance: $800 (insuficiente para montos altos)

### Pago Rechazado - Intentos Excedidos
- Tarjeta: `378282246310005`
- Ya tiene 3 intentos fallidos

### Pago Rechazado - Tarjeta No Verificada
- Tarjeta: `4111111111111111`
- No está verificada en el sistema

## Desarrollo

### Ejecutar en modo desarrollo
```bash
python app.py
```

### Variables de entorno
```bash
export SECRET_KEY='tu-secret-key-aqui'
export FLASK_ENV='development'
```

### Personalización
- Modifica los estilos en `static/css/styles.css`
- Ajusta las reglas de validación en `models.py`
- Personaliza las plantillas en `templates/`



## Licencia

Este proyecto es de código abierto y está disponible para uso educativo y comercial.

---

**PaySecure** - Microsistema de Pagos y Facturación
 2026 - Todos los derechos reservados
# MU
=======
# MU
Sistema de Gestion de Pagos y Facturacion
>>>>>>> 99ab4ffeaea040c6e8f160bd3490fa846f7bec73
