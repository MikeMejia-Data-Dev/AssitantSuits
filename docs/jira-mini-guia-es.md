# Mini Guía Jira LexIA

Esta guía traduce el backlog actual de `docs/jira-import.csv` a una vista operativa en español para producto, desarrollo y QA.

## Objetivo

Organizar el MVP de `LexIA` en:

- Épicas
- Historias de usuario
- Tareas técnicas
- Dependencias
- Tecnología sugerida
- Orden recomendado de implementación

## Stack Base del Proyecto

- Frontend: `Flutter Web`
- Gestión de estado: `Riverpod`
- Backend API: `FastAPI`
- Worker IA: `Python`
- Base de datos: `PostgreSQL`
- Búsqueda semántica: `pgvector`
- Cola / estados asíncronos: `Redis`
- Archivos: `S3-compatible object storage`
- Infra local: `Docker Compose`

## Regla General de Dependencias

El orden correcto del MVP es:

1. Seguridad y usuarios
2. Expedientes
3. Documentos y OCR
4. Indexación y RAG
5. Análisis y chat
6. Redacción y exportación
7. Historial y QA final

Si ese orden se rompe, el equipo termina implementando interfaces o flujos que aún no tienen base funcional.

## E1. Autenticación, Roles y Acceso por Firma

### Propósito

Permitir que solo usuarios válidos entren al sistema y que cada uno vea únicamente lo que le corresponde por rol, firma y permisos.

### Historias de usuario

#### `S1` Autenticación e aislamiento del workspace

Como usuario quiero iniciar sesión de forma segura para acceder solo a mi espacio autorizado.

Tareas:

- `T1` Implementar API de autenticación y JWT
- `T2` Construir shell de autenticación y route guards en frontend

Tecnología:

- Backend: `FastAPI`, `JWT`, hashing de contraseñas
- Frontend: `Flutter Web`, guards de ruta, persistencia de sesión

Dependencias:

- `T2` depende de `T1`

Cómo hacerlo:

1. Definir contratos de login, refresh y registro.
2. Generar tokens con `role_id`, `user_id`, `firm_id`.
3. Validar `status=true` antes de permitir acceso.
4. Proteger todas las rutas privadas en frontend.

#### `S15` Recuperación y reseteo de contraseña

Como usuario quiero recuperar mi contraseña sin comprometer la seguridad de la plataforma.

Tareas:

- `T31` Implementar recuperación y reset de contraseña
- `T32` Alinear esquemas de auth y usuarios con el contrato actual

Tecnología:

- Backend: `FastAPI`, tokens temporales, validaciones de expiración

Dependencias:

- `T31` depende de `T1`
- `T32` debe quedar alineada con `T1`

Cómo hacerlo:

1. Crear token de recuperación de un solo uso.
2. No revelar si el correo existe.
3. Invalidar el token después del uso.
4. Probar expiración, token inválido y cambio exitoso.

#### `S16` Administración de usuarios y pertenencia a firma

Como administrador quiero crear y gestionar usuarios de mi firma para controlar el acceso al sistema.

Tareas:

- `T3` Modelar usuarios, firmas y políticas de acceso
- `T34` Implementar persistencia de usuarios y firmas
- `T33` Implementar CRUD de usuarios
- `T35` Construir UI de administración de usuarios

Tecnología:

- Backend: `FastAPI`, `PostgreSQL`
- Frontend: `Flutter Web`
- Contratos: `packages/contracts`

Dependencias:

- `T3` depende de `T1`
- `T34` depende de `T3`
- `T33` depende de `T3`
- `T35` depende de `T33`

Cómo hacerlo:

1. Definir `role_id` numérico `1..3`.
2. Guardar `status` como booleano.
3. Restringir visibilidad por firma y rol.
4. Exponer solo campos públicos, nunca `password_hash`.

#### `S2` Compartir expediente dentro de la firma

