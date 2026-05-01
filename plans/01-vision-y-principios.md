# 01. Vision y principios

## 1. Vision del sistema

Disenar un sistema electoral digital que reduzca el error operativo en mesa, acelere la publicacion de resultados y habilite auditoria publica distribuida en tiempo real.

### Objetivos medibles

- Publicacion de acta firmada en menos de 60 segundos desde su envio.
- Contabilizacion de acta finalizada en proyeccion oficial en menos de 5 segundos p95.
- Trazabilidad completa de cada cambio de acta (cadena de versiones).
- Verificacion criptografica de firma y contenido en todos los nodos validadores.
- Tasa de inconsistencias detectadas antes de consolidacion mayor al 99.9%.
- Consolidacion nacional preliminar mayor al 95% de actas en menos de 4 horas.
- Tiempo maximo para abrir expediente de incidente critico menor a 10 minutos.
- Disponibilidad de plataforma mayor a 99.99% durante la ventana critica electoral.
- Tiempo de sincronizacion desde recuperacion de internet menor a 30 segundos p95.
- Calificacion de fiabilidad por mesa calculada y publicada internamente para el 100% de mesas.

## 2. Filosofia dual de diseno

### Enfoque infraestructura (tipo Gates)

- Seguridad por defecto y por diseno.
- Protocolos claros y versionados.
- Datos consistentes y verificables.
- Arquitectura resiliente y escalable.

### Enfoque experiencia operativa (tipo Jobs)

- Flujo guiado paso a paso sin ambiguedad.
- Validaciones tempranas para bloquear errores.
- Carga cognitiva minima para miembros de mesa.
- Operacion intuitiva incluso con conectividad intermitente.

## 3. Principios no negociables

1. No sobrescribir: todos los cambios son append-only.
2. Todo acta requiere firmas digitales validas (multi-firma obligatoria).
3. Toda publicacion genera evidencia verificable (hash + QR + imagen).
4. El backend no es fuente unica de verdad: validadores externos recalculan y auditan.
5. El sistema debe operar en modo degradado seguro (offline-first en cliente, cola en backend).
6. Toda accion relevante debe quedar firmada, fechada y atribuible a un responsable.
7. Toda etapa debe tener validaciones automaticas + control humano de doble verificacion.
8. La plataforma debe escalar horizontalmente sin dependencia de un nodo unico critico.
9. Toda acta finalizada debe contabilizarse y propagarse de inmediato.
10. La operacion de mesa no puede depender de conectividad continua para continuar.
11. Toda mesa debe contar con una metrica objetiva de fiabilidad de resultados.

## 4.1 Cadena de responsabilidad ante fraude

Cada acta debe responder 3 preguntas sin ambiguedad:

1. Quien hizo que accion y con que identidad verificada.
2. En que momento exacto ocurrio (timestamp confiable y sincronizado).
3. Que evidencia tecnica y fisica respalda esa accion.

La cadena de responsabilidad se sustenta en:

- No repudio criptografico (firma digital por actor).
- Cadena hash inmutable de eventos.
- Evidencia de imagen y comprobante fisico vinculados al hash de acta.
- Registro de aprobadores y testigos operativos por transaccion critica.

## 4. Metas de calidad del producto

- Usabilidad: flujo de captura completado sin asistencia externa en mesa.
- Confiabilidad: cero perdida de actas por fallas de red o reinicios.
- Auditabilidad: cualquier tercero puede reconstruir historia de una acta.
- Transparencia: endpoints publicos de auditoria con datos anonimizados.

## 4.2 Metas operativas de jornada electoral

- Disponibilidad de API operativa: mayor a 99.99% en ventana electoral.
- Disponibilidad de portal ciudadano y paneles operativos: mayor a 99.95% en ventana electoral.
- Tiempo de propagacion a validadores p95 menor a 15 segundos.
- Error de procesamiento por acta menor a 0.1% (excluye datos de entrada invalidos).
- Tiempo de deteccion de anomalia critica menor a 2 minutos.
- Tiempo de contencion inicial de incidente mayor menor a 15 minutos.
- Tiempo de contabilizacion desde acta finalizada a agregado nacional p95 menor a 10 segundos.
- Tiempo de sincronizacion de cola offline tras reconexion p95 menor a 30 segundos.
- Porcentaje de mesas con score de fiabilidad >= 8 mayor al 95%, salvo mesas observadas.

## 5. Definiciones clave

- Acta: unidad principal de resultados por mesa.
- Version de acta: snapshot inmutable de una modificacion aprobada.
- Firma: evidencia criptografica de autorizacion por miembro de mesa.
- Validador: nodo externo de solo lectura que replica y verifica.
- Ledger de auditoria: cadena hash de eventos del sistema.

## 6. Roles operativos y alcance

Roles principales del sistema:

- Administrador electoral nacional/regional.
- Miembro de mesa titular (presidente, secretario, tercer miembro).
- Miembro de mesa suplente.
- Elector designado ad hoc para asumir mesa por inasistencia.
- Fiscalizador institucional (ONPE/JNE).
- Personero de organizacion politica.
- Validador externo/auditor.

Regla de oro de autorizacion:

- El miembro de mesa solo puede operar su mesa asignada.
- El suplente solo adquiere permisos operativos cuando reemplaza formalmente a un titular ausente.
- El elector ad hoc solo adquiere permisos de mesa tras designacion formal, validacion de identidad y registro de causal.
- Fiscalizadores y personeros tienen permisos de observacion/validacion segun norma.
- Toda accion de configuracion o de jornada queda registrada con actor, rol, mesa y evidencia.

## 7. Experiencia multi-dispositivo

El sistema debe funcionar en navegador moderno y resoluciones moviles/tablet/desktop.

Criterios minimos:

- PWA responsive y accesible.
- Flujo tolerante a latencia y cortes de red.
- Controles tactiles para captura en mesa.
- Modo de alto contraste y soporte de accesibilidad.
