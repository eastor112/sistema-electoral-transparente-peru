# 09. Panel de administracion, roles y cedula electoral

## 1. Objetivo

Definir el modulo de administracion electoral que prepara la jornada y garantiza control total sobre:

- Mesas por localidad/ubigeo.
- Actores habilitados por mesa.
- Catalogo de elecciones y candidatos.
- Diseno y congelamiento de cedula.
- Cadena de responsabilidad sobre cada configuracion.

## 2. Modulos del panel de administracion

### 2.1 Modulo de mesas

Funciones:

- Alta masiva e individual de mesas.
- Asignacion por local, distrito, provincia y region.
- Estado de mesa (configurada, habilitada, en jornada, cerrada).
- Carga por archivos y API con validaciones.
- Configuracion de titulares, suplentes y orden de reemplazo.

### 2.2 Modulo de actores electorales

Actores:

- Miembros de mesa titulares (presidente, secretario, tercer miembro).
- Miembros de mesa suplentes.
- Electores designados ad hoc para completar mesa.
- Fiscalizadores ONPE/JNE.
- Personeros.

Funciones:

- Registro de identidad y rol.
- Asignacion a mesa y ventana horaria.
- Revocacion o reemplazo con trazabilidad.
- Politicas de permiso por alcance y accion.
- Registro de asistencia y activacion de reemplazos por jornada.

### 2.3 Modulo de elecciones y candidatos

Funciones:

- Crear proceso electoral por tipo (presidencial, diputados, senadores, etc).
- Registrar candidatos/listas y simbolos oficiales.
- Validar consistencia de catalogos antes de publicacion.
- Versionar cambios y mantener historial de configuracion.

### 2.4 Modulo de cedula electoral

Funciones:

- Disenar cedula logica (orden, opciones, metadatos).
- Validar reglas de consistencia visual y funcional.
- Aprobar y congelar cedula antes de jornada.
- Publicar cedula firmada digitalmente para clientes de mesa.

### 2.5 Modulo de incidencias y apertura

Funciones:

- Registrar apertura oficial de mesa por colegio/local.
- Gestionar flujo de incidencias reportadas por mesa.
- Clasificar severidad y estado de atencion.
- Publicar vista ciudadana de apertura e incidencias.

### 2.6 Modulo de declaracion jurada de cierre

Funciones:

- Generar declaracion jurada oficial por mesa y jornada.
- Mostrar lista de firmantes obligados y estado de firma.
- Registrar excepciones justificadas por ausencia, negativa o impedimento.
- Bloquear cierre operativo hasta completar el requisito legal.

### 2.7 Modulo de conectividad y fiabilidad

Funciones:

- Mostrar mesas en modo online/offline y backlog de sincronizacion.
- Identificar tipo de conectividad disponible (fija, movil, satelital).
- Mostrar score de fiabilidad de mesa del 1 al 10 y factores que lo explican.
- Priorizar soporte y supervision sobre mesas con bajo score o reconexion pendiente.

## 3. Modelo de permisos (RBAC + ABAC)

Reglas clave:

- Administracion nacional: configura catalogos globales y politicas.
- Administracion regional/local: configura mesas y asignaciones dentro de su ambito.
- Miembro de mesa: opera unicamente su mesa asignada.
- Suplente: opera solo cuando el sistema registra su activacion por ausencia o impedimento.
- Elector ad hoc: opera solo tras designacion excepcional auditada y por la jornada actual.
- Fiscalizadores/personeros: acceso de observacion y validacion segun normativa.
- Elector: acceso de solo lectura a apertura de mesa e incidencias publicas.

Atributos de autorizacion:

- mesa_id
- ubigeo
- jornada_id
- role_type
- ventana horaria
- estado de mesa

## 4. Cadena de responsabilidad audit-first

Toda accion relevante del panel genera evento inmutable con:

- actor_id
- role_type
- action
- before_state
- after_state
- reason_code
- timestamp
- device_id
- signature (cuando aplique)

