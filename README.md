# Bot de YouTube - Comentarios y Descargas

Bot automatizado para comentar, ver y descargar videos de YouTube. Incluye:
- ✅ Comentar en videos usando la API oficial de Google
- ✅ Descargar videos en formato MP4
- ✅ Extraer y descargar audio en formato MP3
- ✅ Ver información de videos sin descargarlos
- ✅ Sistema de moderación automática basado en reglas éticas personalizables

## 🔒 Protección de Cuenta

### ⚠️ IMPORTANTE: Seguridad de Credenciales

Este bot está diseñado para **proteger tu cuenta de Google** usando OAuth2 con **scopes limitados**:

- ✅ **Solo solicita acceso a YouTube API** (`youtube.force-ssl`)
- ❌ **NO solicita acceso a email/Gmail**
- ❌ **NO puede acceder a tu bandeja de entrada**
- ✅ **Los tokens solo permiten acciones en YouTube**

### Cómo Funciona la Protección

1. **Scopes Limitados**: El bot solo solicita el permiso `https://www.googleapis.com/auth/youtube.force-ssl`, que permite comentar y gestionar comentarios en YouTube, pero **NO** da acceso a Gmail o email.

2. **Tokens OAuth2**: Los tokens generados solo tienen los permisos solicitados. Incluso si alguien obtiene el token, solo podrá usarlo para acciones en YouTube, no para acceder al email.

3. **Verificación en Autorización**: Cuando autorizas la aplicación, Google te muestra exactamente qué permisos se están solicitando. Puedes verificar que solo se pide acceso a YouTube.

## 📋 Requisitos

