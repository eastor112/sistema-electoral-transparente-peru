# 06. Validadores distribuidos y auditoria publica

## 1. Rol de nodos validadores

Actores recomendados:

- Partidos politicos.
- Universidades.
- Observadores nacionales/internacionales.

Propiedades:

- Solo lectura sobre datos electorales publicados.
- Replica continua de eventos de actas.
- Verificacion independiente de hashes y firmas.

## 2. Modelo de distribucion

### 2.1 Broadcast en tiempo real

- Canal principal por WebSocket o stream de eventos (SSE/NATS/Kafka bridge).
- Mensaje incluye: `acta_id`, `version`, `hash`, `event_hash`, `timestamp`.

### 2.2 Pull periodico de reconciliacion

- Cada validador ejecuta pull incremental (por cursor/event_id).
- Permite recuperar eventos perdidos por cortes de red.

### 2.3 Snapshot + deltas

- Snapshot diario firmado institucionalmente.
- Deltas en tiempo real para mantener paridad.

## 3. Protocolo de verificacion

Por cada evento recibido:

1. Validar estructura del mensaje.
2. Recalcular hash de payload canonico.
3. Verificar firmas digitales de acta.
4. Verificar continuidad de `previous_hash` y `event_hash`.
5. Registrar resultado local (ok/falla y motivo).

Reglas de robustez adicionales:

6. Verificar eventos de custodia y autoria de acciones criticas.
7. Confirmar que no existan saltos de estado fuera de politica.
8. Emitir prueba de verificacion firmada por el validador.

## 4. Auditoria publica

### 4.1 Endpoints sugeridos

- `GET /v1/public/actas/{acta_id}`
- `GET /v1/public/actas/{acta_id}/historial`
- `GET /v1/public/ledger/events?cursor=...`
- `GET /v1/public/health/sla`
- `GET /v1/public/locales/{local_id}/mesas/apertura`
- `GET /v1/public/mesas/{mesa_id}/incidencias`
- `GET /v1/admin/mesas/{mesa_id}/fiabilidad`

### 4.2 Datos expuestos

- Hashes, versiones, timestamps, estado y metadatos no sensibles.
- Nunca exponer biometria, tokens o PII innecesaria.
- En incidencias: exponer descripcion publica, severidad, estado y timestamp.
- Mantener hash de evidencia para verificabilidad sin exponer datos sensibles.

## 5. SLA y SLO

- SLA de publicacion de acta: menor a 60 segundos.
- SLO de consistencia entre nodo central y validadores: mayor a 99.99%.
- SLO de disponibilidad API publica: mayor a 99.95%.
- SLO de deteccion de divergencia critica: menor a 2 minutos.
- SLO de apertura de expediente forense: menor a 10 minutos.

## 6. Deteccion de anomalias

### 6.1 Tipos de alerta

- Retrasos de publicacion superiores al umbral.
- Multiples versiones en ventana inusual.
- Ruptura de cadena hash.
- Divergencia entre hashes de validadores.
- Score de fiabilidad de mesa por debajo del umbral definido.

### 6.2 Accion automatica

- Marcar acta como `BLOQUEADA` para investigacion.
- Emitir alerta al centro de control electoral.
- Generar paquete forense con trazas y evidencia.

El paquete forense minimo incluye:

- Historial completo de versiones de acta.
- Cadena de custodia y eventos de firma.
- Resultados de verificacion de validadores externos.
- Huellas de tiempo y hash de todos los artefactos.

## 7. Transparencia verificable por terceros

- Publicar especificacion de canonicalizacion y hashing.
- Publicar SDK de verificacion (Python/TypeScript).
- Publicar muestras anonimizadas para pruebas comunitarias.

## 8. Esquema de consenso de auditoria

Para elevar detectabilidad del fraude:

- Cada evento critico debe tener verificacion de multiples validadores independientes.
- Se recomienda umbral de consenso (por ejemplo, 2 de 3 o 3 de 5) para marcar consistencia alta.
- Si no hay consenso, el sistema etiqueta el evento como disputado y activa investigacion.

## 9. Uso del score de fiabilidad

La calificacion de mesa del 1 al 10 se usa para:

- Priorizar auditoria humana y tecnica.
- Detectar mesas con patron atipico aun cuando no exista fraude confirmado.
- Enriquecer la cola de revision con contexto cuantitativo.
- Medir calidad operativa por region, local y mesa.
