import requests
from datetime import datetime


class TelegramClient:
    def __init__(self):
        self.MAHDI = "667988654"
        self.BASE = 'https://api.telegram.org/bot'
        self.TOKEN = "1282447806:AAH31HS92tzlBskrW2LNKdYDwIYrF-vxdg0"
        self.send_message("Hello from ***NEBIX***.\n\n"
                          "Telegram bot initialized.\n"
                          "Stating trading algo.")

    def send_message(self, message):
        """Sends a message to an specific user"""
        req = self.BASE + self.TOKEN + '/sendMessage?chat_id=' + \
              self.MAHDI + '&parse_mode=Markdown&text=' + message + \
              "\n``` " + str(datetime.today()) + " ```"
        try:
            response = requests.get(req)
        except Exception as ex:
            print("Error sending telegram notification:", ex)

    def update(self):
        """Gets the recent unread chats"""
        req = self.BASE + self.TOKEN + '/getUpdates'
        res = requests.get(req)
        print(res.text)
