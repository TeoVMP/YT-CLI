# 🔧 Cómo Configurar Redirect URI en Google Cloud Console

## Pasos Detallados

### Paso 1: Acceder a Google Cloud Console

1. Ve a: **https://console.cloud.google.com/**
2. Inicia sesión con la misma cuenta de Google que usaste para crear las credenciales OAuth2

### Paso 2: Navegar a Credentials (Credenciales)

1. En el menú lateral izquierdo, busca **"APIs & Services"** (APIs y Servicios)
2. Haz clic en **"Credentials"** (Credenciales)
   - O ve directamente a: **https://console.cloud.google.com/apis/credentials**

### Paso 3: Encontrar tu OAuth 2.0 Client ID

1. En la lista de credenciales, busca tu **OAuth 2.0 Client ID**
   - Debería tener un nombre como "YouTube Bot Desktop" o similar
   - O busca el Client ID que empieza con: `173177570700-...`
   - **IMPORTANTE**: Debe ser tipo "OAuth 2.0 Client ID", NO "API Key"
2. **Haz clic en el nombre** del OAuth 2.0 Client ID para editarlo

### Paso 4: Verificar el Tipo de Aplicación

1. En la página de edición, busca la sección **"Application type"** (Tipo de aplicación)
2. Debe estar configurado como **"Desktop app"** (Aplicación de escritorio)
3. Si NO está como "Desktop app":
   - ⚠️ **PROBLEMA**: Necesitas crear un nuevo OAuth 2.0 Client ID
   - Ve a la sección "Crear Nuevo OAuth 2.0 Client ID" más abajo

### Paso 5: Configurar Authorized redirect URIs

**Si el tipo es "Desktop app":**

1. En la página de edición, busca la sección **"Authorized redirect URIs"** (URIs de redirección autorizados)
   - Esta sección puede estar más abajo en la página
   - O puede estar en una pestaña/separador
2. Si NO ves esta sección:
   - El OAuth 2.0 Client ID puede estar configurado como "Web application" en lugar de "Desktop app"
   - Necesitas crear uno nuevo (ver sección abajo)

3. Si SÍ ves la sección:
   - Haz clic en **"+ ADD URI"** o en el botón de agregar
   - En el campo que aparece, escribe **EXACTAMENTE**:
     ```
     http://localhost:8080
     ```

### ⚠️ Si NO encuentras "Authorized redirect URIs"

**Esto significa que tu OAuth 2.0 Client ID está configurado como "Web application" en lugar de "Desktop app".**

**Solución: Crear un nuevo OAuth 2.0 Client ID**

1. En la página de Credentials, haz clic en **"+ CREATE CREDENTIALS"** (Crear credenciales)
2. Selecciona **"OAuth client ID"**
3. Si te pide configurar el OAuth consent screen primero:
   - Haz clic en "CONFIGURE CONSENT SCREEN"
   - Selecciona "External" (Externo)
   - Completa los campos requeridos (App name, User support email)
   - En "Scopes", agrega: `https://www.googleapis.com/auth/youtube.force-ssl`
   - Agrega tu email como "Test user"
   - Guarda y continúa
4. En "Application type", selecciona **"Desktop app"** (NO "Web application")
5. Dale un nombre, por ejemplo: "YouTube Bot Desktop"
6. Haz clic en **"CREATE"** (Crear)
7. **IMPORTANTE**: Copia el nuevo Client ID y Client Secret
8. Actualiza tu archivo `.env` con estos nuevos valores:
   ```
   GOOGLE_CLIENT_ID=tu_nuevo_client_id
   GOOGLE_CLIENT_SECRET=tu_nuevo_client_secret
   ```
9. Para "Desktop app", el redirect_uri `http://localhost:8080` se configura automáticamente
   - Pero puedes agregarlo manualmente si es necesario
   ⚠️ **IMPORTANTE:**
   - Debe ser `http://` (NO `https://`)
   - Debe ser `localhost` (NO `127.0.0.1`)
   - NO debe tener barra final (`/`)
   - NO debe tener espacios
   - Debe ser exactamente: `http://localhost:8080`

### Paso 5: Guardar los Cambios

1. Desplázate hacia abajo en la página
2. Haz clic en **"SAVE"** (Guardar) en la parte inferior
3. Espera a que aparezca el mensaje de confirmación

### Paso 6: Esperar a que se Apliquen los Cambios

- Los cambios pueden tardar **2-3 minutos** en aplicarse
- Espera unos minutos antes de intentar el login de nuevo

## Verificación

Después de guardar, verifica que:
- ✅ El URI `http://localhost:8080` aparezca en la lista de "Authorized redirect URIs"
- ✅ No haya espacios adicionales
- ✅ No haya barras finales
- ✅ Sea exactamente `http://localhost:8080`

## Ejemplo Visual

```
Authorized redirect URIs
┌─────────────────────────────┐
│ http://localhost:8080        │  ← Debe aparecer así
└─────────────────────────────┘
```

## Solución de Problemas

### Si no puedes editar el OAuth 2.0 Client ID:
- Verifica que tengas permisos de "Editor" o "Owner" en el proyecto
- Asegúrate de estar en el proyecto correcto de Google Cloud

### Si los cambios no se aplican:
- Espera 5 minutos y vuelve a intentar
- Cierra y vuelve a abrir la página de credenciales
- Verifica que guardaste los cambios correctamente

### Si sigue fallando después de configurar:
1. Verifica que el URI sea exactamente `http://localhost:8080`
2. Asegúrate de que no haya URIs duplicados
3. Intenta eliminar y volver a agregar el URI
4. Verifica que estés usando el Client ID correcto

## Nota para Termux/Android

En Termux/Android, aunque uses `http://localhost:8080` como redirect_uri, Google redirigirá a esa URL después de autorizar. Aunque veas un error "This site can't be reached" en el navegador, **ES NORMAL**. Solo necesitas copiar la URL completa de la barra de direcciones, que contiene el código de autorización.
