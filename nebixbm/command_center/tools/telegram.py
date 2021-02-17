import requests
import os
from datetime import datetime

from nebixbm.log.logger import create_logger, get_file_name


class TelegramClient:
    def __init__(self, header=None):
        filename = get_file_name("TelegramNotifier", None)
        self.logger, self.log_filepath = create_logger(filename, filename)
        self.BASE = 'https://api.telegram.org/bot'
        self.USER_ID = os.getenv("NOTIFY_TELEGRAM_ID")
        self.TOKEN = os.getenv("NOTIFY_TELEGRAM_TOKEN")
        self.header = header
        self.send_message("Telegram bot initialized.\n"
                          "Stating trading algo.")
        self.logger.info("Successfully initialized telegram bot.")

    def send_message(self, message):
        """Sends a message to an specific user"""
        req = self.BASE + self.TOKEN + f"/sendMessage?chat_id={self.USER_ID}"\
                                       "&parse_mode=Markdown&text=\n" \
                                       f"```\n{self.header}```\n\n" \
                                       f"{message}\n\n" \
                                       f"```\n{str(datetime.today())}```"
        self.logger.info("Successfully sent telegram notification.")
        try:
            self.logger.debug(str(req))
            res = requests.get(req)
            self.logger.debug(str(res))
        except Exception as ex:
            pass
            self.logger.error("Error sending telegram notification:", ex)

    # def update(self):
    #     """Gets the recent unread chats"""
    #     req = self.BASE + self.TOKEN + '/getUpdates'
    #     res = requests.get(req)
    #     print(res.text)
