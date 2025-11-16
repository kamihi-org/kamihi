"""
User view module for Kamihi web application.

License:
    MIT

"""

import inspect

from kamihi.db import BaseUser

from .base_view import BaseView

base_fields = [BaseUser.is_admin, BaseUser.roles, BaseUser.permissions, BaseUser.jobs]


class UserView(BaseView):
    """UserView is a custom view for managing users in the admin interface."""

    fields = [
        a
        for a, _ in inspect.getmembers(BaseUser.cls(), inspect.isdatadescriptor)
        if not a.startswith("_") and a != "id" and a not in [f.key for f in base_fields]
    ] + base_fields
    exclude_fields_from_list = [BaseUser.permissions, BaseUser.jobs]
    exclude_fields_from_create = [BaseUser.permissions, BaseUser.jobs]
