"""
Kamihi is a Python framework for creating Telegram bots.

This is a long description. It should be multiple lines and give an overview
of the package functionality. It should also mention the key features and
advantages of the package.

License:
    MIT

Attributes:
    __version__ (str): The version of the package.

"""

__version__ = "0.1.1"

from kamihi.bot import Bot as _Bot

bot = _Bot()

bot.start()
