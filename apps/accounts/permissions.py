from typing import Iterable

from rest_framework import permissions


class RolePermission(permissions.BasePermission):
    """Permission that checks whether the user has at least one required role.

    Views should set `required_roles = ["admin", "staff"]` on the view class.
    Roles are mapped against `is_superuser` and `is_staff` for now. Extend for groups/roles later.
    """

    def has_permission(self, request, view) -> bool:
        required = getattr(view, "required_roles", None)
        if not required:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        for role in self._normalize(required):
            if role == "admin" and request.user.is_superuser:
                return True
            if role == "staff" and request.user.is_staff:
                return True
        return False

    @staticmethod
    def _normalize(roles: Iterable[str]) -> Iterable[str]:
        return [str(r).lower() for r in roles]