- Python 3.8 o superior
- FFmpeg instalado en el sistema (para conversión de audio a MP3)
  - Windows: Descargar de [ffmpeg.org](https://ffmpeg.org/download.html) y agregar al PATH
  - Linux: `sudo apt install ffmpeg` o `sudo yum install ffmpeg`
  - macOS: `brew install ffmpeg`
- Cuenta de Google con acceso a YouTube (solo para funciones de comentarios)
- Proyecto en Google Cloud Console con YouTube Data API v3 habilitada (solo para comentarios)
- Credenciales OAuth2 (Client ID y Client Secret) - solo para comentarios

## 🚀 Instalación

1. **Clonar el repositorio**:
```bash
git clone <tu-repositorio>
cd YTLikesBot
```

2. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

3. **Configurar credenciales**:
   - Copia `env.example` a `.env`
   - Completa con tus credenciales de Google Cloud Console:
   ```bash
   cp env.example .env
   ```

4. **Editar `.env`** con tus credenciales:
```env
GOOGLE_CLIENT_ID=tu_client_id_aqui
GOOGLE_CLIENT_SECRET=tu_client_secret_aqui
REDIRECT_URI=http://localhost:8080
```

## 🔧 Configuración de Google Cloud Console

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita **YouTube Data API v3**
4. Ve a "Credenciales" → "Crear credenciales" → "ID de cliente OAuth 2.0"
5. Selecciona "Aplicación de escritorio"
6. Configura el redirect URI: `http://localhost:8080`
7. Descarga las credenciales y cópialas a tu archivo `.env`

### ⚠️ IMPORTANTE: Configuración de Scopes

Asegúrate de que en Google Cloud Console **NO** habilites:
- Gmail API
- Google Mail API
- Cualquier servicio relacionado con email

Solo habilita **YouTube Data API v3**.

## 📝 Uso

### ⚠️ ADVERTENCIA LEGAL

**Descargar videos y audio de YouTube puede violar los Términos de Servicio de YouTube y leyes de derechos de autor.** Usa esta funcionalidad solo para:
- Contenido de dominio público
- Videos propios
- Contenido con permiso explícito del creador
- Uso educativo/personal (según las leyes de tu país)

### Descargar Video MP4

```bash
python main.py --download-video "https://www.youtube.com/watch?v=VIDEO_ID"
```

Con calidad específica:
```bash
python main.py --download-video "URL" --video-quality best
```

### Descargar Audio MP3

```bash
python main.py --download-audio "https://www.youtube.com/watch?v=VIDEO_ID"
```

Con calidad específica (kbps):
```bash
python main.py --download-audio "URL" --audio-quality 320
```

### Descargar Video y Audio

```bash
python main.py --download-both "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Ver Información de un Video

```bash
python main.py --info "https://www.youtube.com/watch?v=VIDEO_ID"
```

Muestra título, canal, duración, vistas, etc. sin descargar.

### Comentar en un video

```bash
python main.py --video-id dQw4w9WgXcQ --comment "¡Excelente video!"
```

### Obtener comentarios de un video

```bash
python main.py --video-id dQw4w9WgXcQ --get-comments
```

### Activar moderación automática

```bash
python main.py --video-id dQw4w9WgXcQ --comment "Comentario" --moderate
```

### Monitoreo continuo

```bash
python main.py --monitor --video-id dQw4w9WgXcQ
```

### Modo interactivo

```bash
python main.py
```

El modo interactivo te permite elegir entre todas las opciones disponibles.

## 🛡️ Sistema de Moderación Automática

El bot incluye un sistema de moderación que puede eliminar automáticamente comentarios que violen reglas éticas.

### Configurar Reglas Éticas

1. Copia `ethics_rules.json.example` a `ethics_rules.json`:
```bash
cp ethics_rules.json.example ethics_rules.json
```

2. Edita `ethics_rules.json` con tus reglas:
```json
{
  "ethics_rules": {
    "banned_words": ["palabra1", "palabra2"],
    "banned_patterns": [".*spam.*"],
    "max_length": 500,
    "min_length": 10,
    "auto_delete": true
  }
}
```

### Cómo Funciona

1. El bot monitorea comentarios periódicamente
2. Analiza cada comentario contra las reglas éticas
3. Si detecta una violación, elimina el comentario automáticamente
4. Registra todas las acciones en `moderation_logs.json`

## 📁 Estructura del Proyecto

```
YTLikesBot/
├── main.py                 # Script principal
├── youtube_client.py       # Cliente de YouTube API (comentarios)
├── downloader.py          # Descargador de videos y audio
├── moderator.py           # Sistema de moderación
├── content_analyzer.py    # Analizador de contenido
├── config.py              # Configuración
├── requirements.txt       # Dependencias
├── .env                   # Credenciales (NO subir a GitHub)
├── token.json             # Token OAuth2 (NO subir a GitHub)
├── ethics_rules.json      # Reglas éticas (personalizar)
├── downloads/             # Carpeta de descargas (creada automáticamente)
│   ├── videos/           # Videos MP4 descargados
│   └── audio/            # Audios MP3 descargados
└── README.md              # Este archivo
```

## 🔐 Seguridad

### Archivos que NUNCA deben subirse a GitHub:

- `.env` (credenciales)
- `token.json` (tokens OAuth2)
- `credentials.json` (credenciales de Google)
- `moderation_logs.json` (puede contener información sensible)

### Archivos que SÍ deben estar en GitHub:

- `env.example` (plantilla sin credenciales)
- `ethics_rules.json.example` (plantilla de reglas)
- Todo el código fuente
- `README.md`

## ⚠️ Advertencias

1. **Uso Responsable**: Este bot es para uso educativo/testing. No uses para spam o manipulación de métricas.

2. **Descarga de Contenido**: 
   - Descargar videos/audio puede violar los Términos de Servicio de YouTube
   - Puede violar leyes de derechos de autor
   - Usa solo para contenido con permiso o de dominio público
   - El desarrollador no se hace responsable del uso indebido

3. **Políticas de YouTube**: Cualquier uso que viole las políticas de YouTube puede resultar en suspensión de cuenta.

4. **Cuota de API**: Google tiene límites de cuota diaria. Respeta estos límites.

5. **Cuentas Compartidas**: Aunque técnicamente es posible compartir credenciales, NO es recomendable por seguridad.

6. **FFmpeg Requerido**: Para convertir audio a MP3 necesitas FFmpeg instalado en tu sistema.

## 📄 Licencia

[Especificar licencia]

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📞 Soporte

Para problemas o preguntas, abre un issue en el repositorio.

## 📦 Archivos Descargados

Los videos y audios se guardan en:
- Videos MP4: `downloads/videos/`
- Audios MP3: `downloads/audio/`

Estas carpetas se crean automáticamente al ejecutar el bot.

## 🔧 Configuración de Descargas

Puedes configurar la calidad y ubicación de descargas en `config.py` o mediante variables de entorno en `.env`:

```env
DOWNLOAD_DIR=downloads          # Carpeta base de descargas
VIDEO_QUALITY=best              # best o worst
AUDIO_QUALITY=192                # Calidad en kbps (128, 192, 256, 320)
```

---

**Recuerda**: Este bot solo solicita permisos de YouTube para comentar. Tu email está protegido. 🛡️

**Advertencia**: Descargar contenido puede violar términos de servicio y leyes de derechos de autor. Usa responsablemente. ⚖️
