This guide shows how to extend and customize the user model of the framework. You can do this if you need to store more data about your users than just their Telegram ID and their admin status.

## Prerequisites

- A Kamihi application
- Basic understanding of how MongoDB works

## Extending the User class

You can import the base user class into your code and create a subclass extending it. For the framework to actually use this model, you also have to decorate it with `@bot.user_class`. Thus:

```python
from kamihi import bot, BaseUser
from mongoengine import StringField


@bot.user_class
class User(BaseUser):
    name: str = StringField()
```

The user model (and every other model in the framework) is defined using MongoEngine, and you can add any of the [fields supported by it](https://docs.mongoengine.org/guide/defining-documents.html#fields).

