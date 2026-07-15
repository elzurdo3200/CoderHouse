# OpenAI User Template - Dinámico con Variables n8n

## Template Principal (COPIA ESTO EN n8n OpenAI Node)

```
Lead: {{lead_nombre}} <{{lead_email}}>
Empresa: {{empresa}}
Asunto: {{asunto}}
Mensaje: {{mensaje}}
Historial Cliente: {{historial_cliente}}

Por favor analiza este lead y responde SOLO JSON válido.
```

---

## Mapeo de Variables desde Gmail

| Variable | Origen | Expresión n8n |
|---|---|---|
| `{{lead_nombre}}` | Email From name | `={{$node["02 Normalizar"].json.lead_nombre}}` |
| `{{lead_email}}` | Email From address | `={{$node["02 Normalizar"].json.lead_email}}` |
| `{{asunto}}` | Email Subject | `={{$node["02 Normalizar"].json.asunto}}` |
| `{{mensaje}}` | Email Body (plain text) | `={{$node["02 Normalizar"].json.mensaje}}` |
| `{{empresa}}` | Extraído de mensaje o Airtable | `={{$node["04 Buscar en Airtable"].json.empresa || "No especificada"}}` |
| `{{historial_cliente}}` | Lookup en tabla Clientes | `={{$node["04 Buscar en Airtable"].json.historial || "Primer contacto"}}` |

---

## Ejemplo de Nodo Set en n8n (Paso 02 - Normalizar)

```javascript
// Nodo: "02 Normalizar variables dinamicas"
// Tipo: "Set" (Set node)

{
  "lead_nombre": "={{$json.from.value[0].name || 'Contacto'}}",
  "lead_email": "={{$json.from.value[0].address}}",
  "asunto": "={{$json.subject}}",
  "mensaje": "={{$json.textPlain || $json.snippet}}",
  "thread_id": "={{$json.threadId}}"
}
```

---

## Ejemplo de Nodo OpenAI en n8n (Paso 05)

```javascript
// Nodo: "05 OpenAI - Clasificar Lead"
// Tipo: "OpenAI ChatCompletion"

{
  "model": "gpt-3.5-turbo",
  "max_tokens": 500,
  "temperature": 0.7,
  "system_message": "[Ver openai_system_prompt.md]",
  "user_message": "Lead: {{$node['02 Normalizar'].json.lead_nombre}} <{{$node['02 Normalizar'].json.lead_email}}>\nEmpresa: {{$node['03 Validar Datos'].json.empresa || 'No especificada'}}\nAsunto: {{$node['02 Normalizar'].json.asunto}}\nMensaje: {{$node['02 Normalizar'].json.mensaje}}\nHistorial Cliente: {{$node['04 Buscar en Airtable'].json.historial || 'Primer contacto'}}\n\nResponde SOLO JSON válido."
}
```

---

## Validación de Variables en Filtros (IF Nodes)

### Filtro 1: Datos Completos
```javascript
// "03 IF - Datos válidos?"
// Condición:
$node["02 Normalizar"].json.lead_email && 
$node["02 Normalizar"].json.mensaje
```

### Filtro 2: Score Alto
```javascript
// "07 IF - Score >= 70?"
// Condición:
$json.score_0_100 >= 70
```

### Filtro 3: Aprobación Humana
```javascript
// "10 IF - Aprobado por humano?"
// Condición:
$json.Decision_Humana === "Aprobado"
```

---

## Variables Globales de n8n

Configurar en: **Admin → Variables**

```
AIRTABLE_BASE_ID = "appXXXXXXXXXXXXXX"
AIRTABLE_TABLE_LEADS = "tblEx4UKF4j0bkVvr"
AIRTABLE_TABLE_ERRORS = "tblERRORES_ID"
AIRTABLE_TABLE_CLIENTS = "tblCLIENTES_ID"
APPROVER_EMAIL = "aprobador@empresa.com"
SLACK_WEBHOOK = "https://hooks.slack.com/services/XXX/YYY/ZZZ"
OPENAI_MODEL = "gpt-3.5-turbo"
MAX_TOKENS = 500
```

