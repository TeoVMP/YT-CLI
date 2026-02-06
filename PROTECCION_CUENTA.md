# 🔒 Protección de Cuenta - Cómo Funciona

## Resumen Ejecutivo

Este bot está diseñado para **proteger tu cuenta de Google** usando OAuth2 con **scopes (permisos) limitados**. Esto significa que:

- ✅ **Solo se puede acceder a YouTube API** para comentar
- ❌ **NO se puede acceder al email/Gmail**
- ❌ **NO se puede acceder a la bandeja de entrada**
- ✅ **Los tokens solo permiten acciones en YouTube**

## Cómo Funciona la Protección

### 1. Scopes OAuth2 Limitados

El bot solo solicita **un scope específico**:

```
https://www.googleapis.com/auth/youtube.force-ssl
```

Este scope permite:
- ✅ Comentar en videos
- ✅ Gestionar comentarios propios
- ✅ Eliminar comentarios propios
- ❌ **NO permite acceso a Gmail**
- ❌ **NO permite acceso al email**

### 2. Configuración en el Código

En `config.py`, los scopes están definidos así:

```python
YOUTUBE_SCOPES = [
    'https://www.googleapis.com/auth/youtube.force-ssl',  # Solo YouTube
]

# NO incluir estos scopes (protección del email):
# 'https://www.googleapis.com/auth/gmail.readonly'  ❌
# 'https://mail.google.com/'  ❌
# 'https://www.googleapis.com/auth/gmail.modify'  ❌
```

### 3. Proceso de Autorización

Cuando ejecutas el bot por primera vez:

1. Se abre tu navegador
2. Google muestra **exactamente qué permisos se solicitan**
3. Verás algo como: "Esta aplicación quiere acceder a YouTube"
4. **NO verás**: "Esta aplicación quiere acceder a Gmail"
5. Puedes verificar los permisos antes de autorizar

### 4. Tokens con Permisos Limitados

Los tokens OAuth2 generados **solo tienen los permisos solicitados**:

- Si alguien obtiene el token → Solo puede usarlo para YouTube API
- **NO puede** acceder a Gmail con ese token
- **NO puede** leer emails con ese token
- **NO puede** cambiar la contraseña con ese token

## Verificación de Seguridad

### Cómo Verificar que Solo se Solicita YouTube

1. **Al autorizar**: Google muestra los permisos solicitados
2. **En Google Cloud Console**: Ve a "Credenciales" → Tu OAuth2 → Verifica scopes
3. **En el código**: Revisa `config.py` línea `YOUTUBE_SCOPES`

### Qué NO Está Habilitado

En Google Cloud Console, asegúrate de que **NO** estén habilitados:
- ❌ Gmail API
- ❌ Google Mail API
- ❌ Cualquier servicio de email

Solo debe estar habilitado:
- ✅ YouTube Data API v3

## Protección Adicional

### 1. Separación de Credenciales

- **Credenciales OAuth2**: Solo para YouTube API
- **Email de recuperación**: Puede estar en ProtonMail o cualquier otro servicio
- **Contraseña de Google**: No se usa en el bot (solo tokens OAuth2)

### 2. Tokens con Expiración

Los tokens OAuth2 tienen:
- **Expiración**: Se renuevan automáticamente
- **Refresh tokens**: Permiten renovar sin re-autorizar
- **Alcance limitado**: Solo YouTube API

### 3. Revocación de Acceso

Si necesitas revocar el acceso:
1. Ve a [Google Account Security](https://myaccount.google.com/permissions)
2. Encuentra la aplicación
3. Revoca el acceso
4. El token dejará de funcionar inmediatamente

## Preguntas Frecuentes

### ¿Puede alguien acceder a mi email con este bot?

**NO**. El bot solo solicita permisos de YouTube. Incluso si alguien obtiene el token, solo puede usarlo para acciones en YouTube, no para acceder a Gmail.

### ¿Qué pasa si comparto las credenciales OAuth2?

Si compartes las credenciales (Client ID y Secret):
- Otros pueden crear tokens OAuth2
- Pero esos tokens **solo tendrán acceso a YouTube**
- **NO tendrán acceso al email**

### ¿Puedo usar ProtonMail para la cuenta?

Sí, puedes crear la cuenta de Google con ProtonMail. El bot seguirá funcionando igual porque:
- Solo necesita acceso a YouTube API
- No necesita acceso al email
- El email de recuperación puede estar en cualquier servicio

### ¿Cómo sé que mi email está protegido?

1. Verifica los scopes solicitados al autorizar
2. Revisa `config.py` - solo hay scopes de YouTube
3. En Google Cloud Console, verifica que Gmail API NO esté habilitado
4. Los tokens solo funcionan para YouTube API

## Resumen

✅ **Tu email está protegido** porque:
- El bot solo solicita permisos de YouTube
- Los tokens solo permiten acciones en YouTube
- No se habilita Gmail API en Google Cloud Console
- Puedes verificar los permisos antes de autorizar

❌ **NO se puede acceder al email** porque:
- No se solicitan scopes de Gmail
- Los tokens no tienen permisos de email
- Google no permite acceso sin permisos explícitos

---

**Recuerda**: Siempre verifica los permisos que Google muestra al autorizar la aplicación. Si ves algo sobre Gmail o email, **NO autorices** y revisa la configuración.
