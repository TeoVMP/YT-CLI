# Arquitectura Multi-Cuenta Escalable

## Descripción

Sistema escalable para gestionar múltiples cuentas colectivas de Google, con balanceo de carga automático, monitoreo de cuota y failover.

## Componentes

### 1. AccountManager (`account_manager.py`)
Gestiona múltiples cuentas y sus credenciales.

**Funciones principales:**
- Carga configuración de múltiples cuentas
- Obtiene clientes autenticados para cada cuenta
- Cache de clientes para mejor rendimiento

### 2. QuotaMonitor (`quota_monitor.py`)
Monitorea el uso de cuota de cada cuenta.

**Funciones principales:**
- Registra uso de cuota por operación
- Verifica disponibilidad de cuota
- Genera reportes de uso
- Encuentra cuentas con cuota disponible

### 3. LoadBalancer (`load_balancer.py`)
Distribuye carga entre múltiples cuentas.

**Estrategias disponibles:**
- `round_robin`: Rotación equitativa
- `least_used`: Usa la cuenta menos utilizada
- `random`: Selección aleatoria

### 4. FailoverSystem (`failover.py`)
Sistema de failover automático.

**Funciones principales:**
- Cambia automáticamente a otra cuenta si una falla
- Maneja cuentas agotadas
- Recupera cuentas cuando tienen cuota disponible

### 5. ActivityAggregator (`activity_aggregator.py`)
Consolida logs de todas las cuentas.

**Funciones principales:**
- Agrega actividad de todas las cuentas
- Genera estadísticas consolidadas
- Exporta logs agregados

## Configuración

### 1. Crear archivo de configuración

Copia el ejemplo y completa con tus credenciales:

```bash
copy multi_account_config.json.example multi_account_config.json
```

### 2. Editar configuración

Edita `multi_account_config.json`:

```json
{
  "accounts": [
    {
      "id": "account_1",
      "client_id": "tu_client_id_cuenta_1",
      "client_secret": "tu_client_secret_cuenta_1",
      "token_file": "token_account_1.json",
      "max_comments_per_day": 50,
      "priority": 1
    },
    {
      "id": "account_2",
      "client_id": "tu_client_id_cuenta_2",
      "client_secret": "tu_client_secret_cuenta_2",
      "token_file": "token_account_2.json",
      "max_comments_per_day": 50,
      "priority": 2
    }
  ],
  "load_balancing": {
    "strategy": "round_robin",
    "failover_enabled": true
  }
}
```

### 3. Autorizar cada cuenta

La primera vez que uses cada cuenta, se abrirá el navegador para autorizar:

```python
from account_manager import AccountManager

manager = AccountManager()
client = manager.get_account("account_1")
# Se abrirá navegador para autorizar cuenta 1
```

## Uso Básico

### Usar una cuenta específica

```python
from account_manager import AccountManager

manager = AccountManager()
client = manager.get_account("account_1")

if client:
    result = client.comment_video("VIDEO_ID", "Comentario")
    print(result)
```

### Usar balanceador de carga

```python
from account_manager import AccountManager
from quota_monitor import QuotaMonitor
from load_balancer import LoadBalancer

manager = AccountManager()
quota_monitor = QuotaMonitor(manager)
balancer = LoadBalancer(manager, quota_monitor)

# Obtener cliente automáticamente según estrategia
client = balancer.get_client_for_operation("comment")

if client:
    result = client.comment_video("VIDEO_ID", "Comentario")
```

### Usar con failover

```python
from account_manager import AccountManager
from quota_monitor import QuotaMonitor
from load_balancer import LoadBalancer
from failover import FailoverSystem

manager = AccountManager()
quota_monitor = QuotaMonitor(manager)
balancer = LoadBalancer(manager, quota_monitor)
failover = FailoverSystem(manager, quota_monitor, balancer)

# Obtener cliente con failover automático
client = failover.get_client_with_failover("comment")

if client:
    result = client.comment_video("VIDEO_ID", "Comentario")
```

## Monitoreo

### Ver reporte de cuota

```python
from account_manager import AccountManager
from quota_monitor import QuotaMonitor

manager = AccountManager()
quota_monitor = QuotaMonitor(manager)
quota_monitor.print_quota_report()
```

### Ver actividad agregada

```python
from account_manager import AccountManager
from activity_aggregator import ActivityAggregator

manager = AccountManager()
aggregator = ActivityAggregator(manager)
aggregator.print_aggregated_report(hours=24)
```

## Capacidad por Cuenta

**Cuota diaria**: 10,000 unidades (gratis)

**Costo por operación:**
- Comentar: 50 unidades
- Estadísticas: 1 unidad
- Obtener comentarios: 1 unidad

**Con límites actuales (50 comentarios/día):**
- Comentarios: 50 × 50 = 2,500 unidades
- Estadísticas: ~100 unidades
- Obtener comentarios: ~500 unidades
- **Total: ~3,100 unidades/día**
- **Disponible: ~6,900 unidades/día**

## Recomendaciones

### Para empezar
- **1 cuenta**: Suficiente para uso básico (50 comentarios/día)

### Para escalar
- **2-3 cuentas**: Para uso medio (100-150 comentarios/día)
- **5-10 cuentas**: Para uso intensivo (200+ comentarios/día)

### Estrategia de distribución
- Usa `round_robin` para distribución equitativa
- Usa `least_used` para mejor balanceo
- Activa `failover_enabled` para alta disponibilidad

## Archivos Generados

- `token_account_1.json`, `token_account_2.json`, etc.: Tokens OAuth2 por cuenta
- `quota_usage.json`: Log de uso de cuota
- `activity_log_*.json`: Logs de actividad por cuenta
- `aggregated_activity_*.json`: Logs agregados

## Troubleshooting

### "Cuenta no encontrada"
- Verifica que el `id` en la configuración coincida
- Asegúrate de que `multi_account_config.json` existe

### "Cuota insuficiente"
- Verifica uso con `quota_monitor.print_quota_report()`
- Considera agregar más cuentas
- Espera al siguiente día para reset de cuota

### "Error de autenticación"
- Verifica credenciales en `multi_account_config.json`
- Elimina `token_*.json` y vuelve a autorizar
- Verifica que los scopes sean solo de YouTube
