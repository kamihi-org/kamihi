"""
Utility to create a bot with the BotFather and retrieve its token.

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


while True:
    BOT_NAME = uuid.uuid4().hex[:10]  # Generate a random bot name
    BOT_USER_NAME = BOT_NAME + "_bot"
    if not BOT_NAME[0].isnumeric():
        break


@client.on(events.NewMessage)
async def message_handler(event):
    if "Please choose a name for your bot" in event.raw_text:
        await event.reply(BOT_NAME)
    elif "choose a username for your bot" in event.raw_text:
        await event.reply(BOT_USER_NAME)
    elif "Done! Congratulations on your new bot" in event.raw_text:
        pattern = r"\d+:[a-zA-Z0-9_-]+"
        match = re.search(pattern, event.raw_text)
        if match:
            token = match.group(0)
            print(json.dumps({"name": BOT_NAME, "username": BOT_USER_NAME, "token": token}))
        else:
            raise ValueError("Token not found in the response.")
        await client.disconnect()
    elif "Sorry, this username is invalid." in event.raw_text:
        print("Username is invalid, please try again with a different username.")
        await client.disconnect()


async def main():
    await client.send_message("botfather", "/newbot")


with client:
    client.loop.run_until_complete(main())
    client.run_until_disconnected()
