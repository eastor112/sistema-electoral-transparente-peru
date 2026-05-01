# 02. Arquitectura backend Python (FastAPI)

## 1. Arquitectura general

Flujo macro:

Dispositivo de mesa -> API central -> bus de broadcast -> validadores distribuidos -> auditoria publica.

## 2. Componentes backend

### 2.1 API Gateway (FastAPI)

Responsabilidades:

- Exponer API REST para captura, firma y publicacion.
- Validar esquema, reglas de negocio y estado de acta.
- Verificar firma digital ed25519.
- Control de idempotencia por solicitud.
- Emitir eventos a bus de mensajeria.

### 2.2 Servicio de Actas

Responsabilidades:

- Crear actas y nuevas versiones (append-only).
- Mantener maquina de estados.
- Generar hash canonico por version.
- Enlazar previous_hash en correcciones.
- Confirmar persistencia durable antes de contabilizar/publicar.

### 2.3 Servicio de Firmas

Responsabilidades:

- Registrar claves publicas por miembro de mesa y sesion.
- Validar umbral minimo (>=3 firmas).
- Verificar unicidad de firmante por acta/version.
- Auditar intentos fallidos de firma.

### 2.4 Servicio de Evidencia

Responsabilidades:

- Recibir metadatos de imagen (hash local, dimensiones, timestamp).
- Gestionar subida segura a object storage.
- Recalcular hash servidor y comparar integridad.
- Asociar evidencia a hash_acta publicado.

### 2.5 Servicio de Auditoria

Responsabilidades:

- Construir log inmutable de eventos.
- Publicar feed publico de verificacion.
- Exponer endpoints de merkle-ish chain y pruebas de integridad.

### 2.6 Servicio de Replicacion/Broadcast

Responsabilidades:

- Publicar eventos de acta firmada/publicada.
- Gestionar reintentos, orden y deduplicacion.
- Proveer snapshot + delta para nodos rezagados.

### 2.6.1 Servicio de Proyecciones y Conteo Inmediato

Responsabilidades:

- Consumir eventos de actas finalizadas/publicadas en tiempo real.
- Actualizar agregados por mesa, local, region y nacional sin espera manual.
- Mantener vistas CQRS optimizadas para resultados preliminares.
- Garantizar idempotencia para no doble contabilizar una misma version de acta.

### 2.7 Servicio de Responsabilidad y Custodia

Responsabilidades:

- Registrar cadena de custodia por acta y por version.
- Persistir quien, cuando, desde que dispositivo y bajo que rol ejecuta acciones criticas.
- Generar expediente forense inmutable ante alertas de fraude.
- Exponer timeline firmado para auditoria legal y tecnica.

### 2.8 Servicio de Reglas y Riesgo en Tiempo Real

Responsabilidades:

- Evaluar reglas antifraude en cada transicion de estado.
- Asignar score de riesgo por acta/mesa/region.
- Enrutar casos de alto riesgo a cola de revision prioritaria.
- Disparar bloqueos preventivos con trazabilidad completa.

### 2.9 Servicio de Administracion Electoral

Responsabilidades:

- Configurar mesas por localidad, recinto y ubigeo.
- Registrar y asignar miembros de mesa titulares y suplentes por jornada.
- Registrar fiscalizadores ONPE/JNE y personeros por mesa.
- Gestionar calendario, ventanas de operacion y politicas por proceso.

### 2.9.1 Servicio de Asistencia y Reemplazo de Mesa

Responsabilidades:

- Registrar asistencia real de titulares y suplentes el dia de jornada.
- Activar reemplazo por suplencia segun orden y reglas oficiales.
- Permitir designacion excepcional de elector ad hoc cuando no haya quorum suficiente.
- Generar evidencia auditada de la causal de reemplazo y del actor que autoriza.

### 2.10 Servicio de Catalogo Electoral y Cedula

Responsabilidades:

- Registrar elecciones activas (presidencial, diputados, senadores, etc).
- Registrar candidatos, listas, simbolos y metadatos oficiales.
- Versionar diseno logico de cedula por eleccion.
- Publicar artefactos de cedula validados para cliente web.

### 2.11 Servicio de Autorizacion (RBAC + ABAC)

Responsabilidades:

- Resolver permisos por rol, mesa, local y jornada.
- Aplicar politica de minimo privilegio por endpoint/accion.
- Bloquear acciones fuera de la mesa asignada o fuera de ventana.
- Auditar toda decision de autorizacion permitida/denegada.

### 2.12 Servicio de Incidencias de Mesa

Responsabilidades:

- Permitir reporte de incidencias por miembros de mesa y personeros.
- Exigir descripcion estructurada y al menos una foto del suceso.
- Clasificar severidad, estado y trazabilidad de atencion.
- Publicar vista ciudadana anonimizando datos sensibles.

### 2.13 Servicio de Estado de Apertura de Mesa

Responsabilidades:

- Registrar apertura oficial de mesa con timestamp y actor responsable.
- Publicar estado de apertura por colegio/local y mesa para consulta de electores.
- Emitir alertas por apertura tardia segun umbral normativo.

### 2.14 Servicio de Declaracion Jurada de Cierre

Responsabilidades:

- Generar el texto oficial versionado de declaracion jurada por mesa y jornada.
- Exigir firma de miembros de mesa, personeros y fiscalizadores presentes/asignados.
- Vincular la declaracion a la acta final, a la cadena de custodia y al expediente forense.
- Bloquear el cierre definitivo de mesa si faltan firmas obligatorias o constancias de ausencia justificadas.

### 2.15 Servicio de Sincronizacion Offline

Responsabilidades:

- Recibir lotes offline firmados y ordenados desde clientes de mesa.
- Validar integridad, secuencia, idempotencia y resolucion de conflictos.
- Sincronizar inmediatamente cuando detecta conectividad disponible.
- Soportar redes fijas, moviles y satelitales, incluyendo enlaces tipo Starlink.

### 2.16 Servicio de Fiabilidad de Mesa

Responsabilidades:

- Calcular una calificacion de fiabilidad de mesa del 1 al 10.
- Evaluar consistencia, puntualidad, calidad de evidencia, incidentes y validaciones superadas.
- Publicar score interno y razones explicativas auditables.
- Disparar revision prioritaria sobre mesas con score bajo o caidas abruptas.

### 2.17 Servicio de Autenticacion e Identidad

Responsabilidades:

- Gestionar login, refresh y contexto de identidad de actores del sistema.
- Integrar validacion de identidad (DNI/biometria) segun proveedor oficial.
- Emitir y validar tokens de sesion con politicas de expiracion/rotacion.
- Registrar eventos de autenticacion para auditoria y trazabilidad.

### 2.18 Servicio de Notificaciones

Responsabilidades:

- Emitir notificaciones operativas para miembros, fiscalizadores y autoridades.
- Publicar alertas de riesgo, incidencias y estado de sincronizacion.
- Exponer canales en tiempo real para panel interno y vistas publicas permitidas.
- Mantener entrega idempotente y con trazabilidad de recepcion.

## 3. Arquitectura en capas (Clean + Hexagonal)

- Capa API: routers, DTOs, validacion de entrada.
- Capa aplicacion: casos de uso y orquestacion de transacciones.
- Capa dominio: entidades (Acta, Firma, Evento), invariantes y reglas.
- Capa infraestructura: PostgreSQL, Redis, S3, bus, integraciones externas.

Beneficio: permite cambiar adaptadores sin alterar reglas electorales.

## 3.1 Patron de procesamiento para velocidad nacional

Para publicar resultados en horas y no en semanas:

- Escritura transaccional: API valida y persiste en modelo normalizado (OLTP).
- Publicacion por eventos: outbox -> bus -> consumidores de proyecciones.
- Lectura masiva (CQRS): tablas/materializaciones denormalizadas para consulta publica.
- Agregacion por niveles: mesa -> local -> regional -> nacional con recalculo continuo.

Secuencia obligatoria de cierre exitoso:

1. Persistencia transaccional de version final de acta.
2. Confirmacion de commit durable.
3. Emision de evento de acta finalizada al outbox.
4. Actualizacion inmediata de proyecciones y conteo.
5. Propagacion a validadores y auditoria publica.

Esto evita consultas complejas sobre tablas operativas durante picos de jornada.

## 3.2 Disponibilidad y escalado horizontal

La arquitectura debe evitar cuellos de botella verticales.

Lineamientos:

