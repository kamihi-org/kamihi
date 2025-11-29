"""
Utility to generate a credential set for Kamihi tests using Telethon.

License:
    MIT

"""
import asyncio
import json

from telethon.sync import TelegramClient
from telethon.sessions import StringSession

from ..fixtures.settings import TestingSettings

async def main(setts: TestingSettings):
    phone_number = input("Phone number (with country code, no spaces): ")

    client = TelegramClient(StringSession(), setts.api_id, setts.api_hash)
    client.session.set_dc(
        setts.dc_id,
        str(setts.dc_ip),
        443,
    )
    await client.connect()
    await client.start(phone=phone_number)

    async with client.conversation("@botfather") as conv:
        await conv.send_message("/start")
        await conv.get_response()
        await conv.send_message("/newbot")
        await conv.get_response()
        bot_name = f"kamihi_{input('Bot number: ')}_bot"
        await conv.send_message(bot_name)
        await conv.get_response()
        await conv.send_message(bot_name)
        response = await conv.get_response()
        token = response.text.split("`")[1]

    me = await client.get_me()

    print(json.dumps({
        "phone_number": phone_number,
        "user_id": me.id,
        "bot_token": token,
        "bot_username": bot_name,
        "session": client.session.save(),
    }, indent=4))

    await client.send_message(bot_name, "/start")
    await client.disconnect()

if __name__ == "__main__":
    setts = TestingSettings()
    asyncio.run(main(setts))
