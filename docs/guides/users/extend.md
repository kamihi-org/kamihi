This guide shows how to extend and customize the user model of the framework. You can do this if you need to store more data about your users than just their Telegram ID and their admin status.

## Prerequisites

- A Kamihi application
- Basic understanding of how SQLAlchemy works

## Extending the User class

The base project defines a `User` class in `kamihi/models/user.py` that extends from `kamihi.BaseUser`. This class can be extended to add more attributes. For example, to add a `name` attribute, you can modify the file like this:

```python
from kamihi.db import BaseUser
from sqlalchemy import Column, String

class User(BaseUser):
    __table_args__ = {'extend_existing': True}
    name = Column(String, nullable=True)
```

!!! warning
    Be sure to update the database schema when modifying the model. To obtain more information on how to do this, refer to the [database migrations guide](../db/migrations.md).

## Adding users with extended attributes using the CLI

To add users with an extended `User` class, all the extra attributes need to be sent as a JSON string with the `--data` option:

```shell
> kamihi user add 123456789 --data '{"name": "John Doe"}'
```