**Acceder en el flujo:**
```javascript
$env.AIRTABLE_BASE_ID
$env.APPROVER_EMAIL
$env.SLACK_WEBHOOK
```

---

## Hardcoding - QUÉ NO HACER ❌

### ❌ INCORRECTO: Variables hardcodeadas
```javascript
// NO HAGAS ESTO
"Lead: Juan García <juan@empresa.com>"  // Hardcodeado
"Empresa: MiEmpresa"  // Hardcodeado
"API Key: sk-1234567890"  // NUNCA hardcodear keys
```

### ✅ CORRECTO: Variables dinámicas
```javascript
// SÍ HACES ESTO
"Lead: {{$node['02 Normalizar'].json.lead_nombre}} <{{$node['02 Normalizar'].json.lead_email}}>"
"Empresa: {{$node['04 Buscar en Airtable'].json.empresa || 'No especificada'}}"
// API keys en Credentials, NO en JSON
```

---

## Prueba de Variables en n8n

### Paso 1: Usar "Test" del nodo OpenAI
```
1. Click en nodo "05 OpenAI"
2. Click "Test node"
3. Ver en Output si aparecen las variables correctas
4. Si vacías, revisar paso anterior (02 Normalizar)
```

### Paso 2: Ejecutar workflow completo
```
1. Click "Execute Workflow"
2. Esperar a que procese
3. Ver en logs si hay errores de variables
4. Si error: revisar expresiones con $node.path.json
```

### Paso 3: Validar JSON de salida
```javascript
// Verificar en "05 OpenAI" output:
{
  "categoria": "Potencial",
  "score_0_100": 72,
  "prioridad": "Alta",
  // ...
}
// Si no ve JSON, check en System Prompt
```

---

## Ejemplo Completo de Variables en Acción

### Email original desde Gmail:
```
From: María López <maria@saas.com>
Subject: Necesitamos solución de automatización
Body: Hola, tenemos un problema con nuestro flujo de datos...
```

### Variables normalizadas en Paso 02:
```json
{
  "lead_nombre": "María López",
  "lead_email": "maria@saas.com",
  "asunto": "Necesitamos solución de automatización",
  "mensaje": "Hola, tenemos un problema con nuestro flujo de datos...",
  "thread_id": "abc123xyz789"
}
```

### User message enviado a OpenAI:
```
Lead: María López <maria@saas.com>
Empresa: No especificada
Asunto: Necesitamos solución de automatización
Mensaje: Hola, tenemos un problema con nuestro flujo de datos...
Historial Cliente: Primer contacto

Por favor analiza este lead y responde SOLO JSON válido.
```

### JSON respondido por OpenAI:
```json
{
  "categoria": "Potencial",
  "score_0_100": 65,
  "prioridad": "Media",
  "datos_faltantes": ["empresa", "presupuesto"],
  "resumen": "Lead SaaS con necesidad de automatización clara. Falta empresa y contexto de presupuesto.",
  "respuesta_sugerida": "Hola María,\n\nGracias por escribir...",
  "requiere_aprobacion": false
}
```

### Registro en Airtable (Paso 06):
```
Nombre: María López
Email: maria@saas.com
Score IA: 65
Categoría: Potencial
Prioridad: Media
Estado: Procesado por IA
Decision Humana: Pendiente
Datos Faltantes: ["empresa", "presupuesto"]
Respuesta Sugerida: [Guardada]
```

---

## Tips de Debugging

**Si las variables aparecen vacías:**
1. ¿El Gmail trigger devolvió data?
   → Ver logs del trigger
2. ¿El Set node (02) tiene el mapeo correcto?
   → Verificar expresiones con $json.
3. ¿El IF node validó bien?
   → Debuggear con test data falso

**Si OpenAI devuelve error:**
1. ¿El JSON del prompt es válido?
   → Validar en jsonlint.com
2. ¿Las variables están reemplazadas?
   → Ver "Test node" output
3. ¿Max tokens es correcto?
   → Reducir de 500 a 300 si falla
