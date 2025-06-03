"""
Utility to delete a bot with the BotFather.

License:
    MIT

"""

import json
import os
import uuid
import re

from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.sessions import StringSession


load_dotenv()
API_ID = int(os.getenv("KAMIHI_TESTING__TG_API_ID"))
API_HASH = os.getenv("KAMIHI_TESTING__TG_API_HASH")
DC_ID = int(os.getenv("KAMIHI_TESTING__TG_DC_ID"))
DC_IP = os.getenv("KAMIHI_TESTING__TG_DC_IP")
SESSION = os.getenv("KAMIHI_TESTING__TG_SESSION")
BOT = json.loads(os.getenv("KAMIHI_TESTING__BOT"))

client = TelegramClient(
    StringSession(SESSION),
    API_ID,
    API_HASH,
    sequential_updates=True,
)
client.session.set_dc(
    DC_ID,
    DC_IP,
    443,
)


@client.on(events.NewMessage)
async def message_handler(event):
    if "Choose a bot to delete." in event.raw_text:
        await event.reply("@" + BOT["username"])
    elif "Send 'Yes, I am totally sure.' to confirm you really want to delete this bot." in event.raw_text:
        await event.reply("Yes, I am totally sure.")
    elif "Done! The bot is gone." in event.raw_text:
        print("Bot deleted successfully.")
        await client.disconnect()


async def main():
    await client.send_message("botfather", "/deletebot")


with client:
    client.loop.run_until_complete(main())
    client.run_until_disconnected()
