import pytest

from restdoctor.utils.permissions import get_permission_classes_from_map
from tests.test_unit.stubs import (
    permission_classes_map_with_default, permission_classes_map_no_default,
    PermissionC, PermissionB, PermissionA,
)

@pytest.mark.parametrize(
    'permission_classes_map,action,default,expected',
    (
        (permission_classes_map_with_default, 'retrieve', [PermissionC], [PermissionB]),
        (permission_classes_map_with_default, 'list', [PermissionC], [PermissionA]),
        (permission_classes_map_no_default, 'retrieve', [PermissionC], [PermissionB]),
        (permission_classes_map_no_default, 'list', [PermissionC], [PermissionC]),
    ),
)
def test_get_permission_classes_from_map(permission_classes_map, action, default, expected):
    permission_classes = get_permission_classes_from_map(action, permission_classes_map, default)

    assert permission_classes == expected
