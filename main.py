import asyncio, os
from typing import Type
from dotenv import load_dotenv
from src.client import MPPClient, CustomBotType

BOT_CLASS = MPPClient


def main(token: str, name: str, color: str, channel: str, bot_class: Type[CustomBotType] = MPPClient):
    bot = bot_class(token=token, name=name, color=color, channel=channel, instance_name="mpp_bot")
    with bot:
        asyncio.run(bot.run())


if __name__ == "__main__":
    load_dotenv()
    main(os.getenv("TOKEN"), os.getenv("NAME"), os.getenv("COLOR"), os.getenv("CHANNEL"), bot_class=BOT_CLASS)
