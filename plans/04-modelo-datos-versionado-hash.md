# 04. Modelo de datos, versionado y hash

## 1. Entidades principales

### 1.1 Acta

Representa una entidad logica por mesa. No se sobrescribe; evoluciona por versiones.

Campos base sugeridos:

- `acta_id` (string unico legible)
- `mesa_id`
- `ubigeo`
- `estado_actual`
- `version_actual`
- `created_at`, `updated_at`

### 1.2 ActaVersion

Snapshot inmutable por cada cambio.

Campos:

- `acta_id`
- `version` (1..n)
- `previous_hash` (null en v1)
- `payload_resultados` (jsonb canonico)
- `hash` (sha256 del payload canonico)
- `motivo_correccion` (opcional desde v2)
- `creado_por`, `creado_en`

### 1.3 Firma

- `acta_id`
- `version`
- `dni`
- `public_key`
- `signature`
- `timestamp`
- `verificada` (bool)

### 1.4 EvidenciaImagen

- `acta_id`
- `version`
- `hash_acta`
- `imagen_url`
- `hash_imagen_raw`
- `hash_imagen_normalizada`
- `mime_type`
- `byte_size`
- `captured_at_device`
- `storage_object_version`
- `manifest_hash`
- `manifest_signature`
- `tsa_token_ref`
- `metadata` (resolucion, exif permitido, checksum cliente)

### 1.5 EventoAuditoria

- `event_id`
- `event_type`
- `entity_id`
- `payload`
- `previous_event_hash`
- `event_hash`
- `timestamp`

### 1.6 EventoCustodia

- `custody_event_id`
- `acta_id`
- `version`
- `actor_id`
- `role_id`
- `device_id`
- `action`
- `reason_code`
- `evidence_refs` (jsonb)
- `previous_custody_hash`
- `custody_hash`
- `timestamp`

### 1.7 CasoFraude

- `case_id`
- `acta_id`
- `version`
- `risk_score`
- `triggered_rules` (jsonb)
- `status` (ABIERTO, EN_ANALISIS, CERRADO, ESCALADO)
- `opened_at`, `closed_at`
- `resolution_summary`

### 1.8 MesaElectoral

- `mesa_id`
- `local_id`
- `ubigeo`
- `estado_mesa` (CONFIGURADA, ABIERTA, CERRADA)
- `jornada_id`

### 1.9 AsignacionActorMesa

- `asignacion_id`
- `mesa_id`
- `actor_id`
- `role_type` (MIEMBRO_MESA_TITULAR, MIEMBRO_MESA_SUPLENTE, MIEMBRO_MESA_AD_HOC, FISCALIZADOR_ONPE, FISCALIZADOR_JNE, PERSONERO)
- `scope` (LECTURA, VALIDACION, OPERACION)
- `enabled_from`, `enabled_to`

### 1.9.1 ReemplazoMesa

- `replacement_id`
- `mesa_id`
- `reemplaza_actor_id` (opcional si hubo titular identificado)
- `nuevo_actor_id`
- `replacement_type` (SUPLENCIA, ELECTOR_AD_HOC)
- `reason_code` (INASISTENCIA, ABANDONO, IMPEDIMENTO)
- `autorizado_por_actor_id`
- `evidence_refs` (jsonb)
- `created_at`

### 1.10 Eleccion y Cedula

- `eleccion_id`, `tipo_eleccion`, `ambito`, `fecha`
- `candidatura_id`, `organizacion`, `simbolo_url`, `orden_cedula`
- `cedula_version_id`, `layout_schema`, `hash_cedula`, `estado` (BORRADOR, APROBADA, CONGELADA)

### 1.11 EvidenciaIdentidad

- `evidence_id`
- `actor_id`
- `mesa_id`
- `tipo` (ROSTRO, DOCUMENTO, OTRO)
- `evidence_url`
- `evidence_hash`
- `captured_at`

### 1.12 EstadoAperturaMesa

- `apertura_id`
- `mesa_id`
- `local_id`
- `estado` (PENDIENTE, ABIERTA, SUSPENDIDA, CERRADA)
- `opened_at`
- `opened_by_actor_id`
- `custody_event_id`

### 1.13 IncidenciaMesa

