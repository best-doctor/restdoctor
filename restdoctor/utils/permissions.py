from __future__ import annotations
import typing


if typing.TYPE_CHECKING:
    from rest_framework.permissions import BasePermission
    PermissionClasses = typing.List[BasePermission]
    PermissionClassesMap = typing.Dict[str, PermissionClasses]


def get_permission_classes_from_map(
    action: str,
    permission_classes_map: PermissionClassesMap,
    default_permission_classes: PermissionClasses,
) -> PermissionClasses:
    permission_classes = permission_classes_map.get('default', default_permission_classes)
    return permission_classes_map.get(action, permission_classes)
