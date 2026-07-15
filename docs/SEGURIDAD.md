# Check de Seguridad - LeadPilot AI

## Resumen Ejecutivo

✅ **SISTEMA SEGURO PARA PRODUCCIÓN**

Implementadas todas las validaciones requeridas:
- Anti-bucles infinitos
- Validación de tipos correcta
- Prompts dinámicos (sin hardcoding)
- Credenciales protegidas
- Error handling robusto

---

## 1. Prevención de Bucles Infinitos

### Implementación 1: Filtro de Tiempo Gmail

**Nodo 01 - Gmail Trigger**:
```javascript
filters: {
  q: "subject:(Lead OR Consulta OR Presupuesto) newer_than:1d"
}
```

**Efecto**:
- 🔒 Limita búsqueda a últimas 24 horas
- 🔒 Nunca reprocesa emails históricos
- 🔒 Cada ejecución busca solo nuevos

**Test**:
- Ejecutar día 1 → Procesa emails de día 1
- Ejecutar día 2 → Procesa solo nuevos de día 2
- Ejecutar día 2 (2x) → Mismo resultado (no duplica)

---

### Implementación 2: Estado Tracking en Airtable

**Nodo 08 - Registrar resultado IA**:
```javascript
Update: {
  "Estado": "Procesado por IA"
}
```

**Efecto**:
- 🔒 Marca lead como procesado inmediatamente
- 🔒 Si reprocesa, busca ve estado anterior
- 🔒 Aplicación de negocios evita reprocesamiento

**Estados Válidos**:
- "Pendiente IA" → Nuevo lead
- "Procesado por IA" → Ya fue clasificado
- "Aprobado por Humano" → HITL aprobó
- "Contactado" → Email ya enviado
- "Rechazado" → HITL rechazó
- "Error" → Algo falló

---

### Implementación 3: Trigger "From Now On"

**Gmail Trigger Configuración**:
```
Tipo: gmailTrigger
Opción: "From now on" (NO "from start of connection")
```

**Efecto**:
- 🔒 Solo procesa emails DESPUÉS de activar workflow
- 🔒 Ignora histórico completamente
- 🔒 Previene reprocessing de 1000+ emails viejos

---

### Implementación 4: Búsqueda de Duplicados

**Nodo 04 - Buscar en Airtable**:
```javascript
WHERE Email = "{{lead_email}}"
```

**Resultado**:
- Si existe: Usar ID para UPDATE
- Si no existe: CREATE nuevo

**Efecto**:
- 🔒 Múltiples leads del mismo email → Same record updated
- 🔒 Score puede mejorar en iteraciones
- 🔒 Impide duplicados en BD

---

### Comprobación de Bucle Infinito

**Test de Estrés T01**:
```
Lead: Juan García <juan@fintech.io>
Ejecución 1: Procesa, registra en Airtable
Ejecución 2: Misma búsqueda 30 min después
Resultado: ✅ Airtable muestra 1 record (no duplica)
           ✅ Score no se duplica, se actualiza si cambia
```

**Conclusión**: ✅ Sistema resistente a bucles

---

## 2. Validación Correcta de Tipos de Datos

### Regla: Comparar tipo con tipo (nunca mezclar)

#### IF Node 03 - Validar Datos

**Comparación 1: String con Regex**
```javascript
Condición: $json.lead_email REGEX ^[^\s@]+@[^\s@]+\.[^\s@]+$
Tipo: STRING
Efecto: Valida formato email
```

**Comparación 2: Number con Number**
```javascript
Condición: $json.mensaje.length > 10
Comparación: NUMBER > NUMBER
Correcto: ✅ String.length es number
```

---

#### IF Node 07 - Score >= 70

**CORRECTO**:
```javascript
Condición: $json.ia_response_json.score_0_100 >= 70
Tipos: score_0_100 = NUMBER
Operador: >= (comparación numérica)
Resultado: 88 >= 70 → TRUE
           41 >= 70 → FALSE
```

**INCORRECTO (lo que NO hacemos)**:
```javascript
// ❌ Comparar string con número:
"88" >= 70  → FALSE (string > number es falso)

// ❌ Usar > en strings:
"88" > "70" → FALSE (string comparison: "8" < "7" ASCII)

// ❌ Sin conversión:
parseInt("88") vs Number 70 → ✅ es correcto si convierte
```

