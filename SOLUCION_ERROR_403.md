# Solución: Error 403 - App en Modo de Prueba

## Problema

Error: `absfjo3p12 has not completed the Google verification process`
Error 403: `access_denied`

**Causa**: La aplicación está en modo "Testing" y tu cuenta no está en la lista de usuarios de prueba.

## Solución: Agregar Usuario de Prueba

### Paso 1: Ir a OAuth Consent Screen

1. Ve a: https://console.cloud.google.com/
2. Selecciona tu proyecto
3. Ve a: **"Google Auth Platform"** → **"OAuth consent screen"**
   - O: **"APIs & Services"** → **"OAuth consent screen"**

### Paso 2: Agregar Test Users

1. En la página de OAuth Consent Screen, busca la sección **"Test users"** o **"Usuarios de prueba"**
2. Click en **"ADD USERS"** o **"AÑADIR USUARIOS"**
3. Agrega tu email: `teovalentin.tv@gmail.com`
4. Click **"ADD"** o **"AÑADIR"**
5. Click **"SAVE"** o **"GUARDAR"**

### Paso 3: Verificar

Después de agregar tu cuenta como test user:
- Espera unos segundos (puede tardar hasta 1 minuto)
- Intenta autorizar de nuevo
- Debería funcionar ahora

## Pasos Detallados (con capturas de pantalla conceptuales)

### En OAuth Consent Screen:

```
┌─────────────────────────────────────────┐
│ OAuth consent screen                    │
├─────────────────────────────────────────┤
│                                         │
│ Publishing status: Testing              │
│                                         │
│ Test users                              │
│ ┌─────────────────────────────────────┐ │
│ │ [ADD USERS] button                  │ │
│ │                                     │ │
│ │ Users:                               │ │
│ │ • teovalentin.tv@gmail.com          │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [SAVE] button                           │
└─────────────────────────────────────────┘
```

## Si No Ves la Sección de Test Users

1. Asegúrate de estar en **"OAuth consent screen"**
2. Desplázate hacia abajo en la página
3. Busca la sección **"Test users"** o **"Usuarios de prueba"**
4. Si no aparece, puede que necesites completar primero otros pasos:
   - App information (Información de la app)
   - Scopes (Alcances)

## Verificar Estado de la App

En OAuth Consent Screen verás:
- **Publishing status**: "Testing" (modo de prueba)
- Esto significa que solo usuarios de prueba pueden acceder

## Opciones Adicionales

### Opción 1: Mantener en Modo Testing (Recomendado para desarrollo)
- Agrega usuarios de prueba según necesites
- Máximo 100 usuarios de prueba
- No requiere verificación de Google

### Opción 2: Publicar la App (Requiere verificación)
- Para uso público necesitas verificación de Google
- Proceso más largo y complejo
- Solo necesario si quieres que cualquiera use la app

## Después de Agregar Test User

1. Espera 30-60 segundos
2. Intenta autorizar de nuevo:
   ```bash
   py main.py --stats l5ls08f-eEU
   ```
3. Debería funcionar ahora

## Troubleshooting

### "No puedo encontrar Test users"
- Asegúrate de haber completado "App information" primero
- Desplázate hacia abajo en la página
- Busca "Test users" o "Usuarios de prueba"

### "Ya agregué mi cuenta pero sigue sin funcionar"
- Espera 1-2 minutos (puede tardar en propagarse)
- Cierra y vuelve a abrir el navegador
- Intenta autorizar de nuevo

### "Quiero agregar más usuarios"
- Puedes agregar hasta 100 usuarios de prueba
- Cada uno debe tener acceso a la cuenta de Google que uses
