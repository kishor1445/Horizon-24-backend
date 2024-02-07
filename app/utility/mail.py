import os
import io
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


async def send(
    email_ids: list[str],
    subject: str,
    html_body: str,
    attachments: list[io.BytesIO] | None = None,
    mailing_list: bool = False,
    unsubscribe_url: str = "",
) -> None:
    """
    sends mail to those email_ids
    """
    smtp = aiosmtplib.SMTP(
        hostname=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
        port=int(os.getenv("MAIL_PORT", 587)),
        use_tls=False,
        username=os.environ["MAIL_USER"],
        password=os.environ["MAIL_PASS"],
    )
    async with smtp:
        for email_id in email_ids:
            msg = MIMEMultipart()
            msg["From"] = os.getenv("MAIL_USER", "")
            msg["To"] = email_id
            msg["Subject"] = subject
            if mailing_list:
                msg.add_header("List-Unsubscribe", unsubscribe_url)
            msg.attach(MIMEText(html_body, "html"))
            if attachments:
                for attachment in attachments:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.getvalue())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename=horizon24.gif'
                    )
                    msg.attach(part)
            await smtp.sendmail(os.environ["MAIL_USER"], email_id, msg.as_string())


def event_reg_mail(event, reg_data) -> str:
    return f"""
    <DOCTYPE html>
    <html>
    <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Horizon Event | ACM-SIST</title>
    <body style="font-family: Arial, sans-serif; background-color: black;">
    <div style="max-width: 600px; margin: 20px auto; padding: 20px; border: 1px solid #ccc; border-radius: 10px; color: white;">
        <div style="text-align: center;">
            <img src="{os.environ['DOMAIN']}/static/Images/horizon24.gif" alt="horizon24 logo" width="300", height="100" /> 
        </div>
        <p>Your Payment for this event is under verification. You can check the status of your payment in our website</p>
        <h2 style="text-align: center;">{event['name']}</h2>
        <br />
        <p>{event['description']}</p>
        <br />
        <p><b>Venue</b>: {event["venue"]}</p>
        <p><b>Start</b>: {event["start"].strftime('%d-%m-%Y @ %I:%M %p')}</p>
        <p><b>End</b>: {event["end"].strftime('%d-%m-%Y @ %I:%M %p')}</p>
        <p><b>Transaction ID</b>: {reg_data["transaction_id"]}</p>
        <br />
        <div style="text-align: center; margin: 10px;">
            <a href="{event["whatsapp_group_link"]}" style="background-color: #25D366; color: white; padding: 5px; text-decoration: none;">Join WhatsApp</a>
        </div>
        <br />
        <p>Thankyou for Joining Us, {reg_data['name']}<br />
        We hope you enjoy Horizon'24</p>
        <p>Good Luck, ACM-SIST</p>
    </div>
    </body>
    </html>
    """


def payment_verified_mail(reg_data: dict, event: dict):
    return f"""
    <DOCTYPE html>
    <html>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Payment Verified | Horizon'24</title>
    <body style="font-family: Arial, sans-serif; background-color: black;">
    <div style="max-width: 600px; margin: 20px auto; padding: 20px; border: 1px solid #ccc; border-radius: 10px; color: white;">
        <div style="text-align: center;">
            <img src="{os.environ['DOMAIN']}/static/Images/horizon24.gif" alt="horizon24 logo" width="300", height="100" /> 
        </div>
        <p>Your Payment for this event is verification. QR Code for attendance is attacked in this email</p>
        <h2 style="text-align: center;">{event['name']}</h2>
        <br />
        <p>{event['description']}</p>
        <br />
        <p><b>Venue</b>: {event["venue"]}</p>
        <p><b>Start</b>: {event["start"].strftime('%d-%m-%Y @ %I:%M %p')}</p>
        <p><b>End</b>: {event["end"].strftime('%d-%m-%Y @ %I:%M %p')}</p>
        <p><b>Transaction ID</b>: {reg_data["transaction_id"]}</p>
        <br />
        <div style="text-align: center; margin: 10px;">
            <a href="{event["whatsapp_group_link"]}" style="background-color: #25D366; color: white; padding: 5px; text-decoration: none;">Join WhatsApp</a>
        </div>
        <br />
        <p>Thankyou for Joining Us, {reg_data['name']}<br />
        We hope you enjoy Horizon'24</p>
        <p>Good Luck, ACM-SIST</p>
    </div>
    </body>
    </html>
    """
