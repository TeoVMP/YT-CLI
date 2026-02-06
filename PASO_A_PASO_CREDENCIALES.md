# Guía Paso a Paso: Crear Credenciales OAuth2

## Estás en el Paso Correcto ✅

Si ves el dropdown con estas opciones:
- Web application
- Android
- Chrome Extension
- iOS
- TVs and Limited Input devices
- **Desktop app** ← ESTA ES LA CORRECTA
- Universal Windows Platform (UWP)

**Estás en el paso de crear las credenciales OAuth2, que es correcto.**

## Paso Actual: Seleccionar Application Type

### Lo que debes hacer AHORA:

1. **En el dropdown "Application type":**
   - Click en el dropdown
   - Selecciona **"Desktop app"** (Aplicación de escritorio)
   - **NO selecciones "Web application"** u otros tipos

2. **Name (Nombre):**
   - Escribe: `YouTube Bot Desktop`
   - O cualquier nombre descriptivo

3. **Click "CREATE" o "CREAR"**

4. **Se abrirá una ventana con:**
   - **Your Client ID**: Algo como `123456789-xxxxx.apps.googleusercontent.com`
   - **Your Client Secret**: Algo como `GOCSPX-xxxxx`
   
5. **Copia ambas credenciales inmediatamente**
   - ⚠️ Solo se muestran UNA VEZ
   - Guárdalas en un lugar seguro

## Sobre "User Type: External"

**"User Type: External"** NO aparece en esta pantalla porque:

- Se configura en **OAuth Consent Screen** (paso anterior)
- Si ya configuraste OAuth Consent Screen, ya está hecho
- Si NO lo configuraste, necesitas volver atrás

### ¿Ya configuraste OAuth Consent Screen?

**Si SÍ:**
- Continúa con este paso (selecciona "Desktop app")
- Ya está todo bien

**Si NO:**
- Necesitas configurar OAuth Consent Screen primero
- Ve a: "Google Auth Platform" → "OAuth consent screen"
- O: "APIs & Services" → "OAuth consent screen"
- Ahí sí verás "User Type: External"

## Resumen Visual

```
Google Cloud Console
│
├── Paso 1: OAuth Consent Screen
│   └── User Type: External ← AQUÍ se configura
│
└── Paso 2: Create OAuth Client ID (ESTÁS AQUÍ)
    └── Application type: Desktop app ← ESTO es lo que seleccionas ahora
```

## Instrucciones Completas

### Si ya configuraste OAuth Consent Screen:

1. ✅ En "Application type", selecciona **"Desktop app"**
2. ✅ Name: `YouTube Bot Desktop`
3. ✅ Click "CREATE"
4. ✅ Copia Client ID y Client Secret

### Si NO configuraste OAuth Consent Screen:

1. ⚠️ Ve primero a "OAuth consent screen"
2. ⚠️ Configura "User Type: External"
3. ⚠️ Luego vuelve aquí y continúa

## ¿Cómo saber si ya configuraste OAuth Consent Screen?

- Si cuando intentas crear credenciales te pide configurar consent screen primero → NO está configurado
- Si puedes crear credenciales directamente → Ya está configurado

## Siguiente Paso

Después de crear las credenciales y copiarlas:
- Vuelve al script `create_collective_accounts.py`
- Ingresa el Client ID y Client Secret cuando te los pida
