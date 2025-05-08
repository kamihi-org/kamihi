"""
Custom views for the admin interface.

License:
    MIT

"""

from starlette_admin.contrib.mongoengine import ModelView


class NoClsView(ModelView):
    """NoClsView hides the "_cls" field from the admin interface."""

    exclude_fields_from_list = ["_cls"]
    exclude_fields_from_detail = ["_cls"]
    exclude_fields_from_create = ["_cls"]
    exclude_fields_from_edit = ["_cls"]
