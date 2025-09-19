"""
Commands for Kamihi CLI.

License:
    MIT

"""

from .action import app as action_app
from .db import app as db_app
from .init import app as init_app
from .run import app as run_app
from .user import app as user_app
from .version import app as version_app
from .permission import app as permission_app

__all__ = ["version_app", "action_app", "init_app", "run_app", "user_app", "db_app", "permission_app"]
