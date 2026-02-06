# 🧪 Guía para Probar la Funcionalidad de Comentar

## Requisitos Previos

Para comentar en YouTube necesitas:

1. ✅ **Cuenta de Google** (puede ser colectiva)
2. ✅ **Credenciales OAuth2** de Google Cloud Console
3. ✅ **Archivo `.env` configurado**
4. ✅ **Autorización completada** (token.json)

## Paso 1: Verificar Configuración

### Verificar si tienes `.env`:

```bash
# En PowerShell
Test-Path .env

# Si no existe, necesitas configurarlo:
py setup.py
```

### Verificar si tienes `token.json`:

```bash
# En PowerShell
Test-Path token.json

# Si no existe, necesitarás autorizar la primera vez
```

## Paso 2: Configurar Credenciales (Si aún no lo has hecho)

### Opción A: Configuración Interactiva (Recomendado)

```bash
py setup.py
```

Te pedirá:
- GOOGLE_CLIENT_ID
- GOOGLE_CLIENT_SECRET
- Configuraciones opcionales

### Opción B: Configuración Manual

1. Copia el archivo de ejemplo:
```bash
copy env.example .env
```

2. Edita `.env` con un editor de texto y agrega:
```env
GOOGLE_CLIENT_ID=tu_client_id_aqui
GOOGLE_CLIENT_SECRET=tu_client_secret_aqui
REDIRECT_URI=http://localhost:8080
```

## Paso 3: Obtener Credenciales OAuth2

Si aún no tienes las credenciales:

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un proyecto o selecciona uno existente
3. Habilita **"YouTube Data API v3"**
4. Ve a **"Credenciales"** → **"Crear credenciales"** → **"ID de cliente OAuth 2.0"**
5. Tipo: **"Aplicación de escritorio"**
6. Copia el **Client ID** y **Client Secret**

**IMPORTANTE**: En "Alcances", selecciona SOLO `youtube.force-ssl` (NO Gmail)

## Paso 4: Primera Autorización

La primera vez que uses cualquier función que requiera autenticación, se abrirá el navegador:

```bash
# Cualquiera de estos comandos iniciará la autorización:
py main.py --stats VIDEO_ID
py main.py --top-comments VIDEO_ID
py main.py --video-id VIDEO_ID --comment "Texto de prueba"
```

**Pasos en el navegador:**
1. Se abrirá automáticamente
2. **Inicia sesión con tu cuenta de Google** (la que configuraste)
3. Verás una pantalla de permisos
4. **Verifica que solo solicite acceso a YouTube** (no a Gmail)
5. Click en **"Permitir"**
6. El token se guardará en `token.json` automáticamente

## Paso 5: Probar Comentar

### Opción 1: Modo CLI (Línea de comandos)

```bash
# Con URL completa de YouTube
py main.py --video-id "https://www.youtube.com/watch?v=VIDEO_ID" --comment "Tu comentario aquí"

# Con solo el ID del video
py main.py --video-id VIDEO_ID --comment "Tu comentario aquí"
```

**Ejemplo real:**
```bash
py main.py --video-id "https://www.youtube.com/watch?v=l5ls08f-eEU" --comment "¡Excelente video! 🎉"
```

### Opción 2: Modo Interactivo

```bash
py main.py
```

Luego selecciona:
1. Opción **1**: Comentar en un video
2. Ingresa el ID del video (o URL)
3. Ingresa el texto del comentario
4. El comentario se publicará automáticamente

## Paso 6: Verificar que Funcionó

Después de ejecutar el comando, deberías ver:

```
✓ Comentario publicado exitosamente!
```

Si hay un error, verás:
```
✗ Error: [mensaje de error]
```

## Troubleshooting

### Error: "ERROR: GOOGLE_CLIENT_ID y GOOGLE_CLIENT_SECRET deben estar configurados"

**Solución**: Ejecuta `py setup.py` y completa las credenciales.

### Error: "No se pudo extraer el ID del video"

**Solución**: Asegúrate de usar una URL válida de YouTube o solo el ID del video.

### Error: "invalid_client" o "invalid_grant"

**Solución**: 
- Verifica que copiaste correctamente el Client ID y Secret
- Asegúrate de que no haya espacios extra en `.env`
- Elimina `token.json` y vuelve a autorizar

### Error: "quotaExceeded"

**Solución**: Has alcanzado el límite diario de cuota (10,000 unidades). Espera hasta mañana o solicita aumento en Google Cloud Console.

### El navegador no se abre para autorizar

**Solución**: 
- Verifica que el puerto 8080 no esté en uso
- Abre manualmente: http://localhost:8080 después de ejecutar el comando
- Verifica que `REDIRECT_URI` en `.env` sea `http://localhost:8080`

## Ejemplo Completo

```bash
# 1. Configurar (solo primera vez)
py setup.py

# 2. Autorizar (solo primera vez - se abre automáticamente)
py main.py --stats l5ls08f-eEU

# 3. Comentar
py main.py --video-id "https://www.youtube.com/watch?v=l5ls08f-eEU" --comment "¡Genial!"

# 4. Verificar en YouTube que el comentario apareció
```

## Notas Importantes

⚠️ **Límites de YouTube API:**
- Máximo 50 comentarios/día por defecto (configurable)
- Máximo 10 comentarios/hora por defecto (configurable)
- Cada comentario cuesta 50 unidades de cuota

⚠️ **Políticas de YouTube:**
- No uses para spam
- Respeta las políticas de la comunidad
- Los comentarios deben ser relevantes al video

✅ **Seguridad:**
- Solo se solicita acceso a YouTube (no a Gmail)
- Los tokens se guardan localmente en `token.json`
- No compartas tus credenciales