---

#### IF Node 11 - Aprobado por Humano

**CORRECTO**:
```javascript
Condición: $json.decision === "approved"
Tipos: STRING === STRING
Valores esperados: "approved" o "rejected"
Resultado: "approved" === "approved" → TRUE
```

**INCORRECTO**:
```javascript
// ❌ String vs undefined:
undefined === "approved" → FALSE

// ❌ Typo:
"approved" === "Approved" → FALSE (case sensitive)
```

---

### Validación de Arrays

**Seguro**:
```javascript
// IF: datos_faltantes tiene elementos
$json.datos_faltantes && $json.datos_faltantes.length > 0

// Obtener primer elemento:
$json.datos_faltantes[0]  // "email"
```

**Inseguro**:
```javascript
// ❌ Sin check:
$json.datos_faltantes[0]  // Puede ser undefined si array vacío
```

---

### Comparación en Airtable Update

**Tipo correcto en Nodo 08**:
```javascript
"Score IA": "={{$json.ia_response_json.score_0_100}}"  // Number (sin comillas de más)
"Categoría": "={{$json.ia_response_json.categoria}}"   // String
```

---

## 3. Prompts Dinámicos (Sin Hardcoding)

### Variables Dinámicas en User Template (Nodo 05)

**CORRECTO - Todas variables**:
```javascript
"Lead: {{$node['02 Normalizar'].json.lead_nombre}} <{{$node['02 Normalizar'].json.lead_email}}>
Empresa: {{$node['04 Buscar'].json.records[0].fields.Empresa || 'No especificada'}}
Asunto: {{$node['02 Normalizar'].json.asunto}}
Mensaje: {{$node['02 Normalizar'].json.mensaje}}
Historial Cliente: {{$node['04 Buscar'].json.records[0].fields.Historial || 'Primer contacto'}}"
```

**INCORRECTO - Datos fijos**:
```javascript
// ❌ Hardcodeado:
"Lead: Juan García <juan@empresa.com>"  // ← Mismo para todos

// ❌ Mixto:
"Lead: {{nombre}} de empresa MyCompany"  // MyCompany hardcodeada

// ❌ CRÍTICO - API KEY:
"API: sk-1234567890abcdef"  // ← NUNCA en prompt
```

---

### Validación de Variables en Prompt

**Check**:
- ☑️ `lead_nombre` viene de Gmail, no de texto fijo
- ☑️ `lead_email` viene de Gmail, no inventado
- ☑️ `empresa` viene de Airtable (búsqueda previa)
- ☑️ `asunto` viene de Gmail
- ☑️ `mensaje` viene de Gmail
- ☑️ Fallbacks con `|| 'valor default'`

---

## 4. Protección de Credenciales

### Ubicación Correcta

#### Credenciales en n8n Credentials (Protegidas)

```
Admin → Credentials → Crear nueva

Gmail OAuth2
  - Tipo: Gmail
  - Generar OAuth token
  - Permisos: send emails, read emails

Airtable API Token
  - Generar token en airtable.com/account
  - Restringe a base específica
  - Solo lectura/escritura necesaria

OpenAI API Key
  - Generar en https://platform.openai.com/keys
  - Limitar a organización
  - Limitar a modelos específicos
```

#### Variables en n8n Variables (Protegidas)

```
Admin → Variables → Crear

AIRTABLE_BASE_ID = "appXXXXXXXXXXXXXX"
APPROVER_EMAIL = "approver@empresa.com"
SLACK_WEBHOOK = "https://hooks.slack.com/services/XXX/YYY/ZZZ"
```

---

#### JSON Exportado (SIN Credenciales)

**leadpilot_ai_n8n_workflow.json** tiene:

```javascript
// ✅ Referencias a credenciales (seguras):
"credentials": {
  "gmailOAuth2": "Gmail_Account"  // ← Solo nombre, no secret
}

// ✅ Variables como strings (seguras):
"base": {"mode": "id", "value": "{{$env.AIRTABLE_BASE_ID}}"}
"url": "{{$env.SLACK_WEBHOOK}}"

// ❌ NUNCA incluye:
"apiKey": "sk-123..."     // ← NO
"credentials": {...}      // ← NO
"tokens": {...}          // ← NO
```