- APIs stateless detras de load balancers.
- Consumers paralelos por particion/event stream.
- Cache y sesiones distribuidas, nunca en memoria local de un nodo.
- Base de datos con replicas, particionado y estrategia de failover automatizado.
- Portal ciudadano y panel administrativo desacoplados de la ruta critica de escritura.

## 3.3 Estrategia offline-first

Cuando no exista internet en mesa:

- El cliente PWA opera con almacenamiento local cifrado y cola durable.
- Cada accion se guarda como evento firmado y ordenado localmente.
- La mesa puede continuar captura, incidencias y firmas sin bloqueo por red.

Cuando la conectividad reaparece:

- La cola se sincroniza inmediatamente en orden causal.
- Se usa idempotency key por evento para evitar duplicados.
- La plataforma prioriza enviar primero cierres de acta, incidencias criticas y evidencias pendientes.
- La reconexion puede ocurrir por cualquier enlace disponible, incluido satelital.

## 4. Stack tecnico recomendado

- Framework: FastAPI + Pydantic v2.
- Persistencia: SQLAlchemy 2 + Alembic + psycopg.
- Asincronia: asyncio + background workers (Celery/RQ o consumers dedicados).
- Mensajeria: NATS JetStream o Kafka.
- Cache/coord: Redis.
- AuthN/AuthZ: OAuth2/JWT + mTLS entre servicios internos.

Para cliente web multi-dispositivo:

- Frontend web (PWA) consumiendo BFF/API.
- WebSocket/SSE para estado en vivo y confirmaciones.
- Soporte de subida de evidencia (imagen/documento) desde movil/tablet.

## 5. Contratos API (resumen)

### 5.1 Captura de acta

- `POST /v1/actas`
- Crea acta en estado ABIERTA.

### 5.2 Validacion y cierre de captura

- `POST /v1/actas/{acta_id}/validar`
- Ejecuta reglas de consistencia y mueve a EN_VALIDACION.

### 5.3 Registro de firma

- `POST /v1/actas/{acta_id}/firmas`
- Verifica firma ed25519 y agrega evidencia de firmante.

### 5.4 Publicacion

- `POST /v1/actas/{acta_id}/publicar`
- Requiere umbral de firmas y genera evento PUBLICADA.

### 5.5 Correccion versionada

- `POST /v1/actas/{acta_id}/corregir`
- Crea nueva version con `previous_hash` obligatorio.

### 5.6 Consulta de trazabilidad

- `GET /v1/actas/{acta_id}/custodia`
- Devuelve cadena de responsabilidad y evidencia asociada.

### 5.7 Evaluacion de riesgo

- `GET /v1/actas/{acta_id}/riesgo`
- Devuelve score de riesgo, reglas disparadas y estado de investigacion.

### 5.8 Administracion de mesas

- `POST /v1/admin/mesas`
- `POST /v1/admin/mesas/{mesa_id}/miembros`
- `POST /v1/admin/mesas/{mesa_id}/suplentes`
- `POST /v1/admin/mesas/{mesa_id}/fiscalizadores`
- `POST /v1/admin/mesas/{mesa_id}/personeros`

### 5.8.1 Asistencia y reemplazo

- `POST /v1/mesas/{mesa_id}/asistencia`
- `POST /v1/mesas/{mesa_id}/reemplazos/suplente`
- `POST /v1/mesas/{mesa_id}/reemplazos/elector-ad-hoc`

### 5.9 Catalogo electoral y cedula

- `POST /v1/admin/elecciones`
- `POST /v1/admin/elecciones/{eleccion_id}/candidatos`
- `POST /v1/admin/elecciones/{eleccion_id}/cedula`
- `GET /v1/public/elecciones/{eleccion_id}/cedula`

### 5.10 Incidencias de mesa

- `POST /v1/mesas/{mesa_id}/incidencias`
- `GET /v1/mesas/{mesa_id}/incidencias`
- `PATCH /v1/mesas/{mesa_id}/incidencias/{incidencia_id}`

### 5.11 Estado de apertura y consulta ciudadana

- `POST /v1/mesas/{mesa_id}/apertura`
- `GET /v1/public/locales/{local_id}/mesas/apertura`
- `GET /v1/public/mesas/{mesa_id}/incidencias`

### 5.12 Declaracion jurada de cierre

