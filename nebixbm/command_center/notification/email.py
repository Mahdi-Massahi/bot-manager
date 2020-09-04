import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

    def send_email(self, target_email, subject, text, html=None) -> bool:
        """Sends email to target email"""
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
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(
                self._smtp_host, self._smtps_port, context=context,
            ) as server:
                server.login(self._email, self._password)
                server.sendmail(self._email, target_email, message.as_string())
        except Exception as err:
            self.logger.error(f"Failed to send email: {err}")
            return False
        else:
            self.logger.info("Successfully sent email")
            return True
