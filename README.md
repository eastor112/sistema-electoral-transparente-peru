# Plan Maestro - Sistema Electoral Digital Auditado y Distribuido (Backend Python)

Este repositorio contiene el diseno integral de un sistema electoral digital con enfoque de producto, arquitectura auditable y construccion abierta por la comunidad.

## Proyecto abierto para la transparencia electoral

Este proyecto nace con una premisa central: la transparencia electoral mejora cuando la arquitectura, las reglas del sistema y los mecanismos de auditoria pueden ser revisados publicamente.

Tambien parte de una necesidad concreta: ante los cuestionamientos, denuncias de irregularidades y preocupaciones publicas que han rodeado las ultimas 3 elecciones en el Peru, este sistema busca proponer una alternativa auditable, transparente y tecnicamente verificable.

Por eso, este repositorio se plantea como una iniciativa abierta para:

- Disenar tecnologia electoral verificable por terceros.
- Permitir escrutinio tecnico y ciudadano de la arquitectura.
- Facilitar colaboracion de desarrolladores, auditores, academia y sociedad civil.
- Reducir cajas negras en sistemas criticos para la democracia.

El objetivo no es solo construir software funcional, sino construir confianza publica mediante apertura, trazabilidad y revisabilidad.

## Objetivo del plan

Definir un backend en Python (FastAPI) que cumpla con:

- Minimizar error humano.
- Eliminar digitacion posterior.
- Garantizar trazabilidad total.
- Permitir auditoria publica en tiempo real.
- Hacer el fraude extremadamente detectable.
- Garantizar alta disponibilidad y escalado horizontal para soportar jornada nacional sin degradacion critica.

Y que ademas pueda ser desarrollado, auditado y mejorado por una comunidad abierta interesada en la integridad del proceso electoral.

Y que ademas soporte operacion electoral completa:

- Panel de administracion para configurar mesas por localidad.
- Registro y asignacion de miembros de mesa titulares y suplentes por mesa.
- Registro de fiscalizadores (ONPE/JNE) y personeros por mesa/jornada.
- Configuracion de candidatos, simbolos y diseno de cedula por tipo de eleccion.
- Operacion web multi-dispositivo (celular, tablet, laptop y desktop).
- Operacion offline-first con sincronizacion inmediata al detectar conectividad.

## Documentos

1. [plans/01-vision-y-principios.md](plans/01-vision-y-principios.md)
   Vision del sistema, objetivos y principios de diseno.
2. [plans/02-arquitectura-backend-python.md](plans/02-arquitectura-backend-python.md)
   Arquitectura tecnica backend con FastAPI, componentes y decisiones clave.
3. [plans/03-seguridad-identidad-criptografia.md](plans/03-seguridad-identidad-criptografia.md)
   Identidad, autenticacion, firmas digitales y modelo de confianza.
4. [plans/04-modelo-datos-versionado-hash.md](plans/04-modelo-datos-versionado-hash.md)
   Modelo de datos, eventos, versionado estilo Git y log inmutable.
5. [plans/05-flujo-operativo-estados-acta.md](plans/05-flujo-operativo-estados-acta.md)
   Flujo extremo a extremo, maquina de estados y reglas de negocio.
6. [plans/06-validadores-distribucion-auditoria.md](plans/06-validadores-distribucion-auditoria.md)
   Nodos validadores, broadcast, auditoria y deteccion de anomalias.
7. [plans/07-operacion-devsecops-observabilidad.md](plans/07-operacion-devsecops-observabilidad.md)
   Operacion nacional, despliegue, observabilidad, continuidad y seguridad operacional.
8. [plans/08-roadmap-riesgos-gobernanza.md](plans/08-roadmap-riesgos-gobernanza.md)
   Roadmap de implementacion, riesgos y gobierno del sistema.
9. [plans/09-panel-administracion-roles-y-cedula.md](plans/09-panel-administracion-roles-y-cedula.md)
   Panel de administracion electoral, roles, permisos por mesa y diseno de cedula.

## Stack recomendado (backend)

- Python 3.12+
- FastAPI + Uvicorn/Gunicorn
- PostgreSQL 16+
- Redis (colas, cache y deduplicacion)
- Object Storage compatible S3 (imagenes de acta)
- Mensajeria para broadcast (NATS o Kafka)
- OpenTelemetry + Prometheus + Grafana + Loki

Base de datos principal confirmada para este proyecto: PostgreSQL.

## Principio rector

Confiar en reglas verificables, no en operadores individuales.

## Principio de apertura

La transparencia del sistema tambien depende de la transparencia de su construccion.

Por ello, este proyecto debe favorecer:

- Documentacion publica de decisiones tecnicas.
- Protocolos auditables y entendibles.
- Especificaciones abiertas para integraciones y validacion.
- Revision comunitaria de riesgos, reglas y controles.
- Trazabilidad de cambios en arquitectura, seguridad y operacion.