- `incidencia_id`
- `mesa_id`
- `reportado_por_actor_id`
- `reportado_por_role_type` (MIEMBRO_MESA, PERSONERO)
- `descripcion`
- `foto_url`
- `foto_hash`
- `severidad` (BAJA, MEDIA, ALTA, CRITICA)
- `estado` (REPORTADA, EN_REVISION, RESUELTA, ESCALADA)
- `public_summary`
- `created_at`, `updated_at`

### 1.14 DeclaracionJuradaMesa

- `sworn_statement_id`
- `mesa_id`
- `jornada_id`
- `acta_id`
- `texto_version`
- `statement_hash`
- `estado` (PENDIENTE, PARCIAL, COMPLETA, OBSERVADA)
- `created_at`, `closed_at`

### 1.15 FirmaDeclaracionJurada

- `sworn_statement_signature_id`
- `sworn_statement_id`
- `actor_id`
- `role_type` (MIEMBRO_MESA, PERSONERO, FISCALIZADOR_ONPE, FISCALIZADOR_JNE)
- `signature`
- `public_key`
- `signed_at`
- `exception_reason_code` (opcional si no firma por causal registrada)

### 1.16 EstadoSincronizacionMesa

- `sync_state_id`
- `mesa_id`
- `ultimo_evento_local_seq`
- `ultimo_evento_confirmado_seq`
- `backlog_count`
- `last_sync_attempt_at`
- `last_sync_success_at`
- `connectivity_type` (FIJA, MOVIL, SATELITAL, DESCONOCIDA)
- `offline_mode_active` (bool)

### 1.17 FiabilidadMesa

- `mesa_id`
- `score` (1..10)
- `score_version`
- `factores` (jsonb)
- `ultima_actualizacion`
- `nivel` (ALTA, MEDIA, BAJA, CRITICA)

## 2. JSON de referencia

### 2.1 Acta base

```json
{
  "acta_id": "CAJ-01234",
  "mesa_id": "M-000123",
  "resultados": {
    "presidencial": {},
    "congreso": {},
    "senado": {},
    "parlamento_andino": {}
  },
  "version": 1,
  "previous_hash": null,
  "hash": "...",
  "firmas": [],
  "timestamp_creacion": "2026-05-01T12:00:00Z",
  "timestamp_publicacion": null
}
```

### 2.2 Firma

```json
{
  "dni": "12345678",
  "public_key": "base64:...",
  "signature": "base64:...",
  "timestamp": "2026-05-01T12:05:00Z"
}
```

### 2.3 Imagen

```json
{
  "acta_id": "CAJ-01234",
  "version": 1,
  "hash_acta": "...",
  "imagen_url": "s3://bucket/2026/CAJ-01234-v1.jpg",
  "hash_imagen_raw": "...",
  "hash_imagen_normalizada": "...",
  "mime_type": "image/jpeg",
  "byte_size": 3840021,
  "manifest_hash": "...",
  "manifest_signature": "base64:...",
  "tsa_token_ref": "tsa:2026-05-01:abc123"
}
```

## 3. Versionado estilo Git

Reglas:

- `v1` se crea al cierre de captura validada.
- Cada correccion crea `v(n+1)` con `previous_hash = hash(vn)`.
- Versiones previas nunca se borran ni mutan.
- La publicacion oficial referencia una version exacta.

## 4. Restricciones SQL criticas

- `unique(acta_id, version)`
- `unique(acta_id, version, dni)` para firmas
- `check(version >= 1)`
- `check(previous_hash is not null)` cuando `version > 1`
- `foreign key` fuerte entre acta, version, firmas y evidencias
- `unique(custody_event_id)` y cadena hash de custodia continua
- `check(risk_score between 0 and 100)` para casos de fraude
- `not null` en `actor_id`, `role_id`, `device_id` para acciones criticas
- `unique(mesa_id, actor_id, role_type, jornada_id)` para evitar duplicidad de asignacion
- `check(enabled_from < enabled_to)` para ventanas de autorizacion
- `check(role_type in ('MIEMBRO_MESA_TITULAR','MIEMBRO_MESA_SUPLENTE','MIEMBRO_MESA_AD_HOC','FISCALIZADOR_ONPE','FISCALIZADOR_JNE','PERSONERO'))` para asignacion de actores
- `check(estado in ('BORRADOR','APROBADA','CONGELADA'))` para cedula versionada
- `check(length(descripcion) >= 20)` para incidencias
- `not null` en `foto_url` y `foto_hash` para incidencias
- `check(reportado_por_role_type in ('MIEMBRO_MESA','PERSONERO'))` para reporte de incidencias
- `check(role_type in ('MIEMBRO_MESA_TITULAR','MIEMBRO_MESA_SUPLENTE','MIEMBRO_MESA_AD_HOC','PERSONERO','FISCALIZADOR_ONPE','FISCALIZADOR_JNE'))` para firma de declaracion jurada
- `unique(sworn_statement_id, actor_id, role_type)` para firmas de declaracion jurada
- `check(score between 1 and 10)` para fiabilidad de mesa
- `check(ultimo_evento_confirmado_seq <= ultimo_evento_local_seq)` para sincronizacion
- `unique(acta_id, version, hash_imagen_raw)` para evitar duplicidad exacta de evidencia
- `check(byte_size > 0)` para evidencia imagen
- `check(mime_type in ('image/jpeg','image/png','image/webp'))` para formatos permitidos
- `not null` en `manifest_hash`, `manifest_signature`, `tsa_token_ref` para evidencia imagen valida

