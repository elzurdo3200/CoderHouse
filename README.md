# LeadPilot AI - Ecosistema de Automatización IA Autónomo

**Trabajo Práctico Final: Integración Completa de Stack IA + Automatización**

## 🎯 Caso de Uso

**LeadPilot AI** automatiza la gestión integral de leads B2B recibidos vía Gmail. El sistema implementa un flujo end-to-end que:

1. **Captura** leads desde Gmail (trigger inteligente con filtros)
2. **Registra** la información en Airtable como fuente única de verdad
3. **Procesa** con OpenAI GPT utilizando prompts estructurados para clasificación y análisis
4. **Valida** mediante Human-in-the-Loop en Slack (aprobación antes de contactar)
5. **Responde** al cliente manteniendo el hilo de Gmail (Thread ID)
6. **Resiste** fallos con 2+ nodos de Error Handling y rutas de recuperación

---

## 🛠️ Tecnologías Integradas (5 de 4 requeridas)

| Tecnología | Rol | Detalles |
|---|---|---|
| **n8n** | Orquestador Principal | Flujo con 15+ nodos, ejecutables, sin UI visual |
| **Airtable** | Base de Datos + Memoria | 3 tablas: Leads, Clientes, Errores con relaciones |
| **OpenAI GPT** | Motor IA | Prompt estructurado, salida JSON, max_tokens optimizado |
| **Gmail** | Canal Entrada + Salida | Trigger + Response, mantiene Thread ID |
| **Slack** | Human-in-the-Loop | Notificaciones y aprobación antes de acción crítica |

---

## 📁 Estructura del Repositorio

```
leadpilot-ai-automation/
├── README.md                                      # Este archivo
├── CHECKLIST_ENTREGA.md                          # Verificación punto-a-punto
├── .gitignore                                     # Excluir .env, API keys
│
├── LeadPilot_AI_Diagrama_Arquitectura.pdf         # Diagrama técnico (requerido)
│
├── leadpilot_ai_n8n_workflow.json                 # Workflow importable en n8n
│
├── database/
│   ├── airtable_schema.json                       # Esquema técnico (4 tablas)
│   ├── airtable_schema.csv                        # Formato tabular para referencia
│   └── airtable_relationships.md                  # Documentación de relaciones
│
├── prompts/
│   ├── openai_system_prompt.md                    # System prompt estructura
│   ├── openai_user_template.md                    # Template dinámico con variables
│   └── prompt_best_practices.md                   # Notas de optimización
│
├── scripts/
│   ├── validate_n8n_workflow.py                   # Validar JSON antes de importar
│   └── generate_test_data.py                      # Script para pruebas de estrés
│
├── tests/
│   ├── test_stress_log.txt                        # Resultado 6 pruebas documentadas
│   ├── test_cases.md                              # Casos de prueba detallados
│   └── error_scenarios.md                         # Escenarios de "camino infeliz"
│
├── evidencias/
│   ├── 01_diagrama_arquitectura.png               # Screenshot del diagrama
│   ├── 02_flujo_n8n_evidencia.png                 # Flujo en n8n canvas
│   ├── 03_airtable_schema_evidencia.png           # Tablas y relaciones
│   ├── 04_slack_hitl_evidencia.png                # HITL funcionando
│   ├── 05_error_handling_evidencia.png            # Error routes activas
│   └── demo_leadpilot_ai.mp4                      # Video demo 3 min (opcional)
│
├── docs/
│   ├── ARQUITECTURA.md                            # Explicación técnica detallada
│   ├── VARIABLES_DINAMICAS.md                     # Mapeo de todas las variables
│   ├── SEGURIDAD.md                               # Check de seguridad
│   └── TROUBLESHOOTING.md                         # Guía de debugging
│
└── .env.example                                   # Template para variables (NO subir .env)
```

---

## 🚀 Cómo Usar Este Proyecto

### Requisitos Previos
- Cuenta n8n (Cloud o Self-hosted)
- Cuenta Airtable con API token
- Cuenta OpenAI con API key
- Cuenta Gmail con OAuth2 configurado
- Cuenta Slack con Webhooks (opcional para pruebas)

### Instalación Rápida

#### 1. **Preparar Base de Datos (Airtable)**
```bash
1. Crear nueva base en Airtable
2. Importar esquema desde: database/airtable_schema.json
3. Crear las 3 tablas: Leads, Clientes, Errores
4. Copiar BASE_ID desde URL: https://airtable.com/[BASE_ID]/...
```

#### 2. **Configurar Credenciales en n8n**
```
Gmail OAuth2        → Conectar cuenta Gmail
Airtable API Token  → Generar y vincular
OpenAI API Key      → Pegar clave de https://platform.openai.com/keys
Slack Webhook       → (Opcional) Generar desde workspace Slack
```

#### 3. **Importar Workflow**
```
n8n → Import from File → leadpilot_ai_n8n_workflow.json
```

#### 4. **Configurar Variables n8n**
```
Ir a: Admin → Variables
Crear:
  AIRTABLE_BASE_ID = "appXXXXX"
  APPROVER_EMAIL = "tu-email@empresa.com"
  SLACK_WEBHOOK = "https://hooks.slack.com/..." (si usas Slack)
```

#### 5. **Activar el Workflow**
```
Click en "Active" → El workflow comienza a escuchar emails
```

---

## 🏗️ Arquitectura Técnica

### Flujo Principal (Happy Path)

