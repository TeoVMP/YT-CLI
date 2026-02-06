# 🔒 Guía de Privacidad y Ofuscación

## Protección de Datos Personales

Este bot incluye un sistema de ofuscación para proteger tu privacidad y la de la cuenta colectiva.

## Generar Nombres Genéricos

### Generar Sugerencias de Cuenta

Ejecuta:

```bash
py main.py --generate-account
```

Esto generará:
- ✅ Email genérico sugerido
- ✅ Nombre de cuenta genérico
- ✅ Nombre de canal de YouTube genérico
- ✅ Nombre de proyecto genérico

**Ejemplo de salida:**
```
📧 EMAIL SUGERIDO: user_a1b2c3d4@example.com
👤 NOMBRE DE CUENTA: digital_account_4521
📺 CANAL YOUTUBE: ContentBot789
☁️  PROYECTO: youtube-service-234
```

## Características de Ofuscación

### 1. Ofuscación Automática en Logs

Todos los logs automáticamente ofuscan:
- ✅ Emails (se convierten en emails genéricos)
- ✅ Client IDs (solo muestran parte)
- ✅ Client Secrets (completamente ocultos)

### 2. Enmascaramiento de Datos Sensibles

El sistema detecta y enmascara:
- Emails en texto
- IDs de cliente
- Secrets y tokens
- Información personal

### 3. Generación de Nombres Seguros

El generador crea nombres que:
- ✅ No revelan información personal
- ✅ Son completamente genéricos
- ✅ No identifican al usuario real
- ✅ Incluyen números aleatorios

## Recomendaciones para Crear la Cuenta

### Email

**Opción 1: Email Genérico**
- Usa el email sugerido por `--generate-account`
- O crea uno similar con formato genérico

**Opción 2: ProtonMail**
- Crea cuenta en ProtonMail con nombre genérico
- Usa ese email para crear cuenta de Google
- Mayor privacidad adicional

### Nombre de Cuenta

**Usa nombres genéricos:**
- ✅ `ContentBot123`
- ✅ `VideoService456`
- ✅ `MediaCollective789`
- ❌ `TuNombreReal`
- ❌ `TuEmpresa2024`

### Nombre de Proyecto en Google Cloud

**Usa nombres descriptivos pero genéricos:**
- ✅ `youtube-bot-123`
- ✅ `video-service-456`
- ✅ `media-api-789`
- ❌ `MiProyectoPersonal`
- ❌ `EmpresaXYZ`

## Archivos de Privacidad

### `obfuscation_mapping.json`
- Contiene mapeo de datos reales a ofuscados
- **NO subir a GitHub** (ya está en .gitignore)
- Permite recuperar datos si es necesario

### `account_suggestions.json`
- Contiene sugerencias de nombres generados
- **NO subir a GitHub** (ya está en .gitignore)
- Solo para referencia local

## Verificar Privacidad

### Verificar Logs

Los logs en `downloads/activity_log.json` automáticamente tienen:
- Emails ofuscados
- IDs parcialmente ocultos
- Sin información personal identificable

### Verificar Configuración

```bash
# Ver qué datos están ofuscados
python -c "from obfuscator import DataObfuscator; o = DataObfuscator(); print(o.get_obfuscated_info())"
```

## Mejores Prácticas

1. **Usa nombres genéricos**: No uses información personal
2. **Genera nombres aleatorios**: Ejecuta `--generate-account`
3. **No compartas credenciales**: Mantén `.env` privado
4. **Revisa logs**: Verifica que datos estén ofuscados
5. **Usa ProtonMail**: Para mayor privacidad del email

## Ejemplo Completo

```bash
# 1. Generar nombres genéricos
py main.py --generate-account

# 2. Crear cuenta de Google con el email sugerido
# 3. Usar el nombre de cuenta sugerido
# 4. Crear proyecto con el nombre sugerido
# 5. Configurar credenciales
py setup.py

# 6. Verificar que logs estén ofuscados
py main.py --activity-report
```

---

**Recuerda**: La privacidad es importante. Usa nombres genéricos y mantén los archivos sensibles privados.