## 5. Estrategia de consultas

- Indices por `mesa_id`, `ubigeo`, `estado`, `timestamp_publicacion`.
- Materialized views para dashboard de auditoria publica.
- Query de reconstruccion historica por `acta_id` ordenada por version.

## 6. Integridad referencial y validaciones

- No registrar firma si hash de version no coincide.
- No aceptar evidencia imagen con hash_acta distinto al publicado.
- No aceptar evidencia imagen si falla verificacion de `manifest_signature`.
- No aceptar evidencia imagen sin sello de tiempo valido (`tsa_token_ref`).
- No aceptar evidencia imagen si `hash_imagen_raw` recalculado no coincide con el declarado.
- No aceptar evidencia imagen si falta versionado de objeto (`storage_object_version`).
- No permitir PUBLICADA sin al menos 3 firmas validas.
- No permitir cierre de incidente sin evidencia de analisis y resolucion.
- No permitir transiciones de estado sin evento de custodia asociado.
- No permitir operacion de mesa a actores no asignados o fuera de ventana.
- No permitir activacion de suplente sin registro de ausencia o impedimento del titular.
- No permitir designacion de elector ad hoc sin evento de reemplazo y evidencia de identidad.
- No permitir publicar votos sobre cedula no aprobada o no congelada.
- No permitir publicar incidencia sin foto valida y descripcion minima.
- No permitir que actores no autorizados reporten incidencias de mesa.
- No permitir cerrar mesa sin declaracion jurada en estado `COMPLETA` o excepciones justificadas auditadas.
- No permitir firma de declaracion jurada sobre texto distinto al `statement_hash` oficial.
- No permitir confirmar lote offline fuera de secuencia causal.
- No permitir score de fiabilidad sin factores explicativos persistidos.

## 6.3 Metrica de fiabilidad de mesa

La calificacion del 1 al 10 se construye con factores ponderados, por ejemplo:

1. Consistencia matematica de resultados.
2. Numero y severidad de incidencias reportadas.
3. Calidad y completitud de evidencias (imagenes, firmas, declaracion jurada).
4. Puntualidad de apertura, cierre y sincronizacion.
5. Concordancia con validadores externos.
6. Historial de correcciones/versiones.

Regla operativa:

- `9-10`: alta certeza.
- `7-8`: confiable con observaciones menores.
- `4-6`: requiere revision focalizada.
- `1-3`: alta probabilidad de anomalia o investigacion inmediata.

## 6.2 Politica de publicacion ciudadana

En consulta publica de incidencias:

1. Exponer estado de mesa, severidad, timestamps y resumen publico.
2. Ocultar PII del reportante y metadatos sensibles de dispositivos.
3. Mantener referencia hash para verificabilidad de evidencia.

## 6.1 Validacion continua por etapas

Cada etapa persiste evidencia de validacion:

1. Validacion sintactica: esquema, tipos, obligatoriedad.
2. Validacion semantica: reglas numericas y consistencia electoral.
3. Validacion criptografica: firma, hash, nonce, anti-replay.
4. Validacion operativa: rol autorizado, dispositivo y ventana temporal.
5. Validacion de riesgo: score y reglas antifraude.

Sin estos 5 sellos, la transicion no puede confirmar.

## 7. Retencion y archivado

- Datos operativos calientes: 12-24 meses.
- Historial y auditoria: retencion legal definida por normativa.
- Archivado en almacenamiento WORM para evidencia probatoria.
