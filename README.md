# Plan Maestro - Sistema Electoral Digital Auditado y Distribuido (Backend Python)

Este repositorio contiene el diseño integral de un sistema electoral digital con enfoque de producto, arquitectura auditable y construcción abierta por la comunidad.

## Proyecto abierto para la transparencia electoral

Este proyecto nace con una premisa central: la transparencia electoral mejora cuando la arquitectura, las reglas del sistema y los mecanismos de auditoría pueden ser revisados públicamente.

También parte de una necesidad concreta: ante los cuestionamientos, denuncias de irregularidades y preocupaciones públicas que han rodeado las últimas 3 elecciones en el Perú, este sistema busca proponer una alternativa auditable, transparente y técnicamente verificable.

Por eso, este repositorio se plantea como una iniciativa abierta para:

- Diseñar tecnología electoral verificable por terceros.
- Permitir escrutinio técnico y ciudadano de la arquitectura.
- Facilitar colaboración de desarrolladores, auditores, academia y sociedad civil.
- Reducir cajas negras en sistemas críticos para la democracia.

El objetivo no es solo construir software funcional, sino construir confianza pública mediante apertura, trazabilidad y revisabilidad.

## Objetivo del plan

Definir un backend en Python (FastAPI) que cumpla con:

- Minimizar error humano.
- Eliminar digitación posterior.
- Garantizar trazabilidad total.
- Permitir auditoría pública en tiempo real.
- Hacer el fraude extremadamente detectable.
- Garantizar alta disponibilidad y escalado horizontal para soportar jornada nacional sin degradación crítica.

Y que, además, pueda ser desarrollado, auditado y mejorado por una comunidad abierta interesada en la integridad del proceso electoral.

Y que, además, soporte operación electoral completa:

- Panel de administración para configurar mesas por localidad.
- Registro y asignación de miembros de mesa titulares y suplentes por mesa.
- Registro de fiscalizadores (ONPE/JNE) y personeros por mesa/jornada.
- Configuración de candidatos, símbolos y diseño de cédula por tipo de elección.
- Operación web multidispositivo (celular, tablet, laptop y desktop).
- Operación offline-first con sincronización inmediata al detectar conectividad.

## Documentos

1. [plans/01-vision-y-principios.md](plans/01-vision-y-principios.md)
   Visión del sistema, objetivos y principios de diseño.
2. [plans/02-arquitectura-backend-python.md](plans/02-arquitectura-backend-python.md)
   Arquitectura técnica backend con FastAPI, componentes y decisiones clave.
3. [plans/03-seguridad-identidad-criptografia.md](plans/03-seguridad-identidad-criptografia.md)
   Identidad, autenticación, firmas digitales y modelo de confianza.
4. [plans/04-modelo-datos-versionado-hash.md](plans/04-modelo-datos-versionado-hash.md)
   Modelo de datos, eventos, versionado estilo Git y log inmutable.
5. [plans/05-flujo-operativo-estados-acta.md](plans/05-flujo-operativo-estados-acta.md)
   Flujo extremo a extremo, máquina de estados y reglas de negocio.
6. [plans/06-validadores-distribucion-auditoria.md](plans/06-validadores-distribucion-auditoria.md)
   Nodos validadores, broadcast, auditoría y detección de anomalías.
7. [plans/07-operacion-devsecops-observabilidad.md](plans/07-operacion-devsecops-observabilidad.md)
   Operación nacional, despliegue, observabilidad, continuidad y seguridad operacional.
8. [plans/08-roadmap-riesgos-gobernanza.md](plans/08-roadmap-riesgos-gobernanza.md)
   Roadmap de implementación, riesgos y gobierno del sistema.
9. [plans/09-panel-administracion-roles-y-cedula.md](plans/09-panel-administracion-roles-y-cedula.md)
   Panel de administración electoral, roles, permisos por mesa y diseño de cédula.

## Stack recomendado (backend)

- Python 3.12+
- FastAPI + Uvicorn/Gunicorn
- PostgreSQL 16+
- Redis (colas, caché y deduplicación)
- Object Storage compatible con S3 (imágenes de acta)
- Mensajería para broadcast (NATS o Kafka)
- OpenTelemetry + Prometheus + Grafana + Loki

Base de datos principal confirmada para este proyecto: PostgreSQL.

## Principio rector

Confiar en reglas verificables, no en operadores individuales.

## Principio de apertura

La transparencia del sistema también depende de la transparencia de su construcción.

Por ello, este proyecto debe favorecer:

