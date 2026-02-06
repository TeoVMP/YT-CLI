# Guía Actualizada: Google Cloud Console - Nueva Interfaz

## Navegación en la Nueva Interfaz de Google Auth Platform

Google ha actualizado su interfaz. Ahora usa **"Google Auth Platform"** en lugar de "APIs y servicios" para algunas funciones.

## Pasos Actualizados para Configurar OAuth

### Paso 1: Crear Proyecto

1. Ve a: https://console.cloud.google.com/
2. Inicia sesión con tu cuenta colectiva
3. Click en el **selector de proyectos** (arriba, al lado del logo de Google)
4. Click **"NEW PROJECT"** o **"NUEVO PROYECTO"**
5. Nombre: Usa el nombre sugerido (ej: `youtube-service-234`)
6. Click **"CREATE"** o **"CREAR"**
7. Espera a que se cree (puede tardar unos segundos)
8. Selecciona el proyecto recién creado del selector

### Paso 2: Habilitar YouTube Data API v3

**Opción A: Desde el menú tradicional**
1. Ve a **"APIs & Services"** → **"Library"** (o **"APIs y servicios"** → **"Biblioteca"**)
2. Busca **"YouTube Data API v3"**
3. Click en el resultado
4. Click **"ENABLE"** o **"HABILITAR"**

**Opción B: Desde la búsqueda**
1. En la barra de búsqueda superior, busca: **"YouTube Data API v3"**
2. Click en el resultado
3. Click **"ENABLE"**

### Paso 3: Configurar OAuth Consent Screen

**Sí, "OAuth consent screen" es correcto** - Es la pantalla de consentimiento.

1. **Opción A - Desde Google Auth Platform:**
   - En el menú lateral izquierdo, busca **"Google Auth Platform"**
   - Click en **"OAuth consent screen"** (o **"Pantalla de consentimiento"**)

2. **Opción B - Desde APIs & Services:**
   - Ve a **"APIs & Services"** → **"OAuth consent screen"**

3. **Configuración:**
   - **User Type (Tipo de usuario)**: Selecciona **"External"** (Externo)
   - Click **"CREATE"** o **"CREAR"**

4. **App Information (Información de la app):**
   - **App name**: `YouTube Bot`
   - **User support email**: Tu email de la cuenta colectiva
   - **Developer contact information**: Tu email de la cuenta colectiva
   - Click **"SAVE AND CONTINUE"** o **"GUARDAR Y CONTINUAR"**

5. **Scopes (Alcances) - MUY IMPORTANTE:**
   - Click **"ADD OR REMOVE SCOPES"** o **"AÑADIR O ELIMINAR ALCANCES"**
   - En el buscador, escribe: `youtube.force-ssl`
   - Selecciona **SOLO** `https://www.googleapis.com/auth/youtube.force-ssl`
   - **NO selecciones:**
     - ❌ Gmail API
     - ❌ Google Mail API
     - ❌ Cualquier scope relacionado con email
   - Click **"UPDATE"** o **"ACTUALIZAR"**
   - Click **"SAVE AND CONTINUE"** o **"GUARDAR Y CONTINUAR"**

6. **Test users (Usuarios de prueba):**
   - Click **"ADD USERS"** o **"AÑADIR USUARIOS"**
   - Agrega el email de la cuenta colectiva
   - Click **"ADD"** o **"AÑADIR"**
   - Click **"SAVE AND CONTINUE"** o **"GUARDAR Y CONTINUAR"**

7. **Summary (Resumen):**
   - Revisa la información
   - Click **"BACK TO DASHBOARD"** o **"VOLVER AL PANEL"**

### Paso 4: Crear Credenciales OAuth2

**Opción A - Desde Google Auth Platform:**
1. En el menú lateral, ve a **"Google Auth Platform"** → **"Clients"** (o **"Clientes"**)
2. Click **"CREATE CREDENTIALS"** o **"CREAR CREDENCIALES"**
3. Selecciona **"OAuth client ID"** o **"ID de cliente OAuth"**

**Opción B - Desde APIs & Services:**
1. Ve a **"APIs & Services"** → **"Credentials"** (o **"Credenciales"**)
2. Click **"CREATE CREDENTIALS"** → **"OAuth client ID"**

**Configuración:**
- **Application type**: Selecciona **"Desktop app"** (Aplicación de escritorio)
- **Name**: `YouTube Bot Desktop`
- Click **"CREATE"** o **"CREAR"**

**Obtener Credenciales:**
- Se mostrará una ventana con:
  - **Your Client ID** (tu Client ID)
  - **Your Client Secret** (tu Client Secret)
- **⚠️ IMPORTANTE**: Copia ambas inmediatamente
- Click **"OK"** o **"ACEPTAR"**

## Verificar Configuración

### Verificar Scopes (Alcances)

1. Ve a **"Google Auth Platform"** → **"OAuth consent screen"**
2. Click en **"Scopes"** o **"Alcances"**
3. Verifica que **SOLO** aparezca:
   - ✅ `https://www.googleapis.com/auth/youtube.force-ssl`
4. Si aparece algo de Gmail o email:
   - ❌ Elimínalo inmediatamente
   - Solo debe haber scopes de YouTube

### Verificar APIs Habilitadas

1. Ve a **"APIs & Services"** → **"Enabled APIs"** (o **"APIs habilitadas"**)
2. Verifica que aparezca:
   - ✅ YouTube Data API v3
3. Si aparece Gmail API:
   - ❌ Deshabilítala inmediatamente

## Estructura de la Nueva Interfaz

```
Google Cloud Console
├── Google Auth Platform (NUEVO)
│   ├── Overview
│   ├── Branding
│   ├── Audience
│   ├── Clients ← Aquí creas credenciales OAuth2
│   ├── Data Access
│   ├── Verification Center
│   └── Settings
│
└── APIs & Services (TRADICIONAL)
    ├── Dashboard
    ├── Library ← Aquí habilitas APIs
    ├── OAuth consent screen ← Pantalla de consentimiento
    └── Credentials ← También puedes crear credenciales aquí
```

## Resumen Rápido

1. ✅ Crear proyecto
2. ✅ Habilitar YouTube Data API v3 (desde Library)
3. ✅ Configurar OAuth consent screen (desde Google Auth Platform o APIs & Services)
4. ✅ Agregar scope: `youtube.force-ssl` SOLO
5. ✅ Crear OAuth client ID (desde Clients o Credentials)
6. ✅ Copiar Client ID y Client Secret

## Troubleshooting

### "No veo OAuth consent screen"
- Busca en el menú lateral: **"Google Auth Platform"** → **"OAuth consent screen"**
- O desde: **"APIs & Services"** → **"OAuth consent screen"**

### "No puedo agregar scopes"
- Asegúrate de haber completado el paso de "App Information" primero
- Debes hacer click en "ADD OR REMOVE SCOPES" en la sección de Scopes

### "No veo Clients en el menú"
- Puede aparecer como **"OAuth clients"** o **"Clientes OAuth"**
- También puedes usar **"APIs & Services"** → **"Credentials"** → **"CREATE CREDENTIALS"**

### "La interfaz está en inglés"
- Puedes cambiar el idioma en la configuración de Google Cloud Console
- O seguir las instrucciones en inglés (son equivalentes)
