# 🚀 Guía de Despliegue en AWS - MU Payment System

## Pasos para Desplegar

### 1️⃣ Crear Instancia EC2 en AWS

1. **Ir a AWS Console** → EC2 → Launch Instance
2. **Configurar:**
   - **Nombre**: MU-Payment-System
   - **AMI**: Ubuntu Server 22.04 LTS (Free tier eligible)
   - **Tipo de instancia**: t2.micro (Free tier)
   - **Par de claves**: Crear nuevo o usar existente (.pem)
   - **Security Group**: Crear con las siguientes reglas:
     ```
     SSH (22)    → Solo tu IP
     HTTP (80)   → 0.0.0.0/0
     HTTPS (443) → 0.0.0.0/0
     ```

3. **Lanzar instancia**

---

### 2️⃣ Copiar Archivos al Servidor

Desde tu máquina local, ejecuta:

```bash
# Reemplaza con tu clave .pem y la IP de tu instancia
scp -i ~/tu-clave.pem -r /home/wowo/Descargas/MU/MU/* ubuntu@TU-IP-PUBLICA:~/MU/
```

**Ejemplo:**
```bash
scp -i ~/aws-key.pem -r /home/wowo/Descargas/MU/MU/* ubuntu@54.123.45.67:~/MU/
```

---

### 3️⃣ Conectarse al Servidor

```bash
ssh -i ~/tu-clave.pem ubuntu@TU-IP-PUBLICA
```

---

### 4️⃣ Ejecutar Script de Despliegue

Una vez conectado al servidor:

```bash
cd ~/MU
chmod +x deploy_to_aws.sh
./deploy_to_aws.sh
```

**El script automáticamente:**
- ✅ Actualiza el sistema
- ✅ Instala dependencias
- ✅ Configura Python y el entorno virtual
- ✅ Inicializa la base de datos
- ✅ Configura Gunicorn y Nginx
- ✅ Genera SECRET_KEY segura
- ✅ Configura firewall
- ✅ Inicia los servicios

---

### 5️⃣ Verificar Despliegue

Al finalizar, verás un mensaje como:

```
✅ ¡Despliegue completado exitosamente!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 La aplicación está disponible en:
   http://54.123.45.67

📋 Credenciales de demo:
   Usuario: demo
   Contraseña: demo123
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Abre esa URL en tu navegador para verificar que funciona.

---

## 🔧 Comandos Útiles

### Ver logs en tiempo real
```bash
sudo journalctl -u mu -f
```

### Reiniciar la aplicación
```bash
sudo systemctl restart mu
```

### Ver estado del servicio
```bash
sudo systemctl status mu
```

### Ver logs de Nginx
```bash
sudo tail -f /var/log/nginx/mu_access.log
sudo tail -f /var/log/nginx/mu_error.log
```

### Actualizar la aplicación
```bash
cd ~/MU
# Copiar nuevos archivos desde tu máquina local
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart mu
```

---

## 🔐 Configurar SSL (HTTPS) - Opcional

Para tener HTTPS con certificado gratuito:

```bash
# Instalar Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtener certificado (reemplaza con tu dominio)
sudo certbot --nginx -d tu-dominio.com

# Renovar automáticamente
sudo certbot renew --dry-run
```

---

## 💾 Backup de Base de Datos

### Crear backup manual
```bash
cp ~/MU/database/payments.db ~/MU/database/backup_$(date +%Y%m%d_%H%M%S).db
```

### Configurar backup automático diario
```bash
# Crear script de backup
cat << 'EOF' > ~/backup_db.sh
#!/bin/bash
cp ~/MU/database/payments.db ~/MU/database/backup_$(date +%Y%m%d).db
# Mantener solo últimos 7 días
find ~/MU/database/backup_*.db -mtime +7 -delete
EOF

chmod +x ~/backup_db.sh

# Agregar a crontab (todos los días a las 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * ~/backup_db.sh") | crontab -
```

---

## 🚨 Troubleshooting

### La aplicación no carga

1. **Verificar que está corriendo:**
   ```bash
   sudo systemctl status mu
   ```

2. **Ver logs de errores:**
   ```bash
   sudo journalctl -u mu -n 50
   ```

3. **Verificar Nginx:**
   ```bash
   sudo nginx -t
   sudo systemctl status nginx
   ```

### Error de base de datos

```bash
cd ~/MU
source venv/bin/activate
python3 -c "from models import Database; Database()"
sudo systemctl restart mu
```

### Error de permisos

```bash
sudo chown -R ubuntu:www-data ~/MU
chmod -R 755 ~/MU
chmod -R 775 ~/MU/database
sudo systemctl restart mu
```

---

## 📊 Monitoreo

### Ver uso de recursos
```bash
top
htop  # Si está instalado
```

### Ver conexiones activas
```bash
sudo netstat -tupln | grep -E '(8000|80)'
```

---

## 💰 Costo Estimado

| Servicio | Costo (Free Tier) | Costo (Post Free Tier) |
|----------|-------------------|------------------------|
| EC2 t2.micro | $0/mes (12 meses) | ~$8.50/mes |
| EBS Storage (30GB) | $0 | ~$3/mes |
| Transferencia datos | 100GB gratis | $0.09/GB |
| **Total** | **$0/mes** | **~$10-15/mes** |

---

## ✅ Checklist Final

- [ ] Instancia EC2 creada y corriendo
- [ ] Security Group configurado (puertos 22, 80, 443)
- [ ] Archivos copiados al servidor
- [ ] Script de despliegue ejecutado sin errores
- [ ] Aplicación accesible desde navegador
- [ ] Login funciona con credenciales demo
- [ ] Registro de nuevos usuarios funciona
- [ ] Procesamiento de pagos funciona
- [ ] (Opcional) SSL configurado con dominio
- [ ] (Opcional) Backup automático configurado

---

## 📞 Soporte

Si encuentras problemas:
1. Revisa los logs: `sudo journalctl -u mu -n 100`
2. Verifica Nginx: `sudo nginx -t`
3. Revisa Security Group en AWS Console
4. Verifica que la instancia EC2 esté corriendo

¡Listo! Tu aplicación MU ahora está en producción en AWS 🎉