```
Gmail Email
    ↓
[01 Trigger Gmail]  ← Filtro: "Lead OR Consulta" + last 1 day
    ↓
[02 Normalizar Variables]  ← Extraer: email, nombre, asunto, mensaje
    ↓
[03 Validar Datos] ← IF: email y mensaje existen?
    ├─ NO → [Error Handling - Datos Faltantes]
    └─ SÍ ↓
[04 Buscar en Airtable]  ← ¿Lead duplicado?
    ├─ Sí → [Actualizar registro]
    └─ No → [Crear nuevo]
    ↓
[05 OpenAI - Clasificar Lead]  ← Prompt dinámico
    ├─ Error → [Error Handling - API IA]
    └─ OK ↓
[06 Registrar Resultado IA]  ← Guardar score, categoría, respuesta
    ↓
[07 IF Score >= 70?]  ← Filtro de prioridad
    ├─ Score < 70 → [Terminar]
    └─ Score >= 70 ↓
[08 Enviar a Slack - HITL]  ← Notificar aprobador
    ↓
[09 Wait for Webhook]  ← Esperar decisión humana (aprobado/rechazado)
    ├─ Rechazado → [Registrar rechazo, NO contactar]
    └─ Aprobado ↓
[10 Registrar Aprobación]
    ↓
[11 Enviar Email al Cliente]  ← Respuesta en Thread ID original
    ↓
[12 Actualizar Estado a Contactado]
```

### Rutas de Error (2 Error Handling Obligatorios)

**Error Route 1: Datos Faltantes**
- Detecta: email vacío, mensaje vacío, datos incompletos
- Acción: Registra en tabla Errores, NO procesa con IA
- Salida: Registra estado "Error" en Airtable

**Error Route 2: Fallo API OpenAI**
- Detecta: timeout, credenciales inválidas, límite de tokens
- Acción: continueOnFail en nodo OpenAI
- Salida: Log en tabla Errores con detalle técnico

---

## 🔐 Check de Seguridad

- ✅ **Anti-bucles infinitos**: Filtro Gmail con búsqueda acotada (`newer_than:1d`) + estado tracking
- ✅ **Tipos de datos correctos**: IF nodes comparan número vs número, string vs string
- ✅ **Prompts dinámicos**: Todas las variables vienen de Gmail/Airtable, NO hardcodeadas
- ✅ **Max Tokens**: OpenAI configurado a 500 tokens para optimizar costos
- ✅ **No API keys en JSON**: Credenciales en n8n Credentials, no exportadas
- ✅ **HITL obligatorio**: Aprobación Slack antes de contactar cliente
- ✅ **Thread ID**: Se mantiene en Airtable y se usa en respuesta

---

## 📊 Pruebas de Estrés

Se ejecutaron **6 pruebas** documentadas en `tests/test_stress_log.txt`:

| Prueba | Escenario | Resultado | Evidencia |
|---|---|---|---|
| T01 | Lead completo, score alto (88) | ✅ OK | Email enviado |
| T02 | Sin email válido | ✅ OK | Error registrado |
| T03 | Datos ambiguos, score bajo (41) | ✅ OK | No contactar |
| T04 | HITL aprobado (score 94) | ✅ OK | Email en hilo original |
| T05 | HITL rechazado | ✅ OK | Rechazo registrado |
| T06 | Fallo API OpenAI | ✅ OK | Error Handling capturó |

---

## 🔗 Enlaces Obligatorios

### Base de Datos (Airtable - Vista Lectura)
[Acceso a Airtable LeadPilot](https://airtable.com/appRAWorY6yPb4QJn/tblEx4UKF4j0bkVvr/viwd1TlkGIsdGkjva)

### Workflow n8n (Lectura)
[Ver workflow en n8n Cloud](https://delroy2026.app.n8n.cloud/workflow/qSfCEYFOYzLFvlGc?projectId=KJrQfW9cIoac0mkH)

### Repositorio GitHub
[GitHub: leadpilot-ai-automation](https://github.com/ocapizza/leadpilot-ai-automation)

---

## 📋 Entregables Incluidos

- ✅ Diagrama arquitectura PDF
- ✅ Workflow JSON importable
- ✅ Esquema Airtable (JSON + CSV)
- ✅ Prompts estruturados
- ✅ 6 Pruebas documentadas
- ✅ 5+ Evidencias (screenshots)
- ✅ Video demo (3 min)
- ✅ Documentación técnica completa
- ✅ Checklist de cumplimiento

---

## 🎓 Conceptos Clave Implementados

| Concepto | Implementación |
|---|---|
| **Trigger Inteligente** | Gmail con filtros por asunto y fecha |
| **Normalización de datos** | Set node extrae variables dinámicamente |
| **Validación** | IF nodes con type checking |
| **IA Estructurada** | OpenAI con prompt + JSON schema |
| **Resiliencia** | continueOnFail + Error Handling routes |
| **HITL (Human-in-the-Loop)** | Slack notification + Wait for Webhook |
| **Idempotencia** | Búsqueda de duplicados en Airtable |
| **Auditabilidad** | Todos los pasos registrados en DB |
| **Multicanal** | Gmail + Slack + Airtable |

---

## 📞 Soporte y Debugging

Ver archivos en `docs/`:
- **ARQUITECTURA.md**: Explicación nodo por nodo
- **VARIABLES_DINAMICAS.md**: Mapeo completo
- **SEGURIDAD.md**: Validaciones implementadas
- **TROUBLESHOOTING.md**: Problemas comunes y soluciones

---

## 📝 Licencia

Trabajo académico para AI Automation Course - 2026

---

**Última actualización**: 15 de Julio, 2026
**Estado**: ✅ Completado y testeado
**Autor**: Tu Nombre  
**Versión**: 1.0
