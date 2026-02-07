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
2. **Haz clic en el nombre** del OAuth 2.0 Client ID para editarlo

### Paso 4: Configurar Authorized redirect URIs

1. En la página de edición, busca la sección **"Authorized redirect URIs"** (URIs de redirección autorizados)
2. Haz clic en **"+ ADD URI"** o en el botón de agregar
3. En el campo que aparece, escribe **EXACTAMENTE**:
   ```
   http://localhost:8080
   ```
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
