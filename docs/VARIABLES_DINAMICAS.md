# Variables Dinámicas - Mapeo Completo

## Índice
1. [Variables de Gmail](#variables-de-gmail)
2. [Variables de Airtable](#variables-de-airtable)
3. [Variables Globales n8n](#variables-globales-n8n)
4. [Variables de OpenAI](#variables-de-openai)
5. [Expresiones n8n](#expresiones-n8n)
6. [Validación y Testing](#validación-y-testing)

---

## Variables de Gmail

### Extracción en Nodo 01 (Trigger)

La entrada directa de Gmail trigger proporciona:

```json
{
  "id": "msg123abc",                          // ID único del email
  "threadId": "thread_abc123xyz",             // Thread ID para respuestas
  "from": {
    "value": [
      {
        "name": "Juan García",                // Nombre completo
        "address": "juan@empresa.com"         // Email
      }
    ]
  },
  "subject": "Consulta de automatización",    // Asunto
  "textPlain": "Hola, necesitamos...",        // Body en texto
  "snippet": "Hola, necesitamos...",          // Preview
  "date": "2026-07-15T14:23:00Z",            // Timestamp
  "headers": {                                 // Headers adicionales
    "from": "juan@empresa.com",
    "to": "ventas@empresa.com"
  }
}
```

### Normalización en Nodo 02

Mapeo a variables locales para uso posterior:

```javascript
{
  "lead_email": "={{$json.from.value[0].address}}",
  "lead_nombre": "={{$json.from.value[0].name || 'Contacto'}}",
  "asunto": "={{$json.subject}}",
  "mensaje": "={{$json.textPlain || $json.snippet || ''}}",
  "thread_id": "={{$json.threadId}}",
  "message_id": "={{$json.id}}"
}
```

### Uso Posterior

Una vez normalizadas, acceder en cualquier nodo con:

```javascript
// En el nodo ACTUAL (Nodo 02):
{{$json.lead_email}}
{{$json.lead_nombre}}

// En nodos POSTERIORES (Nodo 05+):
{{$node['02 Normalizar'].json.lead_email}}
{{$node['02 Normalizar'].json.lead_nombre}}
```

---

## Variables de Airtable

### Búsqueda en Nodo 04

Search devuelve array de records:

```json
{
  "records": [
    {
      "id": "rec_12345abcde",
      "fields": {
        "Email": "juan@empresa.com",
        "Nombre": "Juan García",
        "Empresa": "Tech Solutions S.A.",
        "Estado": "Procesado por IA",
        "Score IA": 65,
        "Historial": "2 interacciones previas"
      }
    }
  ]
}
```

### Acceso a Campos Airtable

```javascript
// Record ID (para update/delete):
{{$node['04 Buscar en Airtable'].json.records[0].id}}

// Campos específicos:
{{$node['04 Buscar en Airtable'].json.records[0].fields.Empresa}}
{{$node['04 Buscar en Airtable'].json.records[0].fields.Historial}}
{{$node['04 Buscar en Airtable'].json.records[0].fields.Score}}

// Safe access (si podría no existir):
{{$node['04 Buscar en Airtable'].json.records[0].fields.Empresa || 'No especificada'}}
```

### Update en Nodo 08

Los updates actualizan los campos:

```javascript
{
  "Estado": "Procesado por IA",
  "Score IA": "={{$json.ia_response_json.score_0_100}}",
  "Categoría": "={{$json.ia_response_json.categoria}}",
  "Prioridad": "={{$json.ia_response_json.prioridad}}",
  "Respuesta Sugerida": "={{$json.ia_response_json.respuesta_sugerida}}"
}
```

### Tabla Errores - Create

Cuando hay error (Nodo 17):

```javascript
{
  "Origen": "05 OpenAI - Clasificar Lead",
  "Tipo Error": "API OpenAI",
  "Detalle": "{{$json.message || 'Sin detalles'}}",
  "Lead Email": "{{$json.lead_email}}",
  "Estado": "Pendiente corrección",
  "Gravedad": "Crítica",
  "Timestamp": "={{new Date().toISOString()}}",
  "Stack Trace": "={{JSON.stringify($json)}}"
}
```

---

## Variables Globales n8n

### Configuración en Admin → Variables

```
AIRTABLE_BASE_ID = "appXXXXXXXXXXXXXX"
AIRTABLE_TABLE_LEADS = "tblEx4UKF4j0bkVvr"
AIRTABLE_TABLE_ERRORS = "tblERRORES_ID"
AIRTABLE_TABLE_CLIENTS = "tblCLIENTES_ID"
APPROVER_EMAIL = "aprobador@empresa.com"
SLACK_WEBHOOK = "https://hooks.slack.com/services/XXX/YYY/ZZZ"
OPENAI_MODEL = "gpt-3.5-turbo"
MAX_TOKENS = 500
TEMPERATURE = 0.7
```

### Acceso en Nodos

```javascript
// Sintaxis:
{{$env.NOMBRE_VARIABLE}}

// Ejemplos:
{{$env.AIRTABLE_BASE_ID}}           // "appXXXXXXXXXXXXXX"
{{$env.APPROVER_EMAIL}}             // "aprobador@empresa.com"
{{$env.SLACK_WEBHOOK}}              // "https://hooks..."
{{$env.MAX_TOKENS}}                 // 500

// En Airtable nodes:
"base": {"mode": "id", "value": "{{$env.AIRTABLE_BASE_ID}}"}

// En OpenAI node:
"model": "{{$env.OPENAI_MODEL}}",
"max_tokens": "={{$env.MAX_TOKENS}}"
```

### Ventajas

- ✅ No hardcodeadas en JSON
- ✅ Seguras en n8n (protegidas)
- ✅ Fácil cambio sin editar workflow
- ✅ Reutilizables en múltiples nodos

---

## Variables de OpenAI

### Input - System Message

```
"Sos un analista comercial B2B especializado en evaluación de leads.
Tu tarea es:
1. Clasificar leads según potencial comercial
2. Detectar datos faltantes que requieren seguimiento
3. Redactar respuestas profesionales y personalizadas
4. Devolver JSON estructurado para procesamiento automático

DEVUELVE SOLO JSON VÁLIDO. Nada más."
```

### Input - User Template

```
Lead: {{lead_nombre}} <{{lead_email}}>
Empresa: {{empresa}}
Asunto: {{asunto}}
Mensaje: {{mensaje}}
Historial Cliente: {{historial_cliente}}

Por favor analiza este lead y responde SOLO JSON válido.
```

### Expresión Completa en Nodo 05

```javascript
// User message (multiline):
"Lead: {{$node['02 Normalizar'].json.lead_nombre}} <{{$node['02 Normalizar'].json.lead_email}}>
Empresa: {{$node['04 Buscar en Airtable'].json.records[0].fields.Empresa || 'No especificada'}}
Asunto: {{$node['02 Normalizar'].json.asunto}}
Mensaje: {{$node['02 Normalizar'].json.mensaje}}
Historial Cliente: {{$node['04 Buscar en Airtable'].json.records[0].fields.Historial || 'Primer contacto'}}

Por favor analiza este lead y responde SOLO JSON válido."
```

### Output - Estructura Esperada

```json
{
  "message": {
    "role": "assistant",
    "content": "{\"categoria\":\"VIP\",\"score_0_100\":88,\"prioridad\":\"Alta\",\"datos_faltantes\":[],\"resumen\":\"...\",\"respuesta_sugerida\":\"...\",\"requiere_aprobacion\":true}"
  }
}
```

### Acceso en Nodos Posteriores

```javascript
// Raw JSON string:
{{$node['05 OpenAI'].json.message.content}}

// Después de parsear en Nodo 06:
{{$json.ia_response_json.score_0_100}}        // 88
{{$json.ia_response_json.categoria}}          // "VIP"
{{$json.ia_response_json.respuesta_sugerida}} // Email text

// En filtro IF (Nodo 07):
$json.ia_response_json.score_0_100 >= 70
```

---

## Expresiones n8n

### Sintaxis Básica

```javascript
// Variable actual:
{{$json.nombreCampo}}

// Nodo anterior:
{{$node['Nombre del Nodo'].json.campo}}

// Múltiples niveles:
{{$node['04 Buscar'].json.records[0].fields.Email}}

// Condicionales:
{{$node['04 Buscar'].json.records[0].fields.Empresa || 'Desconocida'}}
{{$json.lead_email ? 'Con email' : 'Sin email'}}

// Operaciones:
{{$json.mensaje.length}}
{{$json.score >= 70 ? 'Alto' : 'Bajo'}}

// Objetos/Arrays:
{{JSON.stringify($json.datos_faltantes)}}
{{JSON.parse($json.ia_response_json)}}

// Fechas:
{{new Date().toISOString()}}
{{$json.date.split('T')[0]}}
```

### Expresiones en IF Nodes

```javascript
// Comparación número:
$json.score_0_100 >= 70        // CORRECTO
$json.score_0_100 > 70         // CORRECTO
$json.score_0_100 === 88       // CORRECTO

// Comparación string:
$json.decision === "approved"  // CORRECTO
$json.categoria === "VIP"      // CORRECTO

// Array include:
$json.datos_faltantes.includes("email")  // CORRECTO

// Combinadas:
$json.score_0_100 >= 70 && $json.requiere_aprobacion === true
$json.email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)  // REGEX
```

---

## Validación y Testing

### Test de Expresiones Individuales

1. **Abrir nodo → "Test node"**
2. **Pestaña "Inputs"**: Ver datos del nodo anterior
3. **Pestaña "Outputs"**: Ver resultado de la expresión

### Ejemplo: Test Nodo 02 (Normalizar)

**Input** (desde Trigger):
```json
{
  "from": {"value": [{"name": "Juan", "address": "juan@empresa.com"}]},
  "subject": "Consulta",
  "textPlain": "Necesitamos...",
  "threadId": "abc123"
}
```

**Expresión** en campo "lead_email":
```javascript
={{$json.from.value[0].address}}
```

**Output esperado**:
```json
{
  "lead_email": "juan@empresa.com"
}
```

### Debug Mode

Para depurar flujos:

1. **Nodo 05 OpenAI**: Ver output JSON completo
2. **Nodo 06 Parsear**: Verificar parsing correcto
3. **Nodo 07 IF**: Chequear condición evaluada
4. **Nodo 08 Airtable**: Confirmar campos actualizados

### Errores Comunes

| Error | Causa | Solución |
|---|---|---|
| `Cannot read property 'json' of undefined` | Nodo anterior no retornó data | Verificar trigger/inputs |
| `Invalid JSON` | OpenAI no retornó JSON válido | Revisar prompt system |
| `Type mismatch in IF` | Comparar string con número | Usar parseInt() o Number() |
| `records[0] undefined` | Búsqueda en Airtable sin resultados | Agregar default: `\|\| 'valor'` |
| `$env variable empty` | Variable no configurada en n8n | Verificar Admin → Variables |

---

## Referencia Rápida de Nodos

### Nodo 01 (Trigger)
```
$json.from.value[0].name      → Nombre lead
$json.from.value[0].address   → Email lead
$json.subject                 → Asunto
$json.textPlain               → Mensaje
$json.threadId                → Thread ID
```

### Nodo 02 (Normalizar)
```
$json.lead_email              → juan@empresa.com
$json.lead_nombre             → Juan
$json.asunto                  → Consulta...
$json.mensaje                 → Hola...
$json.thread_id               → abc123...
```

### Nodo 04 (Airtable Search)
```
$json.records[0].id           → rec_12345
$json.records[0].fields.Empresa  → Tech S.A.
$json.records[0].fields.Historial → Contexto
```

### Nodo 05 (OpenAI)
```
$json.message.content         → JSON string desde OpenAI
```

### Nodo 06 (Parsear)
```
$json.ia_response_json.score_0_100     → 88
$json.ia_response_json.categoria       → "VIP"
$json.ia_response_json.respuesta_sugerida  → "Email..."
```

### Nodo 10 (Wait Webhook)
```
$json.decision                → "approved" | "rejected"
```

---

## Checklist de Variables

Antes de activar el flujo:

- ☑️ Trigger Gmail configura 6 variables
- ☑️ Nodo 02 accede a todas con `$node['02'].json.variable`
- ☑️ Nodo 05 user message usa {{}} correctamente
- ☑️ Nodo 06 parsea JSON con JSON.parse()
- ☑️ Nodo 07 IF compara NUMBER >= NUMBER
- ☑️ Nodo 08 Airtable usa $env.AIRTABLE_BASE_ID
- ☑️ Nodo 11 IF compara STRING === STRING
- ☑️ Nodo 12 Gmail usa {{$node['02'].json.lead_email}}
- ☑️ Variables globales configuradas en Admin

---

**Última actualización**: 15 de Julio, 2026
