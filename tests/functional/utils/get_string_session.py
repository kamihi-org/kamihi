"""
Utility to generate a string session for Telegram using Telethon.

This module provides a simple way to create a string session for Telegram,
which is needed for authentication with Telethon so it can be used in
automated functional testing.

License:
    MIT

"""

import os

from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon.sessions import StringSession


load_dotenv()

PHONE_NUMBER = os.getenv("KAMIHI_TESTING__TG_PHONE_NUMBER")
API_ID = int(os.getenv("KAMIHI_TESTING__TG_API_ID"))
API_HASH = os.getenv("KAMIHI_TESTING__TG_API_HASH")
DC_ID = int(os.getenv("KAMIHI_TESTING__TG_DC_ID"))
DC_IP = os.getenv("KAMIHI_TESTING__TG_DC_IP")

client = TelegramClient(StringSession(), API_ID, API_HASH)
client.session.set_dc(
    DC_ID,
    DC_IP,
    443,
)
client.connect()
client.start(phone=PHONE_NUMBER)
print(client.session.save())