---

### Check de Seguridad

**Antes de subir a GitHub**:

```bash
# No buscar patrones de API keys:
grep -r "sk-" leadpilot-ai-automation/         # ❌ OpenAI key
grep -r "Bearer " leadpilot-ai-automation/     # ❌ Token
grep -r "app" leadpilot-ai-automation/         # ⚠️ Airtable base ID

# No hardcodear emails:
grep -r "@empresa.com" leadpilot-ai-automation/  # ⚠️ Email hardcodeado

# Verificar .gitignore:
cat .gitignore | grep -E "env|key|secret|credentials"
```

---

## 5. Error Handling Robusto

### Error Route 1: Datos Faltantes

**Trigger**: Nodo 03 IF falla (email inválido o mensaje < 10 chars)

**Flujo**:
```
[03 IF FALSE]
  ↓
[16a Capturar error]
  ↓
[16b Registrar en tabla Errores]
  ↓
[FIN - No procesa con IA]
```

**Ventajas**:
- 🔒 NO envía datos malformados a OpenAI (ahorra tokens)
- 🔒 NO contacta al cliente
- 🔒 Registra para revisión manual posterior

**Test T02**: ✅ Datos faltantes detectados

---

### Error Route 2: Fallo API OpenAI

**Trigger**: Nodo 05 OpenAI falla (timeout, credencial, rate limit)

**Configuración**:
```javascript
Nodo 05: {
  "continueOnFail": true,  // ← Sigue si falla
  "onError": "continueRegardless"
}

// Error handler:
Conexión: [05 ERROR] → [17 Registrar en Errores]
```

**Ventajas**:
- 🔒 Workflow NO se detiene
- 🔒 Email NOT enviado (cliente no recibe respuesta incompleta)
- 🔒 Error loggueado con stack trace para debugging
- 🔒 Sistema disponible para próximos leads

**Test T06**: ✅ Error API capturado

---

### Registro de Errores

**Tabla Errores - Campos**:

```
Error ID        → Autonumber único
Origen          → Nodo que falló (ej: "05 OpenAI")
Tipo Error      → Categoría (ej: "API OpenAI")
Detalle         → Mensaje de error técnico
Lead Email      → Email del lead afectado
Estado          → "Pendiente corrección" / "Reintentado" / "Cerrado"
Gravedad        → "Crítica" / "Alta" / "Media"
Timestamp       → Fecha/hora del error
Stack Trace     → JSON completo para debugging
```

**Análisis**:
```
SELECT * FROM Errores WHERE Estado = "Pendiente corrección"
→ Muestra errores sin resolver
→ Permite batch retry
→ Identifica patrones de fallo
```

---

## 6. Seguridad de HITL (Human-in-the-Loop)

### Prevención de "Efecto Metralleta"

**Escenario peligroso**:
```
❌ INCORRECTO:
  Lead score >= 70 → ENVIAR EMAIL AUTOMÁTICO
  (Sin aprobación humana)
  
  Riesgo: Lead spam, respuesta no auditada, responsabilidad legal
```

**Implementación correcta**:
```
✅ CORRECTO:
  Lead score >= 70 → Notificar Slack con resumen
                  ↓
               Humano revisa
                  ↓
            Aprueba ✅ / Rechaza ❌
                  ↓
           SI APRUEBA → Enviar email
           SI RECHAZA → NO enviar, registrar rechazo
```

---

### Validaciones de Aprobación

**Nodo 10 - Wait for Webhook**:
```
Espera respuesta con estructura:
{
  "decision": "approved" | "rejected"
}
```

**Nodo 11 - IF Aprobado**:
```javascript
Condición: $json.decision === "approved"

TRUE:  → Nodo 12 (Enviar Email)
FALSE: → Nodo 15 (Registrar rechazo, NO contactar)
```

**Test T04 & T05**: ✅ HITL funcionando correctamente

---

## 7. Auditoría y Trazabilidad

### Registro Completo en Airtable

**Tabla Leads - Estados**:
```
Cronología del lead:
1. Creación: "Pendiente IA"
2. Procesamiento: "Procesado por IA" (con Score, Categoría, Respuesta)
3. Decisión Humana: 
   - "Aprobado por Humano" (si HITL aprueba)
   - "Rechazado" (si HITL rechaza)
   - "Pendiente" (si score < 70, sin HITL)
4. Cierre: "Contactado" (si email enviado)

Cada estado es auditado:
  - Timestamp automático
  - Responsable (histórico de cambios)
  - Detalles de decisión
```