- `POST /v1/mesas/{mesa_id}/declaracion-jurada/generar`
- `POST /v1/mesas/{mesa_id}/declaracion-jurada/firmas`
- `GET /v1/mesas/{mesa_id}/declaracion-jurada`

### 5.13 Sincronizacion offline y fiabilidad

- `POST /v1/sync/lotes`
- `GET /v1/mesas/{mesa_id}/fiabilidad`
- `GET /v1/admin/mesas/fiabilidad`

### 5.14 Autenticacion y notificaciones

- `POST /v1/auth/login`
- `POST /v1/auth/refresh`
- `GET /v1/auth/me`
- `GET /v1/notificaciones`
- `POST /v1/notificaciones/broadcast`

## 6. Reglas de consistencia critica

- Suma de votos por lista debe coincidir con total por eleccion.
- No permitir valores negativos ni fuera de rango de electores.
- Bloquear publicacion sin multi-firma valida.
- No permitir editar una version publicada; solo crear version nueva.
- No permitir publicar acta con score de riesgo critico sin escalamiento registrado.
- Toda accion critica debe incluir `actor_id`, `rol`, `device_id` y `reason_code`.
- No permitir a un miembro de mesa operar una mesa no asignada.
- No permitir que un suplente opere sin activacion formal de reemplazo.
- No permitir que un elector ad hoc opere sin designacion, identidad validada y causal registrada.
- No permitir cambios de cedula despues del congelamiento de jornada.
- No permitir reporte de incidencia sin descripcion y evidencia fotografica minima.
- No permitir publicar PII en endpoints publicos de incidencias.
- No permitir cierre definitivo de mesa sin declaracion jurada completa o causal de excepcion registrada.
- No permitir que la falta de internet impida la continuidad operativa local de la mesa.
- No permitir doble contabilizacion de eventos sincronizados desde modo offline.

## 7. Rendimiento y escalabilidad

- Horizontal scaling en API stateless.
- Particionado por region/ubigeo en tablas de alto volumen.
- Backpressure en consumidores de broadcast.
- Objetivo inicial: 25k RPS lectura publica y 2k RPS escritura operativa.
- El dimensionamiento debe considerar simultaneidad nacional de mesas + actores internos + electores consultando.

Objetivos senior de jornada:

- p95 escritura de acta firmada menor a 400 ms en API central.
- p95 publicacion a feed de resultados menor a 5 s.
- p95 de contabilizacion desde acta finalizada a agregado nacional menor a 10 s.
- p99 de propagacion a validadores menor a 20 s.
- Consolidado nacional preliminar mayor a 95% de actas menor a 4 h.
- Cero downtime planificado durante la jornada electoral.
- p95 de sincronizacion de lote offline menor a 30 s tras recuperacion de conectividad.
- Calculo de score de fiabilidad actualizado en menos de 60 s tras evento relevante.

## 8. Resiliencia

- Outbox pattern para garantizar publicacion de eventos tras commit DB.
- Retry con jitter exponencial para integraciones externas.
- Circuit breakers para RENIEC/biometria y object storage.
- Dead-letter queue para eventos no procesables.
- Reproceso deterministico por particion para reconstruccion completa post-incidente.
- Snapshot horario de proyecciones CQRS para recuperacion rapida de portal publico.
- Rehidratacion automatica de proyecciones desde log de eventos si cae algun proyector.
- Cola de sincronizacion reenviable y durable para mesas con conectividad intermitente.

## 8.1 Validacion por compuertas (gates)

Cada endpoint critico aplica 4 gates obligatorias:

1. Gate de identidad: autenticacion + rol + vinculacion mesa-dispositivo.
2. Gate de integridad: esquema, reglas numericas y hash esperado.
3. Gate criptografica: firma, nonce, anti-replay e idempotencia.
4. Gate de riesgo: score antifraude y politica de bloqueo/escalamiento.

## 9. Estructura de codigo sugerida

```text
backend/
  app/
    api/
      v1/
        routes_actas.py
        routes_firmas.py
        routes_auditoria.py
    domain/
      entities.py
      rules.py
      value_objects.py
    application/
      use_cases/
      services/
    infrastructure/
      db/
      repositories/
      messaging/
      storage/
      crypto/
    workers/
    main.py
```
