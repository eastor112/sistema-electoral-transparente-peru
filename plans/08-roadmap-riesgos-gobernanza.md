# 08. Roadmap, riesgos y gobernanza

## 1. Roadmap por fases

### Fase 0 - Protocolo, simulacion y certificacion

Objetivo:

- Definir protocolo tecnico/legal de cadena de custodia.
- Ejecutar simulacion nacional previa con volumen realista.
- Certificar controles de seguridad y auditabilidad.

Entregables:

- Manual de evidencia forense y responsabilidad por rol.
- Baseline de rendimiento para jornada (SLO/SLA firmados).
- Informe de auditoria externa pre-electoral.
- Texto oficial y politica de declaracion jurada aprobados legalmente.

### Fase 1 - MVP

Objetivo:

- Captura digital de acta.
- Firma digital basica.
- Almacenamiento seguro y consulta interna.

Entregables:

- API FastAPI v1.
- Modelo de datos versionado v1.
- Verificacion de firma ed25519.

### Fase 2 - Multi-firma y validadores

Objetivo:

- Multi-firma obligatoria (>=3).
- Broadcast a nodos validadores.
- Primer panel de auditoria.

Entregables:

- Servicio de validadores.
- Feed de eventos publicos.
- Alertas basicas de inconsistencias.

### Fase 3 - Versionado avanzado y auditoria publica

Objetivo:

- Correcciones versionadas estilo Git.
- Ledger hash inmutable.
- Portal publico de trazabilidad.

Entregables:

- Historial completo por acta.
- Pruebas criptograficas publicables.
- SLA y reportes de cumplimiento.

### Fase 4 - Integracion biometrica real y escala nacional

Objetivo:

- Integracion robusta con proveedor biometrico.
- Operacion multi-region nacional.
- Ensayos de alta concurrencia de punta a punta.

Entregables:

- Arquitectura resiliente nacional.
- Certificaciones de seguridad y auditoria externa.
- Manual operativo nacional.

## 2. Riesgos y mitigacion

| Riesgo | Mitigacion |
|---|---|
| Robo de clave | Claves efimeras por jornada + revocacion rapida |
| Error humano | UI guiada + validaciones de consistencia + bloqueos de flujo |
| Manipulacion backend | Validadores externos + ledger hash publico |
| Falta de conexion | Offline-first en cliente + colas + idempotencia |
| Imagen falsa | Hash de imagen + vinculacion con hash_acta + verificacion distribuida |
| Ataques DDoS | WAF + CDN + rate limiting + autoscaling |
| Dependencia de proveedor externo | Circuit breaker + modo contingencia + pruebas fallback |

## 3. Gobernanza del sistema

### 3.1 Comite tecnico electoral

Responsable de:

- Aprobar cambios de protocolo.
- Definir parametros de seguridad y SLA.
- Coordinar auditorias tecnicas independientes.

Define ademas:

- Politica de bloqueo/desbloqueo de actas en investigacion.
- Umbrales oficiales de riesgo y escalamiento.
- Criterios de admision de evidencia digital en disputas.
- Version oficial del texto de declaracion jurada y causales validas de excepcion.

### 3.2 Politicas de auditoria

- Auditoria pre-electoral obligatoria.
- Auditoria en vivo durante jornada.
- Auditoria post-electoral con publicacion de hallazgos.

### 3.3 Modelo de transparencia

- Publicar especificaciones tecnicas y changelog oficial.
- Publicar metricas de disponibilidad y tiempos de publicacion.
- Mantener repositorio de verificacion para terceros.

## 3.4 Matriz RACI de responsabilidad

Para cadena clara ante fraude:

- Mesa electoral: responsable de captura y firma.
- Operaciones TI electoral: responsable de disponibilidad y continuidad.
- Equipo de seguridad/fraude: responsable de deteccion y analisis.
- Comite tecnico electoral: accountable de decisiones de bloqueo y resolucion.
- Validadores externos: consultados y verificadores independientes.
- Organo de control/justicia electoral: informado y habilitado para auditoria completa.

## 4. KPIs de exito

- Tiempo medio de publicacion por acta.
- Porcentaje de actas sin correccion posterior.
- Porcentaje de actas verificadas por validadores externos.
- Numero de alertas criticas resueltas en menos de 15 minutos.
- Porcentaje de incidentes con cadena de custodia completa y verificable.
- Tiempo medio de apertura de expediente forense.
- Porcentaje de eventos criticos con consenso de validadores externos.
- Porcentaje de mesas cerradas con declaracion jurada completa y verificable.

## 5. Resultado esperado

- Eliminacion de digitacion manual posterior.
- Reduccion drastica de errores humanos.
- Trazabilidad completa verificable.
- Auditoria distribuida y evidencia fisica/digital consistente.

## 6. Vision de cierre

La robustez del sistema proviene de reglas verificables y protocolos auditables.
La adopcion del sistema proviene de una experiencia operativa simple y guiada.
