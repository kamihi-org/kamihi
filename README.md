<div align="center">
  <img src="https://api.iconify.design/flowbite:paper-plane-solid.svg?color=%231520A6" width="200" height="200">
  <h1>Kamihi</h1>
  <p>Python framework for rapid Telegram bot development and management</p>
    <a href="https://app.deepsource.com/gh/kamihi-dev/kamihi/" target="_blank"><img alt="DeepSource" title="DeepSource" src="https://app.deepsource.com/gh/kamihi-dev/kamihi.svg/?label=code+coverage&show_trend=false&token=XJwx56oI7k7Bm23vhsstts9q"/></a>
</div>

> This project is currently in the early stages of development. Expect frequent changes and updates as we work towards a stable release. Your feedback and contributions are welcome!

## TL;DR

Install with:
```sh
uv add kamihi # or pip install kamihi
```

Create a bot with:
```python
from kamihi import bot

bot.settings.token = "123456789:ABC-DEF1234ghIkl-zyx57W2P0s"

@bot.action
async def start():
    return "Hello! I'm your friendly bot. How can I help you today?"

bot.start()
```

Execute the bot with:
```
python your_script.py
```

## Documentation

The documentation is available at [kamihi-dev.github.io/kamihi](https://kamihi-dev.github.io/kamihi/). It includes a comprehensive guide to using Kamihi, including installation instructions, usage examples, and API references.

## Contributing

We welcome contributions to Kamihi! If you have an idea for a new feature, bug fix, or improvement, please open an 
issue or submit a pull request. For more information on how to contribute, check out [this page](https://kamihi-dev.github.io/kamihi/dev/) on the docs.

## License

This project is licensed under the MIT License. See the [LICENSE.md](LICENSE.md) file for more information.
