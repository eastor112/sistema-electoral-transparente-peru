# Auth JWT + 2FA (Email/Telegram)

Fecha: 2026-05-02
Estado: completado

## Resumen

Se implemento un sistema de autenticacion basado en JWT con doble factor por codigo OTP, soportando dos canales de entrega para login:

- email
- telegram

Incluye registro, login en dos pasos, refresh token, recuperacion de contrasena y registro de chat id de Telegram para recibir OTP.

## Objetivos cumplidos

- JWT firmado para access token y refresh token.
- Hash de contrasenas con PBKDF2 SHA256 + salt.
- OTP de un solo uso con expiracion e intentos maximos.
- Registro y autenticacion con email + contrasena + OTP.
- Seleccion de canal OTP en login (`email` o `telegram`).
- Recuperacion de contrasena por OTP de email.
- Registro autenticado de `telegram_chat_id` con mensaje de verificacion previo al guardado.
- Proveedores de mensajeria desacoplados por puertos (email/telegram) con modo consola para desarrollo.

## Flujo funcional

### 1) Registro

Endpoint: `POST /api/v1/auth/register`

Campos clave:

- `email`
- `password`
- `full_name` (opcional)
- `telegram_chat_id` (opcional)

### 2) Login (paso 1)

Endpoint: `POST /api/v1/auth/login`

Campos clave:

- `email`
- `password`
- `channel`: `email` o `telegram`

Resultado:

- `challenge_id`
- `expires_at`
- `channel`

### 3) Login (paso 2)

Endpoint: `POST /api/v1/auth/login/verify`

Campos clave:

- `challenge_id`
- `code`

Resultado:

- `access_token`
- `refresh_token`
- `token_type`

### 4) Refresh

Endpoint: `POST /api/v1/auth/refresh`

Campo:

- `refresh_token`

### 5) Recuperacion de contrasena

Paso 1: `POST /api/v1/auth/password-recovery/request`

Paso 2: `POST /api/v1/auth/password-recovery/confirm`

### 6) Registro de chat id Telegram

Endpoint: `POST /api/v1/auth/telegram/register-chat-id`

Requiere:

- token JWT en Authorization Bearer
- body con `telegram_chat_id`

Reglas:

- valida que el usuario autenticado exista y este activo
- valida que el chat id no este asociado a otro usuario
- intenta enviar un mensaje de verificacion al chat
- solo si el envio es exitoso, persiste el chat id

## Modelo de datos y migraciones

Migraciones aplicables:

- `20260502_0001_auth_jwt_otp.py`
- `20260502_0002_add_user_telegram_chat_id.py`

Estructura relevante:

- tabla `users`:
  - `user_id`
  - `email` (unique)
  - `password_hash`
  - `telegram_chat_id` (nullable, unique)
  - metadatos de auditoria basicos (`created_at`, `updated_at`, `last_login_at`)

- tabla `email_otp_challenges`:
  - `challenge_id`
  - `user_id`
  - `purpose` (`LOGIN`, `PASSWORD_RESET`)
  - `code_hash`
  - `attempts`
  - `max_attempts`
  - `expires_at`
  - `consumed_at`

## Configuracion (entorno)

Variables agregadas para la feature:

- `JWT_REFRESH_TOKEN_EXPIRE_MINUTES`
- `PASSWORD_HASH_ITERATIONS`
- `OTP_CODE_LENGTH`
- `OTP_TTL_MINUTES`
- `OTP_MAX_ATTEMPTS`
- `EMAIL_PROVIDER`
- `EMAIL_FROM`
- `RESEND_API_KEY`
- `RESEND_API_URL`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASSWORD`
- `SMTP_USE_TLS`
- `TELEGRAM_PROVIDER`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_API_BASE_URL`

## Proveedores y modo desarrollo

Email:

- `console`
- `resend`
- `smtp`

Telegram:

- `console`
- `bot` (Telegram Bot API)

Comportamiento de desarrollo:

- con `APP_ENV` en `dev`, `local` o `development`, el envio se fuerza a consola para evitar costos.

## Seguridad y controles

- Los codigos OTP se almacenan con hash, no en texto plano.
- Los desafios OTP expiran y se invalidan por uso.
- Se controla maximo de intentos por desafio.
- Se devuelve error controlado cuando el canal solicitado no esta disponible.
- Se exige access token valido para operaciones de perfil (`/auth/me`, registro de chat id).

## Archivos principales tocados

- `src/election_system/api/v1/routes/auth.py`
- `src/election_system/api/dependencies/auth.py`
- `src/election_system/application/services/auth_service.py`
- `src/election_system/application/ports.py`
- `src/election_system/core/security.py`
- `src/election_system/core/config.py`
- `src/election_system/core/exceptions.py`
- `src/election_system/infrastructure/repositories/auth_repository.py`
- `src/election_system/infrastructure/notifications/email_sender.py`
- `src/election_system/infrastructure/notifications/telegram_sender.py`
- `src/election_system/infrastructure/db/models.py`
- `alembic/versions/20260502_0001_auth_jwt_otp.py`
- `alembic/versions/20260502_0002_add_user_telegram_chat_id.py`

## Validacion ejecutada

Se valido con:

- `make lint`
- `make typecheck`
- `make test`

Resultado: sin errores en lint/typecheck y pruebas en verde.
