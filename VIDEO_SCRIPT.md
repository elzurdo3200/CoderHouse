# Script de Video Demo - LeadPilot AI (3 minutos)

## Duración Total: 180 segundos

---

## SECCIÓN 1: Introducción (0:00 - 0:20)

**Narración:**
"Bienvenidos a LeadPilot AI, un ecosistema de automatización completamente autónomo que gestiona leads B2B desde Gmail hasta la respuesta final del cliente.

Este sistema integra cinco tecnologías: n8n como orquestador, Airtable como base de datos, OpenAI para procesamiento inteligente, Gmail para entrada y salida, y Slack para validación humana.

Todo sin intervención manual. Todo con seguridad garantizada."

**Visual:**
- Mostrar pantalla de inicio del proyecto
- Logo/título de LeadPilot AI
- Tecnologías en pantalla (n8n, Airtable, OpenAI, Gmail, Slack)

**Duración: 20 segundos**

---

## SECCIÓN 2: Arquitectura del Sistema (0:20 - 0:50)

**Narración:**
"El flujo es simple pero poderoso. Un email llega a Gmail. n8n lo captura automáticamente con filtros inteligentes que evitan bucles infinitos.

El sistema extrae variables dinámicas: email, nombre, asunto y mensaje. Todo sin datos hardcodeados.

Luego valida que los datos sean completos. Si faltan datos, registra el error. Si están completos, continúa."

**Visual:**
- Mostrar diagrama de arquitectura
- Gmail → n8n → Validación (con flechas)
- Resaltar filtro 'newer_than:1d'
- Mostrar captura de n8n con nodos

**Duración: 30 segundos**

---

## SECCIÓN 3: Procesamiento IA (0:50 - 1:30)

**Narración:**
"El siguiente paso es el corazón del sistema: OpenAI GPT.

Enviamos el email a OpenAI con un prompt estructurado que clasifica el lead. El sistema genera un JSON con:
- Categoría (VIP, Potencial, Baja Prioridad)
- Score de 0 a 100
- Prioridad del contacto
- Datos faltantes que detectó
- Respuesta sugerida al cliente

Todo esto se registra automáticamente en Airtable, nuestra base de datos central.

Airtable tiene tres tablas relacionadas: Leads, Clientes y Errores. Esto permite deduplicación y auditabilidad total.

Si el score es menor a 70, el sistema se detiene. No contacta al cliente sin aprobación.

Si el score es 70 o mayor, se activa la validación humana."

**Visual:**
- Mostrar prompt OpenAI en pantalla
- JSON de respuesta de OpenAI
- Mostrar tablas de Airtable (Leads, Clientes, Errores)
- Relaciones entre tablas
- Estados: Pendiente IA, Procesado, Aprobado, Contactado
- Gráfico de flujo condicional (IF Score >= 70)

**Duración: 40 segundos**

---

## SECCIÓN 4: Human-in-the-Loop (1:30 - 2:15)

**Narración:**
"Aquí está lo importante: validación humana obligatoria.

Cuando el score es alto, el sistema envía una notificación a Slack con un resumen completo del lead y la respuesta sugerida.

Un aprobador humano revisa la información y decide: aprobar o rechazar.

Si aprueba, el sistema envía el email al cliente manteniendo el hilo original de Gmail. El cliente no sabe que pasó por validación automática.

Si rechaza, el sistema registra el rechazo. No contacta al cliente. Evita el 'efecto metralleta'.

Todo queda auditado. Todos los pasos, todas las decisiones, todos los cambios de estado."

**Visual:**
- Mostrar notificación de Slack
- Botones: Aprobar / Rechazar
- Email final siendo enviado en Gmail
- Thread ID manteniéndose en Gmail
- Tabla de Airtable mostrando cambios de estado

**Duración: 45 segundos**

---

## SECCIÓN 5: Manejo de Errores (2:15 - 2:50)

**Narración:**
"El sistema es robusto. Tiene dos rutas de error principales.

Ruta 1: Si faltan datos (email vacío, mensaje incompleto), registra en la tabla Errores y NO procesa con IA. Ahorra tokens y evita clasificaciones incorrectas.

Ruta 2: Si OpenAI falla (timeout, credencial expirada), el sistema usa 'continueOnFail'. Registra el error, notifica al aprobador, pero no bloquea el flujo. El sistema sigue activo para otros leads.

Hemos ejecutado 6 pruebas de estrés:
- T01: Lead completo, score 88. Resultado: Email enviado ✓
- T02: Datos faltantes. Resultado: Registrado en Errores ✓
- T03: Score bajo 41. Resultado: No contacta ✓
- T04: HITL aprobado, score 94. Resultado: Email en Thread ID ✓
- T05: HITL rechazado, score 73. Resultado: No contacta ✓
- T06: API OpenAI falla. Resultado: Registrado sin bloquear ✓

100% de las pruebas pasaron."

**Visual:**
- Mostrar tabla de tests
- Casos T01-T06 con resultados
- Ruta de error en rojo en diagrama n8n
- Tabla Errores en Airtable
- Checkmarks verdes en cada prueba

**Duración: 35 segundos**

---

## SECCIÓN 6: Cierre (2:50 - 3:00)

**Narración:**
"LeadPilot AI demuestra un ecosistema de automatización completo:
- Captura autónoma desde Gmail
- Procesamiento inteligente con OpenAI
- Validación humana obligatoria
- Manejo robusto de errores
- Auditoría total en Airtable

Todo integrado. Todo profesional. Todo listo para producción.

Gracias por ver."

**Visual:**
- Mostrar logo de LeadPilot AI
- Logos de tecnologías (n8n, Airtable, OpenAI, Gmail, Slack)
- Resumen visual del flujo completo
- Checklist de requisitos cumplidos (verde)

**Duración: 10 segundos**

---

## DISTRIBUCIÓN DE TIEMPO

- Introducción: 20 seg (11%)
- Arquitectura: 30 seg (17%)
- IA y Airtable: 40 seg (22%)
- HITL: 45 seg (25%)
- Errores y Pruebas: 35 seg (19%)
- Cierre: 10 seg (6%)

**Total: 180 segundos (3 minutos exactos)**

---

## NOTAS TÉCNICAS PARA LA GRABACIÓN

**Resolución:** 1920x1080 (Full HD)
**FPS:** 30 fps
**Codec:** H.264
**Audio:** Narración clara, sin música de fondo (opcional música suave al inicio/fin)

**Pantallas a capturar:**
1. Diagrama de arquitectura (PNG generado)
2. Flujo n8n con nodos (PNG generado)
3. Airtable (Tablas Leads, Clientes, Errores)
4. OpenAI prompt (screenshot)
5. Notificación Slack (screenshot)
6. Gmail con Thread ID (screenshot)
7. Tabla de pruebas de estrés (PNG generado)
8. Documentación del proyecto

**Transiciones:** Suave cross-fade entre secciones
**Texto en pantalla:** Resaltar puntos clave con animaciones