Acciones criticas auditables:

- Crear/editar mesa.
- Asignar/remover miembro de mesa.
- Activar suplente o designar elector ad hoc.
- Asignar fiscalizador/personero.
- Crear/editar/congelar cedula.
- Apertura/cierre de jornada por mesa.
- Generar y firmar declaracion jurada de cierre.

## 5. Flujo de jornada para miembros de mesa

1. Registro de asistencia de titulares y suplentes.
2. Activacion de suplentes o designacion de elector ad hoc si faltan miembros.
3. Login en navegador con identidad verificada.
4. Verificacion de asignacion o activacion formal para la mesa y dispositivo permitido.
5. Carga de cedula congelada vigente.
6. Registro digital guiado de resultados del acta (no del voto individual).
7. Validacion y multi-firma.
8. Impresion de acta.
9. Firma fisica y re-subida de acta firmada.
10. Captura de evidencias de identidad segun politica.
11. Publicacion y replicacion a validadores.
12. Posibilidad de reportar incidencias con descripcion y foto.
13. Firma de declaracion jurada de cierre por todos los actores obligados.
14. Si no hay internet, continuar offline y sincronizar al recuperar conectividad.

## 5.1 Flujo de reporte de incidencia

1. Actor autorizado (miembro/personero) abre formulario de incidencia.
2. Ingresa descripcion del suceso.
3. Adjunta foto obligatoria.
4. Sistema valida permisos y pertenencia a mesa.
5. Sistema registra incidencia y publica resumen en portal ciudadano.

## 5.2 Flujo de consulta ciudadana

1. Elector consulta estado de apertura de su mesa por colegio/local.
2. Elector consulta incidencias publicadas de su mesa.
3. Elector visualiza estado de atencion (reportada, en revision, resuelta).

## 5.4 Monitoreo administrativo de fiabilidad

1. El panel calcula y muestra score de mesa del 1 al 10.
2. El panel explica factores: incidencias, correcciones, sincronizacion, evidencias y validaciones.
3. Mesas con score bajo se resaltan para soporte, auditoria o investigacion.

## 5.3 Flujo de declaracion jurada final

1. El sistema presenta el texto oficial de declaracion jurada.
2. Cada miembro de mesa, personero y fiscalizador firma digitalmente.
3. El panel muestra firmas pendientes, completadas y excepciones registradas.
4. El cierre de mesa solo concluye cuando el documento queda completo u observado con causal valida.

## 6. Requisitos web multi-dispositivo

- Interfaz responsive para celular, tablet, laptop y desktop.
- PWA con capacidades offline-first.
- Sin dependencias de hardware propietario para operar.
- Performance aceptable en redes de baja calidad.

## 7. Controles antifraude especificos del panel

- Doble aprobacion para cambios criticos de mesa/cedula.
- Congelamiento de configuracion previo a jornada.
- Alertas por altas masivas fuera de ventana autorizada.
- Alertas por cambios recurrentes de asignacion en la misma mesa.
- Auditoria de permisos denegados (intentos no autorizados).

## 8. KPIs del modulo de administracion

- Porcentaje de mesas configuradas y validadas antes de jornada.
- Tiempo medio de asignacion y validacion de miembros por mesa.
- Numero de cambios de cedula posteriores al cierre (objetivo: 0).
- Numero de acciones criticas sin evidencia completa (objetivo: 0).
- Porcentaje de logins de mesa exitosos en primer intento.
- Tiempo medio de publicacion de incidencia en portal ciudadano.
- Porcentaje de incidencias con evidencia completa (descripcion + foto).
- Porcentaje de mesas con declaracion jurada completa al cierre.
- Tiempo medio adicional de cierre por recoleccion de firmas finales.
- Porcentaje de mesas sincronizadas antes del umbral tras reconexion.
- Distribucion de score de fiabilidad por region/local/mesa.
- Porcentaje de mesas que requirieron suplencia o designacion ad hoc.
- Tiempo medio para completar quorum operativo tras inasistencia.
