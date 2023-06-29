from restdoctor.rest_framework.schema.utils import get_app_prefix


def test__get_app_prefix__root():
    module_path = 'insurance.further.path'
    expected_result = 'insurance'

    result = get_app_prefix(module_path=module_path)

    assert result == expected_result


def test__get_app_prefix__folder():
    module_path = 'apps.insurance.further.path'
    expected_result = 'apps_insurance'

    result = get_app_prefix(module_path=module_path)

    assert result == expected_result