Como administrador de firma quiero compartir expedientes con otros miembros para colaborar de forma controlada.

Tareas:

- `T4` Implementar API de compartición y auditoría

Tecnología:

- Backend: `FastAPI`, tablas de ACL y auditoría en `PostgreSQL`

Dependencias:

- `T4` depende de `T3`

Cómo hacerlo:

1. Crear tabla de permisos por expediente.
2. Permitir solo `read` o `read_write`.
3. Registrar quién compartió, a quién y cuándo.
4. Validar que un no-admin no pueda compartir.

## E2. Gestión de Expedientes e Historial

### Propósito

Crear el núcleo del producto: expedientes legales con estado, dueño, visibilidad y trazabilidad.

### Historias de usuario

#### `S3` Creación de expedientes

Como abogado quiero crear un expediente con los datos mínimos obligatorios para iniciar el trabajo del caso.

Tareas:

- `T5` Implementar API CRUD de expedientes
- `T6` Construir pantallas de lista, detalle y creación

Tecnología:

- Backend: `FastAPI`
- Frontend: `Flutter Web`
- DB: `PostgreSQL`

Dependencias:

- `T5` depende de `T1`
- `T6` depende de `T2` y `T5`

Cómo hacerlo:

1. Exigir nombre y área legal.
2. Asignar propietario automáticamente.
3. Iniciar con estado por defecto.
4. Filtrar expedientes por usuario/firma/permisos.

#### `S4` Ciclo de vida del expediente

Como usuario quiero mover un expediente entre estados válidos para reflejar su avance real.

Tareas:

- `T7` Implementar transiciones de estado
- `T8` Construir controles de estado en UI

Tecnología:

- Backend: reglas de dominio en `FastAPI`
- Frontend: acciones controladas y feedback visual en `Flutter`

Dependencias:

- `T7` depende de `T5`
- `T8` depende de `T6` y `T7`

Cómo hacerlo:

1. Definir estados permitidos.
2. Bloquear transiciones inválidas.
3. Mantener historial y timestamps.
4. Evitar que cerrar o archivar borre información.

## E3. Carga Documental y Base de Conocimiento

### Propósito

Convertir documentos legales sin estructura en conocimiento utilizable para análisis y chat.

### Historias de usuario

#### `S5` Carga y seguimiento de documentos

Como usuario quiero subir documentos al expediente y ver su estado de procesamiento.

Tareas:

- `T9` Implementar API de upload e integración con object storage
- `T11` Implementar versionado de documentos
- `T10` Construir UI de carga y estados

Tecnología:

- Backend: `FastAPI`, storage tipo `S3`
- Frontend: `Flutter Web`
- DB: `PostgreSQL`

Dependencias:

- `T9` depende de `T5`
- `T11` depende de `T9`
- `T10` depende de `T9`

Cómo hacerlo:

1. Aceptar `pdf`, `doc`, `docx`, `txt`.
2. Rechazar archivos grandes, inválidos o protegidos.
3. Guardar metadata y versión.
4. Mostrar estados: cargado, procesando, extraído, vectorizado, insuficiente.

#### `S6` OCR y calidad de extracción

Como usuario quiero que el sistema extraiga texto útil de los documentos escaneados y me avise si no tienen calidad suficiente.

Tareas:

- `T12` Implementar worker de OCR
- `T13` Implementar scoring de calidad
- `T14` Implementar chunking, embeddings e indexación con `pgvector`

Tecnología:

- Worker IA: `Python`
- Cola: `Redis`
- Vector store: `pgvector`

Dependencias:

- `T12` depende de `T9`
- `T13` depende de `T12`
- `T14` depende de `T12`

Cómo hacerlo:

1. Procesar OCR en segundo plano.
2. Marcar calidad insuficiente cuando el texto no sirva.
3. Partir el texto en fragmentos.
4. Generar embeddings por expediente sin mezclar casos.

## E4. Análisis Jurídico y Chat con RAG Verificado

