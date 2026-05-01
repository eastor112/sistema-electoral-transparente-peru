# 05. Flujo operativo completo y estados

## 1. Flujo extremo a extremo

### 1.0 Pre-jornada administrativa

1. Administracion configura mesas por localidad/ubigeo.
2. Se registran miembros de mesa y suplentes.
3. Se registran fiscalizadores ONPE/JNE y personeros habilitados.
4. Se configura y congela cedula por tipo de eleccion.
5. Se genera acta de configuracion firmada por responsables administrativos.

### 1.1 Inicio

1. Se registra asistencia de miembros titulares y suplentes.
2. Si faltan titulares, se activa reemplazo por suplente segun politica.
3. Si aun no hay quorum suficiente, se designa elector ad hoc con evidencia y autorizacion registradas.
4. Operador se autentica (DNI + biometria).
5. Se inicia sesion segura por mesa.
6. Cliente genera par de claves efimero para firma.
7. Sistema valida que el actor este asignado o activado formalmente para esa mesa y jornada.
8. Se registra evento oficial de apertura de mesa en el sistema.

### 1.1.1 Consulta ciudadana de apertura

1. El elector ingresa al portal ciudadano en navegador.
2. Selecciona su colegio/local y mesa.
3. El sistema muestra estado de apertura y hora oficial registrada.

### 1.2 Captura guiada

1. Ingreso de votos por categoria.
2. Validaciones automaticas en tiempo real.
3. Bloqueo de avance si hay inconsistencias.

### 1.2.1 Operacion offline

1. Si no hay internet, el cliente entra en modo offline seguro.
2. Todos los eventos se guardan localmente en cola cifrada y ordenada.
3. El operador continua el flujo normal sin depender de conectividad.
4. Cuando reaparece internet, el cliente sincroniza inmediatamente.

### 1.3 Validacion humana

1. Miembro A ingresa resultados.
2. Miembro B verifica visualmente.
3. Miembro C confirma resumen final.

### 1.4 Firma digital

1. Cliente canonicaliza payload.
2. Cada miembro firma hash de la version.
3. Backend valida firma y unicidad de firmante.

### 1.5 Publicacion y distribucion

1. Backend marca version como PUBLICADA.
2. Persiste de forma durable el acta finalizada.
3. La contabiliza inmediatamente en proyecciones y agregados oficiales.
4. Emite evento a bus de validadores.
5. Actualiza feed de auditoria publica (< 60 s).
6. Recalcula la fiabilidad de la mesa segun eventos y validaciones disponibles.

### 1.6 Evidencia fisica y digital

1. Se imprime comprobante con hash, QR e ID de acta.
2. Firma fisica sobre comprobante.
3. Captura de imagen del acta/comprobante.
4. Subida final y verificacion de hash de imagen.
5. Captura de evidencia de identidad (rostro) de miembros/validadores segun norma.

### 1.7 Reporte de incidencias en mesa

1. Miembro de mesa o personero reporta incidencia de su mesa.
2. Debe ingresar descripcion del suceso y adjuntar foto obligatoria.
3. El sistema registra severidad inicial y cadena de custodia.
4. El reporte se publica en vista ciudadana con resumen y estado.

### 1.8 Declaracion jurada de cierre

1. Al finalizar la operacion, el sistema genera la declaracion jurada oficial de la mesa.
2. Firman todos los miembros de mesa, personeros y fiscalizadores presentes o asignados segun politica.
3. El texto declara actuacion en honor a la verdad, respeto al derecho democratico y allanamiento a investigacion ante fraude.
4. Cada firma queda vinculada a identidad, rol, dispositivo, timestamp y hash del documento.
5. Sin este paso, la mesa no puede pasar a cierre definitivo salvo excepcion formal registrada.

## 2. Maquina de estados del acta

Estados:

- `ABIERTA`
- `EN_VALIDACION`
- `FIRMADA`
- `PUBLICADA`
- `CORREGIDA`
- `BLOQUEADA`

Transiciones validas:

- `ABIERTA -> EN_VALIDACION`
- `EN_VALIDACION -> FIRMADA`
- `FIRMADA -> PUBLICADA`
- `PUBLICADA -> CORREGIDA` (creando nueva version)
- `* -> BLOQUEADA` (por regla de seguridad/incidente)

## 3. Reglas de transicion

- Solo `EN_VALIDACION` permite agregar firmas.
- `FIRMADA` requiere umbral minimo de firmas.
- `PUBLICADA` es inmutable para esa version.
- `CORREGIDA` exige motivo y evidencia adicional.

Reglas adicionales:

- Toda transicion crea evento de custodia firmado por el actor responsable.
- Cambios de alto impacto exigen doble control humano (principio four-eyes).
- Si riesgo >= umbral critico, la acta pasa a `BLOQUEADA` hasta revision.
- Toda excepcion de flujo requiere `reason_code` y aprobacion trazable.
- Toda captura de votos requiere cedula congelada de la eleccion vigente.

## 3.1 Validacion durante todo el proceso

Compuertas obligatorias por etapa:

1. Captura: validacion numerica, rangos y coherencia entre campos.
2. Pre-firma: resumen inmutable mostrado a los 3 miembros.
3. Firma: verificacion criptografica y anti-replay por cada firmante.
4. Publicacion: umbral de firmas + score de riesgo aceptable.
5. Post-publicacion: contabilizacion inmediata, conciliacion con validadores y evidencia imagen.

Si falla una compuerta, el flujo se detiene y abre incidente tecnico-operativo.

## 4. Casos de error y recuperacion

### 4.1 Sin conectividad

- Cliente guarda en cola local cifrada.
- Reintento automatico con backoff.
- Al reconectar, envia en orden con idempotency keys.
- Si detecta conectividad satelital disponible, la usa como canal valido de sincronizacion.
- Prioriza sincronizar cierre de acta y evidencias criticas antes que eventos secundarios.

### 4.2 Firma invalida

- Se rechaza firma sin alterar estado.
- Se registra evento de seguridad.
- Se notifica al operador en UI con causa resumida.

### 4.3 Conflicto de version

- Si llega firma para version antigua, rechazar con codigo de conflicto.
- Forzar sincronizacion del cliente con version activa.

### 4.4 Sospecha de fraude en mesa

- Activar estado `BLOQUEADA` para acta/version implicada.
- Congelar nuevas firmas/publicacion hasta analisis.
- Generar expediente con eventos de custodia, logs y evidencias.
- Escalar a comite tecnico y autoridad electoral segun severidad.

### 4.5 Falta de firma de declaracion jurada

- Mantener cierre en estado observado o parcial.
- Exigir causal documentada de ausencia, negativa o impedimento.
- Registrar incidente de custodia si un actor obligado se rehusa a firmar.

### 4.6 Inasistencia de miembros de mesa

- Registrar ausencia total o parcial de titulares.
- Activar suplentes en orden predefinido cuando corresponda.
- Si no hay suplentes suficientes, registrar designacion de elector ad hoc.
- Recalcular lista de firmantes obligados segun composicion real de mesa.

## 5. Endpoint-state matrix

- `POST /actas` solo en alta inicial.
- `POST /actas/{id}/validar` solo desde ABIERTA.
- `POST /actas/{id}/firmas` solo desde EN_VALIDACION.
- `POST /actas/{id}/publicar` solo desde FIRMADA.
- `POST /actas/{id}/corregir` solo desde PUBLICADA.

Administracion pre-jornada:

- `POST /admin/mesas` y asignaciones solo en ventana pre-jornada.
- `POST /admin/elecciones/{id}/cedula/congelar` requisito para habilitar captura.

Operacion jornada:

- `POST /auth/login-mesa` requiere actor asignado + dispositivo permitido.
- `POST /mesas/{mesa_id}/asistencia` registra asistencia de titulares/suplentes.
- `POST /mesas/{mesa_id}/reemplazos/suplente` activa reemplazo formal.
- `POST /mesas/{mesa_id}/reemplazos/elector-ad-hoc` registra designacion excepcional.
- `POST /actas/{id}/evidencias-identidad` segun politica de control.
- `POST /mesas/{mesa_id}/apertura` registra apertura oficial de mesa.
- `POST /mesas/{mesa_id}/incidencias` requiere descripcion + foto.
- `POST /mesas/{mesa_id}/declaracion-jurada/generar` crea el documento oficial.
- `POST /mesas/{mesa_id}/declaracion-jurada/firmas` registra cada firma obligatoria.

Consulta ciudadana:

- `GET /public/locales/{local_id}/mesas/apertura` muestra estado de apertura por mesa.
- `GET /public/mesas/{mesa_id}/incidencias` muestra incidencias publicadas y estado.

Monitoreo y control:

- `GET /mesas/{mesa_id}/fiabilidad` muestra score y factores.

## 6. Reglas UX/operacion criticas

- No permitir campos libres donde deba existir selector.
- Mostrar resumen y confirmacion antes de firmar.
- Confirmaciones explicitas en acciones irreversibles.
- Feedback inmediato con codigos de error entendibles.
- Reporte de incidencias con formulario corto, guiado y obligatorio (descripcion + foto).