## Principio de disponibilidad

La arquitectura debe poder escalar horizontalmente para atender simultaneamente:

- Todas las mesas electorales activas.
- Miembros de mesa, personeros y fiscalizadores.
- Autoridades electorales y operadores de control.
- Electores consultando apertura, incidencias y resultados.

El sistema debe asumir como escenario normal el dia de maxima carga electoral, no como caso excepcional.

## Principio de conectividad resiliente

El sistema debe operar correctamente tanto con conectividad estable como con conectividad intermitente o ausente.

Reglas:

- Si no hay internet, la mesa sigue operando en modo offline seguro.
- Si vuelve la conectividad, la sincronizacion ocurre inmediatamente y en orden.
- La arquitectura debe aprovechar cualquier medio disponible: red fija, movil o satelital, incluyendo enlaces tipo Starlink.

## Ajustes incorporados

Esta version del plan incorpora un endurecimiento tecnico y operativo para cumplir simultaneamente con:

- Eficiencia de procesamiento nacional y publicacion en horas.
- Auditabilidad forense de extremo a extremo.
- Cadena de responsabilidad trazable ante fraude en mesa.
- Validacion continua en cada compuerta del proceso.

Ejes transversales agregados:

1. Cadena de custodia digital y fisica con no repudio.
2. Motor de reglas antifraude en tiempo real (riesgo por mesa/acta).
3. Modelo CQRS para lectura masiva de resultados preliminares.
4. Runbook de investigacion y judicializacion de incidentes.

## Comunidad y colaboracion

Este repositorio busca recibir aportes de:

- Ingenieros de software y seguridad.
- Especialistas en sistemas electorales.
- Auditores tecnicos y peritos forenses.
- Organizaciones civiles y academia.
- Ciudadania interesada en vigilancia tecnologica y transparencia.

Areas naturales de contribucion:

- Arquitectura y escalabilidad.
- Criptografia, firma y cadena de custodia.
- UX operativa para mesas electorales.
- Accesibilidad y usabilidad multi-dispositivo.
- Auditoria publica, validadores y metricas de confianza.
- Modelos de datos, gobernanza y protocolos abiertos.

Toda mejora propuesta debe fortalecer al menos uno de estos atributos:

- transparencia
- auditabilidad
- resiliencia
- integridad
- usabilidad
- escalabilidad

## Calidad antes de push

Para estandarizar contribuciones, este repositorio incluye un hook `pre-push` que ejecuta:

- `make test`
- `make lint`
- `make typecheck`

solo cuando se intenta hacer push a `main` o `develop`.

Activacion local (una vez por clon):

`make hooks`

## Alcance funcional complementario

1. Pre-jornada (administracion)
   - Alta de mesas por localidad/ubigeo.
   - Asignacion de miembros de mesa titulares y suplentes.
   - Registro de fiscalizadores y personeros habilitados.
   - Definicion de cedula por proceso electoral.

2. Jornada (operacion de mesa)
   - Miembros de mesa acceden solo a su mesa.
   - Si faltan titulares, se activa suplencia; si no alcanza, electores presentes pueden asumir la mesa con registro ad hoc auditado.
   - Transcripcion/digitalizacion de resultados del acta de mesa (el voto del elector sigue siendo en papel) con validacion en tiempo real.
   - Impresion de acta, firma fisica y re-subida de evidencia.
   - Captura de evidencia fotografica de miembros y validadores.
   - Miembros de mesa y personeros pueden reportar incidencias con descripcion y foto.
   - Al cierre, miembros de mesa, personeros y fiscalizadores firman una declaracion jurada de actuacion veraz y sometimiento a investigacion ante fraude.
   - Si no hay conectividad, la mesa continua offline y sincroniza apenas detecta internet.

3. Consulta ciudadana (elector)
   - El elector puede consultar apertura de su mesa en su colegio/local.
   - El elector puede consultar incidencias reportadas y su estado.

4. Post-jornada (auditoria)
   - Publicacion y conciliacion distribuida.
   - Reconstruccion completa de decisiones por actor.
   - Apertura automatica de caso ante anomalias de custodia o riesgo.
   - Conservacion de la declaracion jurada firmada como evidencia legal y forense.
   - Calificacion de fiabilidad por mesa del 1 al 10 con metricas auditables.

## Regla de contabilizacion inmediata

En el momento en que el acta queda finalizada y validada:

1. Se persiste de forma duradera en el sistema.
2. Se contabiliza inmediatamente en las proyecciones y consolidaciones.
3. Se emite al bus de eventos y se envia a validadores externos.
4. Se publica su trazabilidad sin esperar procesos manuales posteriores.