### Propósito

Garantizar que la IA responda solo con citas verificables y evidencia real del expediente y del corpus legal.

### Historias de usuario

#### `S7` Análisis jurídico verificado

Como abogado quiero obtener un análisis jurídico estructurado y sustentado en normas y jurisprudencia verificadas.

Tareas:

- `T15` Ingestar corpus legal
- `T16` Implementar orquestación RAG y verificador de citas
- `T17` Implementar API de generación de análisis
- `T18` Construir UI de análisis

Tecnología:

- Worker IA: embeddings, retrieval, verificación
- Backend: `FastAPI`
- Frontend: `Flutter Web`
- DB: `PostgreSQL + pgvector`

Dependencias:

- `T15` depende de `T14`
- `T16` depende de `T14` y `T15`
- `T17` depende de `T16`
- `T18` depende de `T17`

Cómo hacerlo:

1. Cargar normas y sentencias con versionado.
2. Recuperar primero evidencia del expediente y luego corpus legal.
3. Rechazar respuestas sin soporte verificable.
4. Persistir secciones, citas, versión del corpus y disclaimer.

#### `S8` Reembolso por fallo técnico

Como negocio quiero devolver créditos si el análisis falla por un error técnico de la plataforma.

Tareas:

- `T19` Implementar ledger de créditos y reembolsos

Tecnología:

- Backend: `FastAPI`
- DB: `PostgreSQL`

Dependencias:

- `T19` depende de `T17`

Cómo hacerlo:

1. Registrar débito al iniciar análisis.
2. Clasificar si el fallo fue técnico o de negocio.
3. Reembolsar solo ante error técnico.
4. Auditar cada movimiento.

#### `S9` Chat jurídico verificado

Como usuario quiero hacer preguntas legales y recibir respuestas con citas verificadas.

Tareas:

- `T20` Implementar API y persistencia de chat
- `T21` Implementar generación de chat con citas verificadas
- `T22` Construir UI de chat legal

Tecnología:

- Backend: `FastAPI`
- Worker IA: retrieval y verificación
- Frontend: `Flutter Web`

Dependencias:

- `T20` depende de `T16`
- `T21` depende de `T16` y `T20`
- `T22` depende de `T20` y `T21`

Cómo hacerlo:

1. Crear conversación y mensajes persistentes.
2. Aplicar las mismas reglas de verificación del análisis.
3. Mostrar citas junto a la respuesta.
4. Bloquear respuestas no verificables.

#### `S10` Conversaciones ligadas al expediente

Como usuario quiero vincular una conversación a un expediente sin alterar automáticamente los datos del caso.

Tareas:

- `T23` Implementar reglas de vínculo conversación-expediente

Tecnología:

- Backend: `FastAPI`
- DB: `PostgreSQL`

Dependencias:

- `T23` depende de `T20`

Cómo hacerlo:

1. Permitir `case_id` opcional en la conversación.
2. No modificar estado ni hechos del expediente por actividad del chat.
3. Exponer ese vínculo para historial y trazabilidad.

## E5. Redacción y Exportación

### Propósito

Transformar análisis verificados en documentos legales editables y exportables.

### Historias de usuario

#### `S11` Borradores editables de tutela

Como abogado quiero generar una tutela editable para ajustarla antes de usarla formalmente.

Tareas:

- `T24` Implementar generación de tutela
- `T25` Construir editor de borradores

Tecnología:

- Worker IA para generación
- Frontend `Flutter Web` con editor enriquecido

Dependencias:

- `T24` depende de `T17`
- `T25` depende de `T24`

Cómo hacerlo:

1. Partir del análisis validado.
2. Generar secciones obligatorias.
3. Permitir edición humana antes de exportar.

#### `S12` Borradores editables de derecho de petición

Como abogado quiero generar un derecho de petición editable según el destinatario y el contexto legal.

Tareas:

- `T26` Implementar generación de derecho de petición

Tecnología:

- Worker IA

Dependencias:

- `T26` depende de `T17`

Cómo hacerlo:

1. Detectar régimen y destinatario.
2. Generar estructura mínima requerida.
3. Dejar contenido editable para revisión humana.

#### `S13` Exportación de análisis y borradores

Como usuario quiero exportar análisis y documentos en formatos formales para compartirlos o trabajarlos fuera de la plataforma.

Tareas:

- `T27` Implementar servicio de exportación

Tecnología:

- Backend: `FastAPI`
- Renderización a `PDF` y `DOCX`
- Storage privado tipo `S3`

Dependencias:

- `T27` depende de `T17` y `T25`

Cómo hacerlo:

1. Convertir contenido editable a `PDF/DOCX`.
2. Incluir metadata, fecha, fuentes y disclaimer.
3. Guardar exportados en storage privado.
4. Servirlos con acceso autenticado.

## E6. Historial, QA y Preparación de Release

### Propósito

Cerrar el MVP con trazabilidad completa, cobertura de pruebas y checklist de salida.

### Historias de usuario

#### `S14` Línea de tiempo completa del expediente

Como usuario quiero ver toda la evolución del expediente en orden cronológico.

Tareas:

- `T28` Implementar API agregadora de historial
- `T29` Construir UI de timeline

Tecnología:

- Backend: `FastAPI`
- Frontend: `Flutter Web`

Dependencias:

- `T28` depende de `T4`, `T23` y `T27`
- `T29` depende de `T28`

Cómo hacerlo:

1. Unificar eventos de documentos, análisis, chat, compartición y borradores.
2. Ordenar cronológicamente.
3. Mostrar actor, fecha, tipo y detalle.

#### `E6` QA final y release readiness

Como equipo quiero validar los flujos críticos antes de liberar el MVP.

Tareas:

- `T30` Crear suite de regresión y checklist de release

Tecnología:

- QA manual
- Tests API
- Pruebas end-to-end

Dependencias:

- `T30` depende de `T1`, `T4`, `T9`, `T12`, `T17`, `T20`, `T24`, `T27`, `T29`

Cómo hacerlo:

1. Cubrir auth, ACL, expedientes, documentos, análisis, chat, drafts y export.
2. Preparar data de prueba consistente.
3. Definir checklist de salida a piloto.

## Orden Recomendado para Jira

### Sprint 1

- `E1` completo
- `E2` completo
- `E3` completo

Resultado esperado:

- Usuarios autenticados
- Roles y firmas funcionando
- Expedientes operativos
- Documentos cargados, procesados e indexados

### Sprint 2

- `E4` completo
- `E5` completo
- `E6` completo

Resultado esperado:

- Análisis jurídico verificado
- Chat jurídico con citas
- Borradores editables
- Exportación formal
- Historial completo
- QA y checklist de release

## Dependencias Críticas

- No iniciar `E2` sin base de auth de `E1`.
- No iniciar análisis `T17` sin retrieval verificado `T16`.
- No iniciar chat verificado `T21` sin `T16`.
- No iniciar drafts `T24` y `T26` sin análisis `T17`.
- No iniciar exportación `T27` sin generación y edición base.
- No cerrar QA `T30` hasta tener el flujo end-to-end armado.

## Recomendación de Uso en Jira

Conviene mantener tres niveles:

- Épica: capacidad de negocio grande
- Historia: necesidad del usuario
- Tarea: trabajo técnico implementable

Campos mínimos útiles en Jira:

- `Epic`
- `Story`
- `Task`
- `Depends On`
- `Sprint`
- `Assignee Role`
- `Acceptance Criteria`
- `Definition of Done`

## Documentos Relacionados

- `docs/jira-import.csv`
- `docs/jira-implementation-order.md`
- `docs/team-delivery-plan.md`
- `docs/mvp-implementation-plan.md`