- Documentación pública de decisiones técnicas.
- Protocolos auditables y entendibles.
- Especificaciones abiertas para integraciones y validación.
- Revisión comunitaria de riesgos, reglas y controles.
- Trazabilidad de cambios en arquitectura, seguridad y operación.

## Principio de disponibilidad

La arquitectura debe poder escalar horizontalmente para atender simultáneamente:

- Todas las mesas electorales activas.
- Miembros de mesa, personeros y fiscalizadores.
- Autoridades electorales y operadores de control.
- Electores consultando apertura, incidencias y resultados.

El sistema debe asumir como escenario normal el día de máxima carga electoral, no como caso excepcional.

## Principio de conectividad resiliente

El sistema debe operar correctamente tanto con conectividad estable como con conectividad intermitente o ausente.

Reglas:

- Si no hay internet, la mesa sigue operando en modo offline seguro.
- Si vuelve la conectividad, la sincronización ocurre inmediatamente y en orden.
- La arquitectura debe aprovechar cualquier medio disponible: red fija, móvil o satelital, incluyendo enlaces tipo Starlink.

## Ajustes incorporados

Esta versión del plan incorpora un endurecimiento técnico y operativo para cumplir simultáneamente con:

- Eficiencia de procesamiento nacional y publicación en horas y no semanas.
- Auditabilidad forense de extremo a extremo.
- Cadena de responsabilidad trazable ante fraude en mesa.
- Validación continua en cada compuerta del proceso.

Ejes transversales agregados:

1. Cadena de custodia digital y física con no repudio.
2. Motor de reglas antifraude en tiempo real (riesgo por mesa/acta).
3. Modelo CQRS para lectura masiva de resultados preliminares.
4. Runbook de investigación y judicialización de incidentes.
5. Integridad criptográfica de datos (doble hash, manifiesto firmado, sello de tiempo y storage inmutable).

## Comunidad y colaboración

Este repositorio busca recibir aportes de:

- Ingenieros de software y seguridad.
- Especialistas en sistemas electorales.
- Auditores técnicos y peritos forenses.
- Organizaciones civiles y academia.
- Ciudadanía interesada en vigilancia tecnológica y transparencia.

Áreas naturales de contribución:

- Arquitectura y escalabilidad.
- Criptografía, firma y cadena de custodia.
- UX operativa para mesas electorales.
- Accesibilidad y usabilidad multi-dispositivo.
- Auditoría pública, validadores y métricas de confianza.
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

Activación local (una vez por clon):

`make hooks`

## Alcance funcional complementario

1. Pre-jornada (administración)
   - Alta de mesas por localidad/ubigeo.
   - Asignación de miembros de mesa titulares y suplentes.
   - Registro de fiscalizadores y personeros habilitados.
   - Definición de cédula por proceso electoral.

2. Jornada (operación de mesa)
   - Miembros de mesa acceden solo a su mesa.
   - Si faltan titulares, se activa suplencia; si no alcanza, electores presentes pueden asumir la mesa con registro ad hoc auditado.
   - Transcripción/digitalización de resultados del acta de mesa (el voto del elector sigue siendo en papel), con validación en tiempo real.
   - Impresión de acta, firma física y re-subida de evidencia.
   - Captura de evidencia fotográfica de miembros y validadores.
   - Miembros de mesa y personeros pueden reportar incidencias con descripción y foto.
   - Al cierre, miembros de mesa, personeros y fiscalizadores firman una declaración jurada de actuación veraz y sometimiento a investigación ante fraude.
   - Si no hay conectividad, la mesa continúa offline y sincroniza apenas detecta internet.

3. Consulta ciudadana (elector)
   - El elector puede consultar apertura de su mesa en su colegio/local.
   - El elector puede consultar incidencias reportadas y su estado.

4. Post-jornada (auditoría)
   - Publicación y conciliación distribuida.
   - Reconstrucción completa de decisiones por actor.
   - Apertura automática de caso ante anomalías de custodia o riesgo.
   - Conservación de la declaración jurada firmada como evidencia legal y forense.
   - Calificación de fiabilidad por mesa del 1 al 10 con métricas auditables.

## Regla de contabilización inmediata

En el momento en que el acta queda finalizada y validada:

1. Se persiste de forma duradera en el sistema.
2. Se contabiliza inmediatamente en las proyecciones y consolidaciones.
3. Se emite al bus de eventos y se envía a validadores externos.
4. Se publica su trazabilidad sin esperar procesos manuales posteriores.