---

### Campos de Auditoría

**Tabla Leads**:
```
Fecha Creación     → timestamp automático
Fecha Actualización → timestamp automático
Estado             → Cambios trazados
Decision Humana    → Quién aprobó/rechazó
Score IA           → Score asignado
Respuesta Sugerida → Qué se envió
Thread ID          → Hilo Gmail para contexto
```

**Tabla Errores**:
```
Timestamp       → Cuándo ocurrió el error
Origen          → Qué nodo falló
Detalle         → Por qué falló
Stack Trace     → Evidencia técnica
Estado          → Resuelto o pendiente
```

---

## 8. Test de Seguridad

### Test 1: Bucle Infinito (T01 + T01 bis)

```
Objetivo: Verificar que no duplica

1. Ejecutar workflow con lead "juan@fintech.io"
   → Airtable: 1 record creado
   
2. Ejecutar nuevamente 30 min después
   → Búsqueda encuentra record anterior
   → UPDATE del score (no CREATE nuevo)
   → Airtable: 1 record (no 2)

Resultado: ✅ PASS
```

---

### Test 2: Validación de Tipos (T03)

```
Objetivo: Verificar comparación correcta

1. Lead con score_0_100 = 41 (NUMBER)
2. IF $json.ia_response_json.score_0_100 >= 70
3. Esperado: FALSE (41 < 70)
4. Acción: NO activa HITL

Resultado: ✅ PASS
```

---

### Test 3: Error Handling (T02, T06)

```
T02 - Datos faltantes:
1. Email vacío en input
2. IF validación falla
3. Registra en tabla Errores
4. NO procesa con IA
Resultado: ✅ PASS

T06 - Fallo OpenAI:
1. Simular error API
2. continueOnFail = true
3. Registra stack trace
4. Workflow sigue activo
Resultado: ✅ PASS
```

---

### Test 4: HITL Seguridad (T04, T05)

```
T04 - Aprobado:
1. Score >= 70 activa Slack
2. Humano click "Aprobar"
3. Email enviado
Resultado: ✅ PASS

T05 - Rechazado:
1. Score >= 70 activa Slack
2. Humano click "Rechazar"
3. NO envía email
4. Registra rechazo
Resultado: ✅ PASS
```

---

## 9. Checklist de Seguridad Pre-Producción

- ☑️ Filtro Gmail `newer_than:1d` previene histórico
- ☑️ Estado tracking en Airtable
- ☑️ Búsqueda de duplicados por email
- ☑️ IF Score valida NUMBER >= NUMBER (no string)
- ☑️ IF Aprobado valida STRING === STRING
- ☑️ Prompt OpenAI dinámico (variables de Gmail/Airtable)
- ☑️ NO API keys en JSON (en n8n Credentials)
- ☑️ Variables globales en n8n Variables
- ☑️ Error Route 1: Datos faltantes → Registra en Errores
- ☑️ Error Route 2: API falla → continueOnFail + Log
- ☑️ HITL obligatorio (score >= 70 requiere aprobación)
- ☑️ Email solo si humano aprueba
- ☑️ Rechazo humano registrado (no contacta)
- ☑️ Airtable threading en Slack (agrupa por lead)
- ☑️ .gitignore excluye .env, *.key, *credentials*
- ☑️ Video demo oculta API keys
- ☑️ 6 pruebas de estrés pasan
- ☑️ Test de "camino infeliz" incluido

---

## Conclusión

**LeadPilot AI implementa un sistema seguro, resiliente y listo para producción.**

Todos los requisitos de seguridad están cumplidos:
- ✅ Anti-bucles
- ✅ Validación de tipos correcta
- ✅ Sin hardcoding (prompts dinámicos)
- ✅ Credenciales protegidas
- ✅ Error handling robusto
- ✅ HITL previene contactos incorrectos
- ✅ Auditoría completa
- ✅ 6/6 pruebas de seguridad pasan

**Status**: 🟢 SEGURO PARA DEPLOY

---

**Última actualización**: 15 de Julio, 2026
