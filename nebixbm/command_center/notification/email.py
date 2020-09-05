import smtplib
import ssl
from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase

from nebixbm.log.logger import create_logger, get_file_name


class EmailSender:
    """Class to send email to address"""

    def __init__(self, sender_email, password, smtp_host, smtps_port=465):
        """Initializes EmailSender"""
        self._email = sender_email
        self._password = password
        self._smtp_host = smtp_host
        self._smtps_port = smtps_port
        filename = get_file_name("EmailSender", None)
        self.logger, self.log_filepath = create_logger(filename, filename)

    def send_email(
        self,
        target_email,
        subject, text,
        html=None,
        filenames: list = None,
    ) -> bool:
        """Sends an email to target email"""
        if None in (target_email, subject, text):
            self.logger.error("Failed to send email: init with None")
            return False
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self._email
        message["To"] = target_email
        part1 = MIMEText(text, "plain")
        message.attach(part1)
        if html:
            part2 = MIMEText(html, "html")
            message.attach(part2)
        if filenames:
            try:
                for fn in filenames:
                    with open(fn, "rb") as f:
                        part3 = MIMEBase("application", "octet_stream")
                        part3.set_payload(f.read())
                    encoders.encode_base64(part3)
                    part3.add_header(
                        "Content-Disposition",
                        f"attachment; filename= {f.name}",
                    )
                    message.attach(part3)
            except Exception as err:
                self.logger.error(f"Failed encode attachment files: {err}")
                return False
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(
                self._smtp_host,
                self._smtps_port,
                context=context,
            ) as server:
                server.login(self._email, self._password)
                server.sendmail(
                    self._email, target_email, message.as_string()
                )
        except Exception as err:
            self.logger.exception(f"Failed to send email: {err}")
            return False
        else:
            self.logger.info("Successfully sent email")
            return True
