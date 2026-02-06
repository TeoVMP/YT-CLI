# 🚀 Inicio Rápido - Bot de YouTube

## Configuración en 3 Pasos

### Paso 1: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 2: Configurar Credenciales OAuth2 (Una sola vez)

**Cada usuario usa su propia cuenta de Google para comentar.**

Ejecuta el script de configuración interactiva:

```bash
py setup.py
```

El script te guiará para:
- Ingresar credenciales OAuth2 de Google Cloud Console
- Configurar límites de rate limiting

**O manualmente:**

1. Copia el archivo de ejemplo:
```bash
copy env.example .env
```

2. Edita `.env` y completa:
```env
GOOGLE_CLIENT_ID=tu_client_id_aqui
GOOGLE_CLIENT_SECRET=tu_client_secret_aqui
```

**📝 Nota**: Las credenciales OAuth2 son del proyecto en Google Cloud Console.
Cada usuario autoriza con su propia cuenta de Google.

### Paso 3: Autorizar con tu Cuenta Personal (Primera vez)

Ejecuta cualquier comando que requiera autenticación:

```bash
py main.py --stats dQw4w9WgXcQ
```

- Se abrirá tu navegador
- **Inicia sesión con tu cuenta personal de Google**
- Autoriza la aplicación
- El token se guarda en `token.json` (solo en tu computadora)
- ¡Listo!

## Funciones que NO Requieren Configuración

Estas funciones funcionan **inmediatamente** sin configurar nada:

```bash
# Descargar video MP4
py main.py --download-video "https://www.youtube.com/watch?v=VIDEO_ID"

# Descargar audio MP3
py main.py --download-audio "https://www.youtube.com/watch?v=VIDEO_ID"

# Ver información básica
py main.py --info "https://www.youtube.com/watch?v=VIDEO_ID"
```

## Funciones que Requieren Configuración

Estas funciones necesitan credenciales OAuth2:

```bash
# Ver estadísticas
py main.py --stats VIDEO_ID

# Ver comentarios destacados
py main.py --top-comments VIDEO_ID

# Exportar comentarios
py main.py --export-comments VIDEO_ID

# Comentar en videos
py main.py --video-id VIDEO_ID --comment "Texto"
```

## Obtener Credenciales OAuth2

Si necesitas las credenciales:

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un proyecto
3. Habilita "YouTube Data API v3"
4. Ve a "Credenciales" → "Crear credenciales" → "ID de cliente OAuth 2.0"
5. Tipo: "Aplicación de escritorio"
6. Copia Client ID y Client Secret

## Ayuda

- Ejecuta `py setup.py` para configuración guiada
- Lee `CUENTA_COLECTIVA.md` para información sobre protección
- Lee `README.md` para documentación completa
