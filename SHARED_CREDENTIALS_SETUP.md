# 🔑 Configuración de Credenciales Compartidas

Este proyecto está diseñado para usar **credenciales OAuth2 compartidas**, lo que significa que todos los usuarios pueden usar la misma API sin necesidad de crear sus propias credenciales.

## ✅ Ventajas

- **No necesitas crear credenciales propias** - Solo haz login con tu cuenta de Google
- **Proceso más simple** - Ejecuta `python main.py --login` y listo
- **Mismo acceso para todos** - Todos usan la misma aplicación OAuth2

## 📋 Requisitos

Para que esto funcione, la aplicación OAuth2 debe estar **publicada** en Google Cloud Console. Ver [PUBLISH_APP.md](PUBLISH_APP.md) para más detalles.

## 🚀 Uso Rápido

1. **Instala dependencias:**
   ```bash
   pip install -r requirements.txt
   # O en Termux: ./install-termux.sh
   ```

2. **Verifica configuración:**
   ```bash
   python setup_simple.py
   ```

3. **Login:**
   ```bash
   python main.py --login
   ```

4. **¡Listo!** Ya puedes usar todas las funciones.

## 🔧 Si las credenciales compartidas no funcionan

Si encuentras errores como "access_denied" o "app not verified":

1. **Verifica que la app esté publicada:**
   - Ve a Google Cloud Console
   - OAuth Consent Screen → Debe estar en "In production"

2. **Usa tus propias credenciales (opcional):**
   ```bash
   python setup.py
   ```
   Esto te guiará para crear tus propias credenciales OAuth2.

## 📝 Notas de Seguridad

- Las credenciales compartidas solo permiten acceso a YouTube API
- **NO tienen acceso a Gmail/email**
- Cada usuario autoriza con su propia cuenta de Google
- Los tokens se guardan localmente en tu computadora

## 🆘 Solución de Problemas

### Error: "access_denied"
- La aplicación no está publicada → Publica la app en Google Cloud Console
- O usa tus propias credenciales con `python setup.py`

### Error: "ModuleNotFoundError"
- Instala dependencias: `pip install -r requirements.txt`
- En Termux: `./install-termux.sh`

### Error: "credentials not configured"
- Ejecuta `python setup_simple.py` para verificar
- O configura credenciales con `python setup.py`
