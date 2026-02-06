# 🔒 Sistema de Cuenta Colectiva Monitoreada

## Descripción

Este bot está configurado para usar una **cuenta de Google colectiva** con sistema de monitoreo y protección integrado.

## Características de Protección

### 1. Monitoreo de Actividad
- ✅ Registra TODAS las acciones realizadas
- ✅ Detecta actividad sospechosa automáticamente
- ✅ Genera reportes de actividad
- ✅ Mantiene logs de hasta 10,000 acciones

### 2. Rate Limiting
- ✅ Límite diario de comentarios: 50 por defecto
- ✅ Límite horario de comentarios: 10 por defecto
- ✅ Bloqueo automático si se exceden límites
- ✅ Configurable en `.env`

### 3. Detección de Actividad Sospechosa
- ✅ Detecta actividad muy alta (más de 50 acciones/hora)
- ✅ Detecta spam de comentarios (más de 20/hora)
- ✅ Bloquea acciones automáticamente si detecta patrones sospechosos

### 4. Validación de Acciones
- ✅ Valida contenido antes de publicar
- ✅ Verifica límites antes de ejecutar
- ✅ Registra intentos bloqueados

## Configuración

### 1. Configurar Credenciales Colectivas

Crea el archivo `.env` con las credenciales de la cuenta colectiva:

```env
GOOGLE_CLIENT_ID=client_id_de_la_cuenta_colectiva
GOOGLE_CLIENT_SECRET=client_secret_de_la_cuenta_colectiva
REDIRECT_URI=http://localhost:8080

# Configuración de protección
COLLECTIVE_ACCOUNT_ENABLED=true
PROTECTION_ENABLED=true
MAX_COMMENTS_PER_DAY=50
MAX_COMMENTS_PER_HOUR=10
```

### 2. Primera Autorización

La primera vez que uses la cuenta colectiva:

1. Ejecuta cualquier comando que requiera autenticación
2. Se abrirá el navegador
3. **Inicia sesión con la cuenta colectiva** (no tu cuenta personal)
4. Autoriza la aplicación
5. El token se guarda en `token.json`

**IMPORTANTE**: Usa la cuenta colectiva, no tu cuenta personal.

## Uso

### Ver Reporte de Actividad

```bash
py main.py --activity-report
```

Muestra:
- Actividad de las últimas 24 horas
- Actividad de la última hora
- Desglose por tipo de acción
- Actividad sospechosa detectada
- Estado de límites de rate limiting

### Comandos Protegidos

Todos los comandos que modifican contenido están protegidos:

```bash
# Comentar (protegido)
py main.py --video-id VIDEO_ID --comment "Texto"

# Ver estadísticas (registrado)
py main.py --stats VIDEO_ID

# Exportar comentarios (registrado)
py main.py --export-comments VIDEO_ID
```

## Archivos de Log

### `downloads/activity_log.json`
Contiene todas las acciones realizadas con la cuenta colectiva:
- Tipo de acción
- Detalles completos
- Timestamp
- Resultado (éxito/bloqueado)

### Estructura del Log

```json
[
  {
    "timestamp": "2024-01-15T14:30:00",
    "action_type": "comment",
    "details": {
      "video_id": "dQw4w9WgXcQ",
      "text": "Comentario...",
      "text_length": 50
    }
  }
]
```

## Monitoreo en Tiempo Real

El sistema monitorea automáticamente:
- ✅ Cada acción antes de ejecutarse
- ✅ Rate limits en tiempo real
- ✅ Patrones sospechosos
- ✅ Intentos bloqueados

## Alertas

El sistema alerta automáticamente si detecta:
- ⚠️ Más de 50 acciones en 1 hora
- ⚠️ Más de 20 comentarios en 1 hora
- ⚠️ Exceso de límites diarios/horarios

## Seguridad

### Protección del Email
- ✅ Solo se solicita acceso a YouTube API
- ✅ NO se solicita acceso a Gmail/email
- ✅ Los tokens solo permiten acciones en YouTube

### Protección de la Cuenta
- ✅ Rate limiting automático
- ✅ Detección de actividad sospechosa
- ✅ Validación de contenido
- ✅ Logs completos de actividad

## Comandos Útiles

```bash
# Ver reporte de actividad
py main.py --activity-report

# Comentar con protección activa
py main.py --video-id VIDEO_ID --comment "Texto"

# Ver estadísticas (registrado)
py main.py --stats VIDEO_ID
```

## Notas Importantes

1. **Usa la cuenta colectiva**: Al autorizar, usa la cuenta colectiva, no tu cuenta personal
2. **Monitoreo activo**: Todas las acciones se registran automáticamente
3. **Protección automática**: El sistema bloquea acciones sospechosas automáticamente
4. **Logs persistentes**: Los logs se guardan en `downloads/activity_log.json`

## Troubleshooting

### "Acción bloqueada"
- Verifica los límites en `.env`
- Revisa el reporte de actividad: `py main.py --activity-report`
- Espera si has alcanzado límites horarios/diarios

### "Actividad sospechosa detectada"
- El sistema detectó patrones anormales
- Revisa los logs en `downloads/activity_log.json`
- Considera ajustar límites si es uso legítimo

---

**Recuerda**: Este sistema protege la cuenta colectiva monitoreando y limitando todas las acciones automáticamente.
