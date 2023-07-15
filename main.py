import asyncio, os
from typing import Type
from dotenv import load_dotenv
from config import Config, BotType

config = Config()


def main(token: str, name: str, color: str, channel: str, instance_name: str, prefix: str, bot_class: Type[BotType]):
    bot = bot_class(token=token, name=name, color=color, channel=channel, instance_name=instance_name, prefix=prefix)
    with bot:
        asyncio.run(bot.run())


if __name__ == "__main__":
    load_dotenv()
    main(os.getenv("TOKEN"), os.getenv("NAME"), os.getenv("COLOR"), os.getenv("CHANNEL"), os.getenv("INSTANCE"), os.getenv("PREFIX"), config.bot)
