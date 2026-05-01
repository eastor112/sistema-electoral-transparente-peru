# 07. Operacion, DevSecOps y observabilidad

## 1. Estrategia de despliegue

- Entornos: dev, qa, staging nacional, produccion nacional.
- Despliegue en Kubernetes multi-zona.
- Blue/green o canary para cambios de backend.
- Infraestructura como codigo (Terraform + Helm).
- Capacidad elastica para escalar horizontalmente por picos regionales y nacionales.
- Balanceadores redundantes y sin punto unico de falla.

## 2. Pipeline CI/CD

Pasos minimos:

1. Lint y tipado estatico.
2. Unit tests + integration tests.
3. Security scans (SAST, dependencias, contenedores).
4. Pruebas criptograficas y de compatibilidad de firma.
5. Prueba de carga base por build candidata.
6. Aprobacion de release firmada.

## 3. Observabilidad

### 3.1 Metrics

- Latencia p50/p95/p99 por endpoint.
- Throughput de publicaciones por minuto.
- Error rate por tipo (validacion, seguridad, infraestructura).
- Tiempo de propagacion a validadores.
- Backlog de colas por etapa (ingesta, firma, publicacion, proyeccion).
- Tiempo de consolidacion por nivel (mesa/local/regional/nacional).
- Tiempo de deteccion y contencion de incidente de fraude.
- Tiempo entre acta finalizada y contabilizacion efectiva en agregados.
- Saturacion por pool de API, cola, DB y proyecciones.
- Backlog de mesas en modo offline y tiempo medio de reconexion.
- Distribucion de conectividad por tipo (fija, movil, satelital).
- Distribucion de score de fiabilidad por mesa y region.

### 3.2 Logs

- Estructurados JSON.
- Campos minimos: `trace_id`, `acta_id`, `mesa_id`, `event_type`, `status`.
- Redaccion de datos sensibles por defecto.

### 3.3 Tracing distribuido

- OpenTelemetry en API, workers y bus.
- Seguimiento extremo a extremo desde captura hasta auditoria publica.

## 4. Continuidad operativa

- RPO cercano a 0 para actas publicadas.
- RTO menor a 15 minutos para API critica.
- Replicacion PostgreSQL sincrona en regiones clave.
- Backups inmutables y pruebas periodicas de restauracion.

Objetivos de jornada para resultados en horas:

- Publicar primer corte nacional util en menos de 60 minutos.
- Alcanzar mayor a 95% de actas procesadas en menos de 4 horas.
- Mantener rezago de proyecciones menor a 30 segundos p95.
- Mantener contabilizacion de acta finalizada menor a 10 segundos p95.
- Mantener capacidad disponible para crecimiento inesperado de consultas ciudadanas sin afectar escritura critica.
- Mantener sincronizacion offline menor a 30 segundos p95 tras recuperar conectividad.
- Mantener mas del 95% de mesas con score de fiabilidad >= 8, salvo mesas observadas.

## 5. Seguridad operacional

- Zero trust interno.
- Accesos privilegiados con MFA y just-in-time access.
- Rotacion de secretos automatica.
- Hardening de contenedores y nodos.

## 6. Pruebas no funcionales

### 6.1 Carga y stress

- Simular picos nacionales por cierre de jornada.
- Validar degradacion elegante y colas persistentes.
- Validar concurrencia simultanea de miembros, fiscalizadores, autoridades y electores.
- Verificar que la ruta critica de cierre y contabilizacion siga estable bajo maxima lectura publica.
- Simular porcentaje de mesas operando offline y reconectando en oleadas.
- Simular fallback a enlaces satelitales para zonas con baja conectividad.

### 6.2 Chaos engineering

- Caida de broker de mensajes.
- Latencia extrema en DB.
- Perdida temporal de conectividad entre regiones.
- Caida de nodos de API o proyectores sin interrumpir contabilizacion global.
- Flapping de red en mesas y reconexion parcial por enlaces satelitales.

### 6.3 Game days

- Simulacros tecnicos y operativos con actores reales.
- Runbooks auditados y actualizados tras cada simulacro.

## 6.4 Simulacion nacional de cierre

- Simular carga de jornada completa con patrones reales por region.
- Medir punta de concurrencia de 15, 30 y 60 minutos.
- Verificar que los dashboards de resultados no se degraden durante picos.
- Validar apertura automatica de casos de fraude y SLA de respuesta.

## 8. War room electoral

Estructura operativa recomendada:

- Celda SRE (plataforma y capacidad)
- Celda de seguridad (incidentes y fraude)
- Celda de datos (consistencia y proyecciones)
- Celda legal/auditoria (cadena de custodia y evidencia)

Objetivo operativo central:

- Toda acta finalizada debe verse persistida, contabilizada y emitida a validadores sin intervencion manual.
- Toda mesa sin internet debe seguir operando y sincronizar apenas el enlace reaparezca.

Cada celda trabaja con runbooks, escalamiento on-call y metricas de decision.

## 7. Gobierno de cambios

- Ventanas de cambio controladas en periodo electoral.
- Congelamiento de features antes de jornada.
- Solo hotfixes autorizados con trazabilidad completa.
