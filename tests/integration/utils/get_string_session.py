"""
TODO: one-line module description.

TODO: Additional details about the module, its purpose, and any necessary
background information. Explain what functions or classes are included.

License:
    MIT

Examples:
    [Examples of how to use the module/classes/functions]

Attributes:
    [List any relevant module-level attributes with types and descriptions]
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
