# 🔧 Actualizar Client ID en .env

## Problema Detectado

El Client ID en tu `.env` no coincide con el que está configurado en Google Cloud Console.

**En Google Cloud Console:**
- Client ID: `173177570700-1k39dsosu2t854fuob0a8ngn621fdkte.apps.googleusercontent.com`

**En tu .env actual:**
- Client ID: `173177570700-j45hf4h1gss3roei9ncg941d85hhlmo1.apps.googleusercontent.com`

## Solución

### Opción 1: Actualizar .env con el Client ID correcto

1. Abre tu archivo `.env` en Termux:
   ```bash
   nano .env
   # o
   vi .env
   ```

2. Actualiza la línea `GOOGLE_CLIENT_ID` con el Client ID que ves en Google Cloud Console:
   ```
   GOOGLE_CLIENT_ID=173177570700-1k39dsosu2t854fuob0a8ngn621fdkte.apps.googleusercontent.com
   ```

3. Guarda el archivo:
   - En nano: `Ctrl+O`, luego `Enter`, luego `Ctrl+X`
   - En vi: `:wq` y luego `Enter`

4. Verifica que el Client Secret también sea el correcto (debería empezar con `GOCSPX-`)

### Opción 2: Usar setup.py para actualizar

```bash
python setup.py
```

Cuando te pida el Client ID, ingresa:
```
173177570700-1k39dsosu2t854fuob0a8ngn621fdkte.apps.googleusercontent.com
```

## Verificación

Después de actualizar, verifica que:
- ✅ El Client ID en `.env` coincida con Google Cloud Console
- ✅ El Redirect URI `http://localhost:8080` esté configurado (ya lo está ✅)
- ✅ El Client Secret sea el correcto

## Nota

El Redirect URI `http://localhost:8080` está correctamente configurado en Google Cloud Console, así que una vez que actualices el Client ID, debería funcionar.
