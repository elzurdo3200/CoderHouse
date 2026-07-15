# Documentación Técnica - Arquitectura LeadPilot AI

## Tabla de Contenidos
1. [Visión General](#visión-general)
2. [Componentes del Sistema](#componentes-del-sistema)
3. [Flujo Detallado por Nodo](#flujo-detallado-por-nodo)
4. [Rutas de Error](#rutas-de-error)
5. [Integración HITL](#integración-hitl)
6. [Seguridad y Resiliencia](#seguridad-y-resiliencia)

---

## Visión General

**LeadPilot AI** es un ecosistema autónomo que captura leads vía Gmail, los procesa con IA (OpenAI GPT), solicita validación humana (HITL) y contacta al cliente manteniendo contexto de conversación.

**Arquitectura**: Orquestador de flujos (n8n) + Base de datos (Airtable) + IA (OpenAI) + Canales (Gmail, Slack)

```
Gmail Email
    ↓
n8n Workflow
├─ Normalizar
├─ Validar
├─ Buscar Duplicados (Airtable)
├─ Clasificar con IA (OpenAI)
├─ Registrar resultado
├─ IF Score >= 70 → HITL (Slack)
│  └─ Wait for Webhook (aprobación humana)
│     ├─ Aprobar → Enviar Email
│     └─ Rechazar → NO contactar
└─ Errores → Tabla Errores (auditoría)
```

---

## Componentes del Sistema

### 1. **n8n (Orquestador)**
- **Rol**: Motor de flujo, coordina todos los pasos
- **Nodos**: 17+ nodos configurados
- **Trigger**: Gmail trigger con filtros inteligentes
- **Ejecución**: Síncrona con saveExecutionProgress

### 2. **Airtable (Base de Datos / Memoria)**
- **Tabla Leads**: Registro principal de leads procesados
- **Tabla Clientes**: Deduplicación de empresas
- **Tabla Errores**: Log de fallos para análisis
- **Relaciones**: Leads ↔ Clientes (1 cliente N leads)

### 3. **OpenAI (Motor IA)**
- **Modelo**: GPT-3.5-turbo (configurable)
- **Prompt**: Estructurado con variables dinámicas
- **Output**: JSON con clasificación, score, respuesta sugerida
- **Tokens**: Max 500 para optimizar costos

### 4. **Gmail (Entrada + Salida)**
- **Entrada**: Trigger escucha emails con filtros
- **Salida**: Envía respuesta en Thread ID original
- **Thread ID**: Mantiene conversación sin crear nuevo email

### 5. **Slack (Human-in-the-Loop)**
- **Notificación**: Alerta al aprobador con resumen del lead
- **Decisión**: Botones Aprobar/Rechazar
- **Thread ID**: Agrupa notificaciones en hilo

---

## Flujo Detallado por Nodo

### Fase 1: Captura y Normalización

#### Nodo 01: Trigger Gmail
```
Tipo: gmailTrigger
Configuración:
  - Filtro: subject:(Lead OR Consulta OR Presupuesto) newer_than:1d
  - Polling: cada minuto
  - Timezone: America/Argentina/Buenos_Aires

Salida JSON:
  {
    "from": {"value": [{"name": "Juan", "address": "juan@empresa.com"}]},
    "subject": "Consulta de automatización",
    "textPlain": "Hola, necesitamos...",
    "threadId": "abc123xyz789",
    "id": "msg123"
  }
```

**Validación**: 
- ✅ Filtro `newer_than:1d` previene bucles (solo últimas 24h)
- ✅ Palabras clave evitan spam (Lead, Consulta, Presupuesto)
- ✅ Polling cada minuto (balance costo/latencia)

---

#### Nodo 02: Normalizar Variables
```
Tipo: Set node
Entrada: Gmail email
Salida:
  {
    "lead_email": "juan@empresa.com",
    "lead_nombre": "Juan",
    "asunto": "Consulta de automatización",
    "mensaje": "Hola, necesitamos...",
    "thread_id": "abc123xyz789",
    "message_id": "msg123"
  }
```

**Validación**:
- ✅ Extrae variables SIN hardcoding
- ✅ Usa `.name || 'Contacto'` para nombre default
- ✅ `.textPlain || $json.snippet` para mensaje robustez
- ✅ Todas las variables dinámicas para flujo posterior

---

### Fase 2: Validación y Deduplicación

#### Nodo 03: Validar Datos
```
Tipo: IF node
Condiciones:
  1. Email valida: regex ^[^\s@]+@[^\s@]+\.[^\s@]+$
  2. Mensaje > 10 caracteres

Ruta TRUE: Continuar flujo
Ruta FALSE: → Error Handling (Datos Faltantes)
```

**Efectividad**:
- ✅ Bloquea emails sin cuerpo (spam)
- ✅ Valida formato email antes de procesamiento
- ✅ Comparación STRING vs STRING (tipos correctos)

---

#### Nodo 04: Buscar en Airtable
```
Tipo: Airtable Search
Búsqueda: WHERE Email = "juan@empresa.com"

Resultados:
  - Si existe: Usar record ID para update
  - Si no existe: Crear nuevo registro

Datos extraídos para contexto:
  - Empresa (de Airtable si existe)
  - Historial previo (si es cliente conocido)
```

**Deduplicación**:
- ✅ Impide contactos duplicados
- ✅ Actualiza scores previos
- ✅ Mantiene historial de interacciones

---

### Fase 3: Procesamiento IA

#### Nodo 05: OpenAI - Clasificar Lead
```
Tipo: OpenAI ChatCompletion

System Message:
  "Sos un analista comercial B2B. Clasificas leads, 
   detectas datos faltantes y redactas respuestas. 
   Devuelves SOLO JSON válido."

User Message Template:
  "Lead: {{lead_nombre}} <{{lead_email}}>
   Asunto: {{asunto}}
   Mensaje: {{mensaje}}
   
   Responde SOLO JSON con: categoria, score_0_100, prioridad, 
   datos_faltantes[], resumen, respuesta_sugerida, 
   requiere_aprobacion"

Configuración:
  - Model: gpt-3.5-turbo
  - Max Tokens: 500 (optimiza costos)
  - Temperature: 0.7 (balance creatividad/consistencia)
  - continueOnFail: true (→ Error Handling)
```

**JSON Expected Output**:
```json
{
  "categoria": "VIP | Potencial | Baja prioridad | Soporte | No calificado",
  "score_0_100": 88,
  "prioridad": "Alta | Media | Baja",
  "datos_faltantes": ["campo_1", "campo_2"],
  "resumen": "Resumen ejecutivo...",
  "respuesta_sugerida": "Email propuesto...",
  "requiere_aprobacion": true
}
```

**Validaciones Internas OpenAI**:
- ✅ No devuelve info hardcodeada (usa variables)
- ✅ Responde SOLO en JSON
- ✅ Límite de tokens optimizado

---

#### Nodo 06: Parsear JSON
```
Tipo: Set node
Operación: JSON.parse($json.message.content)

Convierte:
  String JSON → Objeto accesible
  
Permite acceso a:
  - $json.ia_response_json.score_0_100
  - $json.ia_response_json.categoria
  - $json.ia_response_json.respuesta_sugerida
```

---

### Fase 4: Decisiones Basadas en Score

#### Nodo 07: IF Score >= 70?
```
Tipo: IF node
Condición: score_0_100 >= 70

Ruta TRUE (Score >= 70):
  → Activar HITL (requiere aprobación humana)
  
Ruta FALSE (Score < 70):
  → Terminar flujo (no contactar sin aprobación)
```

**Lógica de Negocio**:
- Score < 50: No contactar (baja probabilidad)
- Score 50-69: Registrar pero no HITL (requiere revisión manual)
- Score >= 70: Activar HITL (preaprobado por IA, espera humano)
- Score > 90: VIP inmediato

---

#### Nodo 08: Registrar Resultado IA
```
Tipo: Airtable Update
Campos Actualizados:
  - Estado: "Procesado por IA"
  - Score IA: {{score_0_100}}
  - Categoría: {{categoria}}
  - Prioridad: {{prioridad}}
  - Respuesta Sugerida: {{respuesta_sugerida}}
  - Datos Faltantes: JSON.stringify(datos_faltantes)

Propósito: Auditoría y trazabilidad
```

---

### Fase 5: Human-in-the-Loop (HITL)

#### Nodo 09: Enviar a Slack - HITL
```
Tipo: HTTP Request (Webhook Slack)
Configuración:
  - Method: POST
  - URL: {{$env.SLACK_WEBHOOK}}
  
Payload:
  {
    "text": "📊 NUEVO LEAD VIP - {{lead_nombre}}",
    "blocks": [
      {
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": "*Lead:* {{lead_nombre}}\n*Email:* {{lead_email}}\n*Resumen:* {{resumen}}\n*Respuesta:*\n```{{respuesta_sugerida}}```"
        }
      },
      {
        "type": "actions",
        "elements": [
          {"type": "button", "text": "✅ Aprobar", "value": "approved", "action_id": "approve_lead"},
          {"type": "button", "text": "❌ Rechazar", "value": "rejected", "action_id": "reject_lead"}
        ]
      }
    ],
    "thread_ts": "{{thread_id}}"  // Agrupa en hilo Slack
  }
```

**Thread ID**: Agrupa notificaciones del mismo lead en Slack

---

#### Nodo 10: Wait for Webhook
```
Tipo: Wait node (Webhook)
Comportamiento:
  - Pausa ejecución indefinidamente
  - Espera respuesta desde Slack
  - Evita contacto automático

Datos esperados:
  {
    "decision": "approved" | "rejected"
  }
```

**Seguridad**: 
- ✅ NO contacta hasta confirmación humana
- ✅ Previene "Efecto Metralleta"
- ✅ Mantiene cadena de auditoría

---

#### Nodo 11: IF Aprobado por Humano?
```
Tipo: IF node
Condición: $json.decision === "approved"

Ruta VERDADERA:
  → Nodo 12 (Enviar Email al cliente)
  
Ruta FALSA:
  → Nodo 15 (Registrar rechazo, NO contactar)
```

---

### Fase 6: Salida y Cierre

#### Nodo 12: Enviar Email al Cliente
```
Tipo: Gmail Send
Campos:
  - To: {{lead_email}}
  - Subject: "Re: {{asunto}}" (mantiene contexto)
  - Body: {{respuesta_sugerida}}
  - CC: {{$env.APPROVER_EMAIL}}
  - inThreadOf: {{thread_id}}

Resultado:
  Email enviado en hilo original de Gmail
  (No crea nuevo thread, responde en el existente)
```

**Thread ID**:
- ✅ Mantiene conversación en hilo original
- ✅ Cliente ve respuesta en contexto
- ✅ Historial completo en Gmail

---

#### Nodo 13-14: Registrar Estado Final
```
Nodo 13: Set { "estado_final": "Contactado" }
Nodo 14: Airtable Update
  - Estado: "Contactado"
  - Decision Humana: "Aprobado"
```

---

#### Nodo 15: Registrar Rechazo
```
Tipo: Airtable Update
Campos:
  - Estado: "Rechazado"
  - Decision Humana: "Rechazado"

Nota: NO envía email al cliente
```

---

## Rutas de Error

### Error Route 1: Datos Faltantes

```
Trigger: Nodo 03 IF falla (email inválido o mensaje vacío)

Flujo:
  [03 IF FALSE] 
    ↓
  [16a Capturar error de validación]
    ↓
  [16b Registrar en tabla Errores]

Registro en Errores:
  - Origen: "03 Validar Datos"
  - Tipo Error: "Datos Faltantes"
  - Detalle: "Email inválido o mensaje vacío"
  - Estado: "Pendiente corrección"
  - Gravedad: "Alta"
```

**Beneficios**:
- ✅ NO procesa con IA (ahorra tokens)
- ✅ Auditoría completa de fallos
- ✅ Permite reintento manual después

---

### Error Route 2: Fallo API OpenAI

```
Trigger: Nodo 05 OpenAI error (timeout, credencial expirada, etc)

Configuración: continueOnFail = true

Flujo:
  [05 OpenAI ERROR] 
    ↓
  [17 Registrar fallo API IA en Errores]

Registro en Errores:
  - Origen: "05 OpenAI - Clasificar Lead"
  - Tipo Error: "API OpenAI"
  - Detalle: "Error message completo"
  - Stack Trace: JSON completo del error
  - Estado: "Pendiente corrección"
  - Gravedad: "Crítica"
```

**Resiliencia**:
- ✅ Flujo NO se detiene
- ✅ Error capturado y registrado
- ✅ Cliente NO recibe respuesta incompleta
- ✅ Permite reintento automático

---

## Integración HITL

### Flujo Completo de Aprobación

```
1. Score >= 70 en Nodo 07
   ↓
2. Nodo 09: Slack notification con botones
   └─ Aprobador abierto está en Slack
   └─ Lee resumen del lead
   └─ Ve respuesta propuesta
   └─ Hace click en [Aprobar] o [Rechazar]
   ↓
3. Nodo 10: Wait for Webhook
   └─ Flujo pausa esperando respuesta
   └─ Puede durar segundos a horas
   └─ Mientras tanto, otros leads se procesan en paralelo
   ↓
4A. SI Aprobado:
   └─ Nodo 11 IF TRUE
   └─ Nodo 12: Enviar Email
   └─ Nodo 13-14: Registrar "Contactado"
   
4B. SI Rechazado:
   └─ Nodo 11 IF FALSE
   └─ Nodo 15: Registrar "Rechazado"
   └─ NO enviar email
```

### Configuración de Slack Webhook

```bash
# En Admin → Variables de n8n:
SLACK_WEBHOOK = "https://hooks.slack.com/services/TXXX/BXXX/KXXX"

# Permiso en Slack:
- Workspace admin configura OAuth App
- Genera Incoming Webhook
- Selecciona canal destino (ej: #leads-approval)
- Copia URL en variable n8n
```

### Botones Interactivos

El payload de Slack incluye `action_id`:
- `approve_lead`: Click "Aprobar" → payload `{"decision": "approved"}`
- `reject_lead`: Click "Rechazar" → payload `{"decision": "rejected"}`

El Webhook de retorno entra en Nodo 10, activando Nodo 11 para procesar.

---

## Seguridad y Resiliencia

### Prevención de Bucles Infinitos

1. **Filtro temporal**: `newer_than:1d` limita Gmail a últimas 24h
2. **Estado tracking**: Lead marcado como "Procesado por IA" después de Nodo 06
3. **Trigger "From now on"**: No reprocesa histórico
4. **Validación de duplicados**: Nodo 04 busca previos

**Comprobación**: Si lead procesa 2 veces, segundo será "duplicado" → actualiza, no crea nuevo

---

### Validación de Tipos de Datos

| Nodo | Comparación | Tipo Correcto |
|---|---|---|
| Nodo 03 | `email REGEX` | STRING |
| Nodo 03 | `mensaje.length > 10` | NUMBER |
| Nodo 07 | `score_0_100 >= 70` | NUMBER >= NUMBER |
| Nodo 11 | `decision === "approved"` | STRING === STRING |

**Nunca**:
- ❌ Comparar número con string ("70" != 70)
- ❌ Usar operador `>` con strings ("88" > "70" → FALSE!)
- ❌ Omitir conversión de tipos

---

### No Hardcoding de Datos

**Correcto**: Todas las variables dinámicas
```javascript
// Template User OpenAI:
"Lead: {{$node['02 Normalizar'].json.lead_nombre}}"
```

**Incorrecto**: Datos fijos
```javascript
// NUNCA:
"Lead: Juan García"  // ← Hardcodeado
"API Key: sk-1234"   // ← CRÍTICO: nunca API keys
```

---

### Credenciales y Secretos

**En n8n Credentials**:
- Gmail OAuth2
- Airtable API Token
- OpenAI API Key

**En n8n Variables** (protegidas):
- `AIRTABLE_BASE_ID`
- `APPROVER_EMAIL`
- `SLACK_WEBHOOK`

**Nunca en JSON**:
- ✅ Credenciales van en n8n Credentials
- ✅ JSON exportable sin datos sensibles
- ✅ Seguro subir a GitHub

---

### Optimización de Costos OpenAI

```javascript
{
  "max_tokens": 500,      // ← Limita uso
  "temperature": 0.7,     // ← Consistencia
  "model": "gpt-3.5-turbo" // ← Económico vs GPT-4
}
```

**Cálculo estimado**:
- Prompt ~200 tokens
- Response ~300 tokens
- **Costo por lead**: ~$0.001 USD
- **1000 leads**: ~$1 USD

---

## Monitoreo y Debugging

### Logs a Revisar

1. **Tabla Leads (Airtable)**:
   - Estado progresa: Pendiente IA → Procesado por IA → Aprobado → Contactado
   - Score IA relleno
   - Datos Faltantes registrados

2. **Tabla Errores (Airtable)**:
   - Cualquier fallo registrado con detalles
   - Stack Trace disponible para debugging

3. **Slack Channel**:
   - Notificaciones de HITL
   - Botones de aprobación
   - Historial de decisiones

4. **Gmail Threads**:
   - Email enviado en hilo original
   - CC a aprobador
   - Respuesta propuesta en cuerpo

### Test de Nodos Individuales

```
1. Click nodo (ej: 05 OpenAI)
2. "Test node"
3. Ver output esperado
4. Si error: revisar inputs del nodo anterior
```

---

## Resumen Arquitectónico

| Componente | Función | Criticidad |
|---|---|---|
| Gmail Trigger | Captura leads | Alta |
| Normalizar | Variables dinámicas | Alta |
| Validar | Anti-spam/datos faltantes | Alta |
| Buscar Duplicados | Deduplicación | Media |
| OpenAI | Clasificación IA | Alta |
| Score Filter | Decide HITL | Alta |
| Slack HITL | Aprobación humana | Alta |
| Wait Webhook | Sincronización decisión | Alta |
| Gmail Send | Contacto cliente | Alta |
| Error Handling x2 | Resiliencia | Alta |

**Salud del Sistema**: Todos los nodos son críticos. Monitorear ejecuciones y tabla Errores regularmente.

---

**Última actualización**: 15 de Julio, 2026
**Versión**: 1.0
