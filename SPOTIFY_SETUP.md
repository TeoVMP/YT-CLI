# Guía de Configuración de Spotify

Esta guía te ayudará a configurar las credenciales de Spotify para usar la funcionalidad de reproducir playlists de Spotify.

## 📋 Pasos para Obtener Credenciales

### 1. Acceder al Dashboard de Spotify

Ve a: **https://developer.spotify.com/dashboard**

Inicia sesión con tu cuenta de Spotify (puedes usar tu cuenta gratuita).

### 2. Crear una Nueva Aplicación

1. Haz clic en el botón **"Create app"** o **"Create an app"**
2. Completa el formulario:
   - **App name**: Cualquier nombre (ej: `YTLikesBot`, `My YouTube Bot`)
   - **App description**: Opcional (ej: `Bot para reproducir playlists de Spotify`)
   - **Website**: Opcional (puedes dejar vacío o poner `http://localhost`)
   - **Redirect URI**: `http://localhost:8080`
   - **What API/SDKs are you planning to use?**: Marca "Web API"
   - Marca la casilla **"I understand and agree..."**
3. Haz clic en **"Save"**

### 3. Obtener las Credenciales

Una vez creada la app, verás la página de configuración:

1. **Client ID**: Está visible en la parte superior. Cópialo.
2. **Client Secret**: 
   - Haz clic en el botón **"View client secret"** o **"Show client secret"**
   - Se mostrará el Client Secret. **Cópialo inmediatamente** (solo se muestra una vez)

### 4. Configurar en el Proyecto

1. Abre o crea el archivo `.env` en la raíz del proyecto
2. Agrega las siguientes líneas:

```env
SPOTIFY_CLIENT_ID=tu_client_id_aqui
SPOTIFY_CLIENT_SECRET=tu_client_secret_aqui
SPOTIFY_REDIRECT_URI=http://localhost:8080
```

**Ejemplo:**
```env
SPOTIFY_CLIENT_ID=abc123def456ghi789jkl012mno345pqr
SPOTIFY_CLIENT_SECRET=xyz789uvw456rst123opq012klm345nop
SPOTIFY_REDIRECT_URI=http://localhost:8080
```

### 5. Verificar la Configuración

Ejecuta el comando para probar:

```bash
python main.py --play-spotify-playlist "https://open.spotify.com/playlist/TU_PLAYLIST_ID"
```

## 🔒 Tipos de Playlists

### Playlists Públicas
- ✅ Funcionan con solo Client ID y Client Secret
- ✅ No requieren autenticación adicional
- ✅ La mayoría de playlists de Spotify son públicas

### Playlists Privadas
- ⚠️ Requieren autenticación OAuth adicional
- ⚠️ Necesitas iniciar sesión con tu cuenta de Spotify
- 💡 Para la mayoría de casos, las playlists públicas son suficientes

## ❓ Solución de Problemas

### Error: "Cliente de Spotify no inicializado"
- Verifica que el archivo `.env` existe
- Verifica que `SPOTIFY_CLIENT_ID` y `SPOTIFY_CLIENT_SECRET` están configurados
- Asegúrate de que no hay espacios extra en los valores

### Error: "401 Unauthorized"
- Verifica que las credenciales son correctas
- Asegúrate de que copiaste el Client Secret completo
- Intenta crear una nueva app si el problema persiste

### Error: "Playlist no encontrada"
- Verifica que la URL de la playlist es correcta
- Asegúrate de que la playlist es pública (si no tienes autenticación OAuth)
- Prueba con otra playlist pública

## 📚 Recursos Adicionales

- **Spotify Developer Dashboard**: https://developer.spotify.com/dashboard
- **Documentación de la API**: https://developer.spotify.com/documentation/web-api
- **Guía de Autenticación**: https://developer.spotify.com/documentation/general/guides/authorization/

## 💡 Notas Importantes

- Las credenciales son **gratuitas** y no tienen límite de uso para uso personal
- El Client Secret es **sensible**, no lo compartas públicamente
- El archivo `.env` está en `.gitignore`, así que tus credenciales no se subirán a GitHub
- Puedes crear múltiples apps si necesitas diferentes configuraciones
