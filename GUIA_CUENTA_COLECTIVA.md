# 🔒 Guía Completa: Crear y Proteger Cuenta Colectiva de Google

## Paso 1: Crear la Cuenta de Google Colectiva

### Opción A: Crear cuenta nueva con email propio

1. Ve a [Crear cuenta de Google](https://accounts.google.com/signup)
2. Completa el formulario:
   - **Nombre**: Usa un nombre descriptivo (ej: "YouTube Bot Colectivo")
   - **Email**: Puedes usar:
     - Un email nuevo de Gmail (ej: `youtubebotcolectivo@gmail.com`)
     - Un email de ProtonMail u otro servicio
   - **Contraseña**: Crea una contraseña fuerte y segura
   - **Teléfono**: Necesario para verificación (puede ser un número compartido)
3. Verifica tu teléfono
4. Completa la verificación de seguridad
5. **¡Cuenta creada!**

### Opción B: Usar cuenta existente (si ya tienes una para el proyecto)

Si ya tienes una cuenta de Google que quieres usar como colectiva, simplemente úsala.

## Paso 2: Configurar Google Cloud Console

### 2.1 Acceder a Google Cloud Console

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. **Inicia sesión con la cuenta colectiva** que acabas de crear
3. Acepta los términos si es la primera vez

### 2.2 Crear un Proyecto

1. En la parte superior, click en el selector de proyectos
2. Click en **"NUEVO PROYECTO"**
3. Completa:
   - **Nombre del proyecto**: "YouTube Bot Colectivo" (o el que prefieras)
   - **Organización**: Déjalo en blanco (si no tienes organización)
4. Click **"CREAR"**
5. Espera unos segundos a que se cree
6. Selecciona el proyecto recién creado del selector

### 2.3 Habilitar YouTube Data API v3

1. En el menú lateral, ve a **"APIs y servicios"** → **"Biblioteca"**
2. En el buscador, escribe: **"YouTube Data API v3"**
3. Click en **"YouTube Data API v3"**
4. Click en el botón **"HABILITAR"**
5. Espera a que se habilite (puede tardar unos segundos)

**⚠️ IMPORTANTE**: Solo habilita YouTube Data API v3. NO habilites:
- ❌ Gmail API
- ❌ Google Mail API
- ❌ Cualquier API relacionada con email

### 2.4 Crear Credenciales OAuth2

1. Ve a **"APIs y servicios"** → **"Credenciales"**
2. Click en **"+ CREAR CREDENCIALES"** (arriba)
3. Selecciona **"ID de cliente OAuth 2.0"**

#### Configuración de la Credencial:

1. **Tipo de aplicación**: Selecciona **"Aplicación de escritorio"**
2. **Nombre**: "YouTube Bot Desktop" (o el que prefieras)
3. Click **"CREAR"**

#### Configurar Pantalla de Consentimiento:

Si es la primera vez, Google te pedirá configurar la pantalla de consentimiento:

1. **Tipo de usuario**: Selecciona **"Externo"** (a menos que tengas Google Workspace)
2. Click **"CREAR"**
3. **Información de la aplicación**:
   - **Nombre de la aplicación**: "YouTube Bot"
   - **Email de soporte**: El email de la cuenta colectiva
   - **Email del desarrollador**: El mismo email
4. Click **"GUARDAR Y CONTINUAR"**
5. **Alcances**: 
   - Click **"+ AÑADIR O ELIMINAR ALCANCES"**
   - Busca y selecciona: **"https://www.googleapis.com/auth/youtube.force-ssl"**
   - **NO selecciones ningún alcance de Gmail o email**
   - Click **"ACTUALIZAR"** → **"GUARDAR Y CONTINUAR"**
6. **Usuarios de prueba**: 
   - Agrega el email de la cuenta colectiva como usuario de prueba
   - Click **"GUARDAR Y CONTINUAR"**
7. **Resumen**: Revisa y click **"VOLVER AL PANEL"**

#### Volver a Crear Credenciales:

1. Ve a **"Credenciales"** nuevamente
2. Click **"+ CREAR CREDENCIALES"** → **"ID de cliente OAuth 2.0"**
3. **Tipo**: "Aplicación de escritorio"
4. **Nombre**: "YouTube Bot Desktop"
5. Click **"CREAR"**

### 2.5 Obtener las Credenciales

Después de crear, verás una ventana con:

- **ID de cliente**: Algo como `123456789-abcdefghijklmnop.apps.googleusercontent.com`
- **Secreto de cliente**: Algo como `GOCSPX-abcdefghijklmnopqrstuvwxyz`

**⚠️ IMPORTANTE**: 
- **Copia estas credenciales inmediatamente**
- **Guárdalas en un lugar seguro**
- **NO las compartas públicamente**

## Paso 3: Verificar que Solo Tiene Permisos de YouTube

### Verificar Alcances (Scopes)

1. En Google Cloud Console, ve a **"APIs y servicios"** → **"Pantalla de consentimiento de OAuth"**
2. Click en **"ALCANCES"**
3. Verifica que SOLO aparezca:
   - ✅ `https://www.googleapis.com/auth/youtube.force-ssl`
4. Si aparece algo relacionado con Gmail o email:
   - ❌ Elimínalo inmediatamente
   - Solo debe haber alcances de YouTube

### Verificar APIs Habilitadas

1. Ve a **"APIs y servicios"** → **"Biblioteca"**
2. Click en **"APIs habilitadas"** (en el menú lateral)
3. Verifica que SOLO aparezca:
   - ✅ YouTube Data API v3
4. Si aparece Gmail API o Google Mail API:
   - ❌ Deshabilítalas inmediatamente

## Paso 4: Configurar el Bot

### Opción A: Usar Script Interactivo

```bash
py setup.py
```

Cuando te pida las credenciales, pega:
- **GOOGLE_CLIENT_ID**: El ID de cliente que copiaste
- **GOOGLE_CLIENT_SECRET**: El secreto de cliente que copiaste

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

COLLECTIVE_ACCOUNT_ENABLED=true
PROTECTION_ENABLED=true
```

## Paso 5: Primera Autorización

1. Ejecuta cualquier comando que requiera autenticación:
```bash
py main.py --stats QebfaG8OWQc
```

2. Se abrirá tu navegador automáticamente

3. **IMPORTANTE**: 
   - **Inicia sesión con la cuenta colectiva** (no tu cuenta personal)
   - Verás una pantalla que dice "YouTube Bot quiere acceder a tu cuenta de Google"
   - **Verifica que solo solicite acceso a YouTube** (no a Gmail)
   - Click **"Permitir"**

4. El token se guardará en `token.json` automáticamente

5. **¡Listo!** Ya puedes usar todas las funciones

## Paso 6: Verificar Protección

### Verificar que Solo Tiene Acceso a YouTube

1. Después de autorizar, ve a [Google Account Security](https://myaccount.google.com/permissions)
2. Inicia sesión con la cuenta colectiva
3. Busca "YouTube Bot" en la lista de aplicaciones
4. Click para ver detalles
5. **Verifica que solo muestre**: "Acceso a YouTube"
6. **NO debe mostrar**: "Acceso a Gmail" o "Acceso a correo"

## Protecciones Implementadas

### ✅ Protección del Email

- Solo se solicita el scope `youtube.force-ssl`
- NO se solicita acceso a Gmail
- Los tokens solo permiten acciones en YouTube
- El email está completamente protegido

### ✅ Protección de la Cuenta

- Rate limiting automático (50 comentarios/día, 10/hora)
- Monitoreo de actividad sospechosa
- Logs completos de todas las acciones
- Validación de contenido antes de publicar

## Comandos para Verificar

```bash
# Ver reporte de actividad
py main.py --activity-report

# Ver estadísticas (requiere autorización)
py main.py --stats VIDEO_ID

# Ver comentarios destacados
py main.py --top-comments VIDEO_ID
```

## Troubleshooting

### "Error: invalid_client"
- Verifica que copiaste correctamente el Client ID y Secret
- Asegúrate de que no haya espacios extra
- Verifica que el archivo `.env` esté en la carpeta del proyecto

### "Error: redirect_uri_mismatch"
- Verifica que en Google Cloud Console el redirect URI sea: `http://localhost:8080`
- Debe coincidir exactamente con el del archivo `.env`

### "No se puede acceder a Gmail"
- ✅ Esto es CORRECTO y ESPERADO
- El bot NO debe tener acceso a Gmail
- Solo debe tener acceso a YouTube

## Resumen de Seguridad

✅ **Email protegido**: Solo acceso a YouTube API
✅ **Cuenta protegida**: Rate limiting y monitoreo activos
✅ **Logs completos**: Toda actividad registrada
✅ **Detección automática**: Bloquea actividad sospechosa

---

**Recuerda**: 
- Usa la cuenta colectiva para autorizar
- Verifica que solo solicite acceso a YouTube
- Mantén las credenciales seguras
- No compartas el archivo `.env` o `token.json`
