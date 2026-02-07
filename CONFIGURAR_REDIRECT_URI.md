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
2. Verifica si dice:
   - **"Web application"** (Aplicación web) → Necesitas agregar redirect_uri manualmente
   - **"Desktop app"** (Aplicación de escritorio) → Redirect_uri se configura automáticamente

### Paso 5: Configurar Authorized redirect URIs

**Si el tipo es "Web application" (Aplicación web):**

1. En la página de edición, **desplázate hacia abajo** hasta encontrar la sección:
   - **"Authorized redirect URIs"** (URIs de redirección autorizados)
   - O **"URIs de redireccionamiento autorizados"** (en español)
   
2. Haz clic en **"+ ADD URI"** o **"+ AGREGAR URI"** o el botón de agregar

3. En el campo que aparece, escribe **EXACTAMENTE**:
   ```
   http://localhost:8080
   ```
   ⚠️ **IMPORTANTE para localhost:**
   - Puedes usar `http://` (NO `https://`) para localhost
   - Debe ser exactamente `http://localhost:8080`
   - Sin espacios, sin barra final

4. Presiona **Enter** o haz clic fuera del campo

5. Si necesitas agregar más URIs, repite el proceso

**Si el tipo es "Desktop app" (Aplicación de escritorio):**

- Para "Desktop app", Google usa `http://localhost` automáticamente
- NO necesitas agregar el redirect_uri manualmente
- Si tienes problemas, puedes crear uno nuevo como "Web application" y agregar el redirect_uri

### ⚠️ Si NO encuentras "Authorized redirect URIs"

**Esto puede significar:**
1. Tu OAuth 2.0 Client ID está configurado como "Desktop app" (no muestra la opción)
2. O estás viendo una página diferente

**Solución 1: Si es "Desktop app" y funciona automáticamente**
- Para "Desktop app", `http://localhost:8080` debería funcionar sin configuración adicional
- Si no funciona, prueba la Solución 2

**Solución 2: Cambiar a "Web application" y agregar redirect_uri**

**Opción A: Editar el existente (si Google lo permite)**
1. En la página de edición, busca "Application type"
2. Si puedes cambiarlo a "Web application", hazlo
3. Luego agrega el redirect_uri como se explica arriba

**Opción B: Crear un nuevo OAuth 2.0 Client ID como "Web application"**

1. En la página de Credentials, haz clic en **"+ CREATE CREDENTIALS"** (Crear credenciales)
2. Selecciona **"OAuth client ID"**
3. Si te pide configurar el OAuth consent screen primero:
   - Haz clic en "CONFIGURE CONSENT SCREEN"
   - Selecciona "External" (Externo)
   - Completa los campos requeridos (App name, User support email)
   - En "Scopes", agrega: `https://www.googleapis.com/auth/youtube.force-ssl`
   - Agrega tu email como "Test user"
   - Guarda y continúa
4. En "Application type", selecciona **"Web application"** (Aplicación web)
5. Dale un nombre, por ejemplo: "YouTube Bot Web"
6. **IMPORTANTE**: En "Authorized redirect URIs", haz clic en "+ ADD URI"
7. Agrega: `http://localhost:8080`
8. Haz clic en **"CREATE"** (Crear)
9. **IMPORTANTE**: Copia el nuevo Client ID y Client Secret
10. Actualiza tu archivo `.env` con estos nuevos valores:
    ```
    GOOGLE_CLIENT_ID=tu_nuevo_client_id
    GOOGLE_CLIENT_SECRET=tu_nuevo_client_secret
    ```
11. Guarda el archivo `.env`
12. Vuelve a intentar el login
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
