# YouTube Bot - Bot para Comentar y Descargar Videos de YouTube

Bot completo para interactuar con YouTube: comentar, descargar videos/audio, ver estadísticas y más.

## 🎯 Características Principales

- ✅ **Comentar en videos** usando tu cuenta personal de Google
- ✅ **Descargar videos MP4** y **audio MP3**
- ✅ **Ver estadísticas** de videos
- ✅ **Exportar comentarios** a archivos de texto
- ✅ **Reproducir videos** automáticamente con VLC
- ✅ **Sistema de protección**: Solo acceso a YouTube (no a Gmail)
- ✅ **Rate limiting** configurable

## 🚀 Inicio Rápido

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar Credenciales OAuth2

**Cada usuario usa su propia cuenta de Google para comentar.**

```bash
py setup.py
```

O manualmente: copia `env.example` a `.env` y completa tus credenciales.

### 3. Autorizar con tu Cuenta Personal

```bash
py main.py --stats VIDEO_ID
```

Se abrirá el navegador para que autorices con tu cuenta personal de Google.

## 📋 Comandos Disponibles

### Comentar

```bash
# Con URL completa
py main.py --video-id "https://www.youtube.com/watch?v=VIDEO_ID" --comment "Tu comentario"

# Con solo el ID
py main.py --video-id VIDEO_ID --comment "Tu comentario"
```

### Descargar

```bash
# Descargar video MP4
py main.py --download-video "https://www.youtube.com/watch?v=VIDEO_ID"

# Descargar audio MP3
py main.py --download-audio "https://www.youtube.com/watch?v=VIDEO_ID"

# Descargar ambos
py main.py --download-both "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Reproducir con VLC

```bash
# Reproducir desde URL
py main.py --play "https://www.youtube.com/watch?v=VIDEO_ID"

# Reproducir archivo local
py main.py --play "ruta/al/video.mp4"

# Pantalla completa
py main.py --play "URL" --play-fullscreen

# Descargar y reproducir automáticamente
py main.py --download-and-play "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Estadísticas y Comentarios

```bash
# Ver estadísticas
py main.py --stats VIDEO_ID

# Ver comentarios destacados
py main.py --top-comments VIDEO_ID

# Exportar comentarios
py main.py --export-comments VIDEO_ID

# Exportar en formato grep
py main.py --export-comments VIDEO_ID --grep-format
```

## 🔐 Seguridad

- ✅ Solo solicita acceso a YouTube API
- ✅ NO tiene acceso a Gmail/email
- ✅ Tokens guardados localmente en tu computadora
- ✅ Cada usuario autoriza con su propia cuenta

## 📖 Documentación

- `QUICK_START.md` - Guía de inicio rápido
- `PRUEBA_COMENTAR.md` - Cómo probar la funcionalidad de comentar
- `GUIA_GOOGLE_CLOUD_NUEVA_INTERFAZ.md` - Configurar Google Cloud Console
- `SOLUCION_ERROR_403.md` - Solucionar error 403
- `MULTI_ACCOUNT.md` - Sistema multi-cuenta (opcional)

## ⚙️ Configuración

### Archivo `.env`

```env
GOOGLE_CLIENT_ID=tu_client_id
GOOGLE_CLIENT_SECRET=tu_client_secret
REDIRECT_URI=http://localhost:8080

# Rate limiting
MAX_COMMENTS_PER_DAY=50
MAX_COMMENTS_PER_HOUR=10
```

### Obtener Credenciales OAuth2

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un proyecto
3. Habilita "YouTube Data API v3"
4. Configura OAuth Consent Screen:
   - User Type: External
   - Scopes: SOLO `youtube.force-ssl`
   - Agrega tu email como Test User
5. Crea credenciales OAuth2:
   - Application type: Desktop app
6. Copia Client ID y Client Secret

## 🎮 Modo Interactivo

```bash
py main.py
```

Menú interactivo con todas las opciones disponibles.

## 📝 Notas Importantes

- **Cada usuario usa su propia cuenta**: No necesitas cuentas colectivas
- **Primera autorización**: Se abre el navegador una vez
- **Límites**: 50 comentarios/día, 10/hora (configurable)
- **Tokens**: Se guardan en `token.json` (no subir a GitHub)

## 🐛 Troubleshooting

### Error 403: access_denied
- Agrega tu email como Test User en OAuth Consent Screen
- Lee `SOLUCION_ERROR_403.md`

### VLC no se abre
- Instala VLC desde https://www.videolan.org/vlc/
- Verifica que esté en el PATH

### Error de credenciales
- Verifica que `.env` tenga las credenciales correctas
- Ejecuta `py setup.py` para reconfigurar

## 📄 Licencia

Este proyecto es de código abierto. Úsalo responsablemente y respeta los términos de servicio de YouTube.
