# Scripts de Validación - LeadPilot AI

## validate_project.py

Script completo de validación del proyecto LeadPilot AI.

### Descripción

Valida la estructura, integridad y completitud del proyecto:
- Directorios y archivos requeridos
- Workflow n8n JSON
- Schema Airtable
- Prompts OpenAI
- .gitignore configuración
- Documentación
- Archivos de evidencia

### Uso

```bash
# Ejecutar validación desde la raíz del proyecto
python3 scripts/validate_project.py

# Ejecutar desde otra ubicación especificando ruta
python3 scripts/validate_project.py /ruta/a/proyecto
```

### Output

El script genera un reporte con:
- ✅ Validación exitosa o ❌ fallida
- 📊 Estadísticas del workflow n8n
- 📊 Estadísticas de Airtable
- ❌ Errores encontrados (si existen)
- ⚠️ Advertencias (si existen)

### Requisitos

- Python 3.6+
- Acceso de lectura a los archivos del proyecto

### Ejemplos de Output

```
🔧 WORKFLOW n8n:
   • Nodos totales: 19
   • Triggers: 2
   • Nodos IA: 1
   • Nodos HITL: 0
   • Conexiones: 14
   • Componentes encontrados: 9/9

📊 AIRTABLE:
   • Tablas: 3
   • Campos totales: 35
   • Relaciones: 0

✅ VALIDACIÓN EXITOSA
```

### Qué se Valida

**Estructura de Directorios:**
- database/ (con airtable_schema.json y .csv)
- prompts/ (con OpenAI prompts)
- tests/ (con test_stress_log.txt)
- docs/ (con documentación técnica)
- evidencias/ (con capturas y video demo)

**Archivos Raíz:**
- README.md
- CHECKLIST_ENTREGA.md
- leadpilot_ai_n8n_workflow.json
- .gitignore
- .env.example

**Workflow n8n:**
- Al menos 11 nodos
- Triggers (Gmail)
- Nodo OpenAI
- Componentes clave (Validación, Airtable, HITL, Error Handling)
- Conexiones entre nodos

**Airtable:**
- 3 tablas: Leads, Clientes, Errores
- Campos suficientes
- Relaciones configuradas

**Prompts:**
- System prompt estructurado
- User template con variables dinámicas

**Evidencias:**
- 4 imágenes PNG
- 1 video MP4 (demo de 3 minutos)
- Tamaños mínimos verificados

### Códigos de Salida

- `0`: Validación exitosa
- `1`: Validación fallida (errores encontrados)

