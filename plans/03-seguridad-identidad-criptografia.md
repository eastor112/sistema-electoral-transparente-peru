# 03. Seguridad, identidad y criptografia

## 1. Modelo de identidad

### 1.1 Identidad operativa

- Usuario de mesa autenticado con DNI + biometria (via proveedor externo).
- Sesion con token de corta vida (JWT access + refresh rotativo).
- Vinculacion de sesion con dispositivo, mesa y ventana horaria.

### 1.2 Integracion biometrica (RENIEC o equivalente)

- Patrón recomendado: backend-for-frontend + gateway de identidad.
- Nunca almacenar biometria cruda en backend electoral.
- Persistir solo: `identity_assertion_id`, nivel de confianza, timestamp, proveedor.

### 1.3 Evidencia fotografica operativa

- Permitir captura de rostro de miembros de mesa, fiscalizadores y validadores cuando aplique norma.
- Guardar imagen en storage cifrado con hash, timestamp y referencia de contexto.
- Evitar uso de imagen para reconocimiento no autorizado; uso acotado a trazabilidad.
- Definir politica de retencion y acceso por principio de necesidad legal.

## 2. Criptografia aplicada

### 2.1 Firma digital de acta

- Algoritmo: ed25519.
- Generacion de clave en cliente (dispositivo de mesa).
- Registro de clave publica por miembro de mesa y sesion.
- Firma del hash canonico de la version de acta.

### 2.2 Canonicalizacion previa a firma

El payload de firma debe serializarse de forma deterministica.

Reglas sugeridas:

- JSON con claves ordenadas alfabeticamente.
- UTF-8 estricto.
- Sin espacios ni campos opcionales nulos.
- Fechas en ISO-8601 UTC.

### 2.3 Cadena de integridad

Para eventos de auditoria:

`hash_n = SHA256(hash_{n-1} + event_payload_canonico)`

Para versiones de acta:

`acta_hash = SHA256(version_payload_canonico + firmas_ordenadas)`

## 3. Multi-firma obligatoria

- Umbral minimo: 3 miembros distintos.
- Reglas:
  - Un DNI no puede firmar dos veces la misma version.
  - Una firma no puede reutilizarse en otra version.
  - Si se corrige el acta, se invalidan firmas previas para la nueva version.
  - Cada firma se vincula a `device_id` y `session_id` auditables.
  - La secuencia de firmas debe conservar orden temporal verificable.

## 3.1 No repudio y cadena de custodia

Para sostener responsabilidad ante fraude se exige:

- Evidencia criptografica: firma del actor sobre hash de acta/version.
- Evidencia contextual: rol, georreferencia aproximada, dispositivo, timestamp seguro.
- Evidencia de flujo: estado previo, estado nuevo y motivo de transicion.
- Evidencia fisica: referencia a comprobante impreso y captura imagen vinculada.
- Declaracion jurada final firmada por los actores obligados de la mesa.

Toda accion critica genera un registro de custodia inmutable con correlacion a expediente.

## 3.2 Declaracion jurada de cierre

La declaracion jurada debe expresar, como minimo:

- Que el firmante realizo sus funciones en honor a la verdad.
- Que respeto el derecho democratico durante la jornada.
- Que reconoce la trazabilidad completa de sus actos en la mesa.
- Que se allana a cualquier investigacion si se detecta fraude en dicha mesa.

Requisitos tecnicos:

- Texto versionado y congelado por jornada/proceso.
- Firma digital del contenido exacto mostrado al actor.
- Vinculo criptografico con `mesa_id`, `jornada_id` y `acta_id` final.
- Marca de tiempo confiable y evidencia de identidad del firmante.

## 4. Seguridad de transporte y red

- TLS 1.3 en todos los endpoints publicos.
- mTLS entre microservicios internos.
- Certificados rotativos con expiracion corta.
- WAF y rate limiting adaptativo por IP y por mesa.

## 5. Seguridad de datos

- Cifrado en reposo (PostgreSQL TDE o disco cifrado + claves gestionadas).
- S3/object storage con cifrado server-side y politicas immutability lock.
- Separacion de PII y datos electorales en esquemas distintos.
- Controles de acceso estrictos a evidencias de rostro e identidad (solo perfiles autorizados).

## 6. Prevencion de fraude y abuso

- Idempotency key obligatoria en endpoints de escritura.
- Nonce anti-replay por operacion firmada.
- Deteccion de patrones anómalos por mesa, region y tiempo.
- Bloqueo temporal ante multiples firmas fallidas.

Controles adicionales:

- Fingerprint de dispositivo permitido por mesa/jornada.
- Geofencing blando (alerta) y duro (bloqueo) segun politica electoral.
- Heuristicas de comportamiento: firmas demasiado rapidas, secuencias improbables, cambios repetitivos.
- Reglas de separacion de funciones para evitar autoaprobacion.

## 7. Registro y forensica

- Logs de seguridad inmutables con retencion prolongada.
- Registro de eventos criticos:
  - autenticacion exitosa/fallida
  - alta de clave publica
  - firma valida/invalida
  - publicacion/correccion/bloqueo
- Correlacion por `trace_id`, `acta_id`, `mesa_id`.

Agregar identificadores de responsabilidad:

- `actor_id` (identidad verificada)
- `role_id` (rol en mesa)
- `device_id` (dispositivo autenticado)
- `custody_event_id` (evento de cadena de custodia)
- `case_id` (si abre investigacion)
- `biometric_evidence_id` (si existe evidencia de identidad/foto asociada)
- `sworn_statement_id` (si la accion corresponde a declaracion jurada)

## 8. Politica de claves

- Claves de firma de mesa efimeras por jornada.
- Rotacion automatica y destruccion segura post-jornada.
- HSM/KMS para claves de firma institucional del backend.

## 9. Checklist de seguridad para salida a produccion

1. Pentest externo e interno aprobado.
2. Simulacion de replay/man-in-the-middle mitigada.
3. Pruebas de carga con degradacion controlada.
4. Auditoria criptografica de implementacion ed25519.
5. Evidencia de trazabilidad completa de actas de prueba.
6. Simulacion de fraude interno con atribucion completa de responsabilidades.
7. Validacion legal de admissibilidad forense de logs y evidencias.
8. Validacion legal del texto y la firma de declaracion jurada por rol obligado.
