import asyncio
import smtplib
from email.message import EmailMessage

import httpx

from election_system.application.ports import EmailSenderPort
from election_system.core.config import settings


class ConsoleEmailSender(EmailSenderPort):
    async def send_email(
        self,
        *,
        to_email: str,
        subject: str,
        text_body: str,
        html_body: str | None = None,
    ) -> None:
        print("=== EMAIL (console provider) ===")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print("Body:")
        print(text_body)
        if html_body:
            print("HTML:")
            print(html_body)
        print("=== END EMAIL ===")


class ResendEmailSender(EmailSenderPort):
    async def send_email(
        self,
        *,
        to_email: str,
        subject: str,
        text_body: str,
        html_body: str | None = None,
    ) -> None:
        if not settings.resend_api_key:
            raise RuntimeError("resend_api_key is required when using resend provider")

        payload: dict[str, object] = {
            "from": settings.email_from,
            "to": [to_email],
            "subject": subject,
            "text": text_body,
        }
        if html_body is not None:
            payload["html"] = html_body

        headers = {
            "Authorization": f"Bearer {settings.resend_api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(settings.resend_api_url, json=payload, headers=headers)
        response.raise_for_status()


class SMTPEmailSender(EmailSenderPort):
    async def send_email(
        self,
        *,
        to_email: str,
        subject: str,
        text_body: str,
        html_body: str | None = None,
    ) -> None:
        message = EmailMessage()
        message["From"] = settings.email_from
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(text_body)
        if html_body is not None:
            message.add_alternative(html_body, subtype="html")

        await asyncio.to_thread(self._send_message_sync, message)

    @staticmethod
    def _send_message_sync(message: EmailMessage) -> None:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
            if settings.smtp_use_tls:
                smtp.starttls()
            if settings.smtp_user:
                smtp.login(settings.smtp_user, settings.smtp_password)
            smtp.send_message(message)


def build_email_sender() -> EmailSenderPort:
    if settings.app_env.lower() in {"dev", "local", "development"}:
        return ConsoleEmailSender()

    provider = settings.email_provider.lower()
    if provider == "console":
        return ConsoleEmailSender()
    if provider == "resend":
        return ResendEmailSender()
    if provider == "smtp":
        return SMTPEmailSender()

    raise RuntimeError(f"Unsupported email_provider: {settings.email_provider}")
