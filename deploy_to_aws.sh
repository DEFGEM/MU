#!/bin/bash
# Script de despliegue automático para AWS EC2
# Ejecutar como: bash deploy_to_aws.sh

set -e

echo "🚀 Iniciando despliegue de MU en AWS..."

# Actualizar sistema
echo "📦 Actualizando sistema..."
sudo apt-get update
sudo apt-get upgrade -y

# Instalar dependencias del sistema
echo "📦 Instalando dependencias del sistema..."
sudo apt-get install -y python3-pip python3-venv python3-dev nginx sqlite3 build-essential libssl-dev libffi-dev

# Crear entorno virtual
echo "🐍 Configurando entorno virtual de Python..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias Python
echo "📦 Instalando dependencias de Python..."
pip install --upgrade pip
pip install gunicorn
pip install -r requirements.txt

# Crear directorios necesarios
echo "📁 Creando directorios..."
mkdir -p database
sudo mkdir -p /var/log/gunicorn
sudo chown admin:www-data /var/log/gunicorn

# Inicializar base de datos
echo "💾 Inicializando base de datos..."
python3 << EOF
from models import Database
db = Database()
print("Base de datos inicializada correctamente")
EOF

# Configurar permisos
echo "🔐 Configurando permisos..."
sudo chown -R admin:www-data ~/MU
chmod -R 755 ~/MU
chmod -R 775 ~/MU/database

# Generar SECRET_KEY segura
echo "🔑 Generando SECRET_KEY..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
echo "SECRET_KEY=$SECRET_KEY" > .env
echo "FLASK_ENV=production" >> .env

# Actualizar mu.service con SECRET_KEY
sed -i "s/CHANGE_THIS_IN_PRODUCTION/$SECRET_KEY/" mu.service

# Configurar Nginx
echo "🌐 Configurando Nginx..."
sudo cp mu_nginx.conf /etc/nginx/sites-available/mu
sudo ln -sf /etc/nginx/sites-available/mu /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Verificar configuración de Nginx
sudo nginx -t

# Configurar servicio systemd
echo "⚙️  Configurando servicio systemd..."
sudo cp mu.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mu
sudo systemctl start mu

# Reiniciar Nginx
echo "🔄 Reiniciando Nginx..."
sudo systemctl restart nginx

# Configurar firewall
echo "🔥 Configurando firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# Verificar servicios
echo ""
echo "🔍 Verificando servicios..."
echo ""
echo "Estado de MU:"
sudo systemctl status mu --no-pager || true
echo ""
echo "Estado de Nginx:"
sudo systemctl status nginx --no-pager || true

# Obtener IP pública
PUBLIC_IP=$(curl -s ifconfig.me)

echo ""
echo "✅ ¡Despliegue completado exitosamente!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 La aplicación está disponible en:"
echo "   http://$PUBLIC_IP"
echo ""
echo "📋 Credenciales de demo:"
echo "   Usuario: demo"
echo "   Contraseña: demo123"
echo ""
echo "🔍 Comandos útiles:"
echo "   Ver logs: sudo journalctl -u mu -f"
echo "   Reiniciar: sudo systemctl restart mu"
echo "   Estado: sudo systemctl status mu"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
