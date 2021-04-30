import pytest
from django.core.exceptions import ImproperlyConfigured
from rest_framework.fields import Field

from restdoctor.rest_framework.schema import RestDoctorSchema
from tests.stubs.serializers import (
    MyModelWithoutHelpTextsSerializer, WithMethodFieldFirstIncorrectSerializer,
    WithMethodFieldSecondIncorrectSerializer, WithMethodFieldFirstCorrectSerializer,
    WithMethodFieldManyCorrectSerializer, WithMethodFieldOptionalManyCorrectSerializer,
    WithMethodFieldManyIncorrectSerializer, WithMethodFieldOptionalManyIncorrectSerializer,
    WithMethodFieldListFieldCorrectSerializer, WithMethodFieldListFieldIncorrectSerializer,
    WithMethodFieldMultipleChoiceFieldCorrectSerializer,
    WithMethodFieldMultipleChoiceFieldIncorrectSerializer,
)


@pytest.mark.parametrize(
    'field,expected_help_text',
    (
        (Field(), None),
        (Field(help_text='help_text'), 'help_text'),
    ),
)
def test_get_field_description_not_raises_success_case(field, expected_help_text):
    schema = RestDoctorSchema()

    result = schema.get_field_description(field)

    assert result == expected_help_text


def test_get_field_description_strict_fail_case(settings):
    settings.API_STRICT_SCHEMA_VALIDATION = True
    schema = RestDoctorSchema()

    with pytest.raises(ImproperlyConfigured):
        schema.get_field_description(Field())


def test_get_field_description_success_case(settings):
    settings.API_STRICT_SCHEMA_VALIDATION = True
    schema = RestDoctorSchema()

    result = schema.get_field_description(Field(help_text='help_text'))

    assert result == 'help_text'


def test_get_field_description_model_field_not_raises_success_case():
    schema = RestDoctorSchema()

    result = schema.get_field_description(
        MyModelWithoutHelpTextsSerializer().fields['abstract_field'])

    assert result is None


def test_get_field_description_model_field_strict_fail_case(settings):
    settings.API_STRICT_SCHEMA_VALIDATION = True
    schema = RestDoctorSchema()

    with pytest.raises(ImproperlyConfigured):
        schema.get_field_description(MyModelWithoutHelpTextsSerializer().fields['abstract_field'])


def test_get_field_description_model_field_success_case(settings):
    settings.API_STRICT_SCHEMA_VALIDATION = True
    schema = RestDoctorSchema()

    result = schema.get_field_description(MyModelWithoutHelpTextsSerializer().fields['timestamp'])

    assert result == 'Event timestamp'


def test_check_annotations_fail_case_field_not_annotated(settings):
    settings.API_STRICT_SCHEMA_VALIDATION = True
    schema = RestDoctorSchema()

    with pytest.raises(ImproperlyConfigured):
        schema.map_field(WithMethodFieldFirstIncorrectSerializer().fields['data'])


def test_check_annotations_fail_case_method_not_annotated(settings):
    settings.API_STRICT_SCHEMA_VALIDATION = True
    schema = RestDoctorSchema()

    with pytest.raises(ImproperlyConfigured):
        schema.map_field(WithMethodFieldSecondIncorrectSerializer().fields['data'])


def test_check_annotations_success_case_all_optional(settings):
    settings.API_STRICT_SCHEMA_VALIDATION = True
    schema = RestDoctorSchema()

    schema.map_field(WithMethodFieldFirstCorrectSerializer().fields['data'])


def test_check_annotations_success_case_all_not_optional(settings):
    settings.API_STRICT_SCHEMA_VALIDATION = True
    schema = RestDoctorSchema()

    schema.map_field(WithMethodFieldFirstCorrectSerializer().fields['data'])


def test_check_annotations_fail_case_method_not_list_annotated(settings):
    settings.API_STRICT_SCHEMA_VALIDATION = True
    schema = RestDoctorSchema()

    with pytest.raises(ImproperlyConfigured):
        schema.map_field(WithMethodFieldManyIncorrectSerializer().fields['data'])


def test_check_annotations_fail_case_many_true_not_specified(settings):
    settings.API_STRICT_SCHEMA_VALIDATION = True
    schema = RestDoctorSchema()

    with pytest.raises(ImproperlyConfigured):
        schema.map_field(WithMethodFieldOptionalManyIncorrectSerializer().fields['data'])


def test_check_annotations_success_case_all_many(settings):
    settings.API_STRICT_SCHEMA_VALIDATION = True
    schema = RestDoctorSchema()

    schema.map_field(WithMethodFieldManyCorrectSerializer().fields['data'])


def test_check_annotations_success_case_many_with_optional(settings):
    settings.API_STRICT_SCHEMA_VALIDATION = True
    schema = RestDoctorSchema()

    schema.map_field(WithMethodFieldOptionalManyCorrectSerializer().fields['data'])


def test_check_annotations_fail_case_list_field(settings):
    settings.API_STRICT_SCHEMA_VALIDATION = True
    schema = RestDoctorSchema()

    with pytest.raises(ImproperlyConfigured):
        schema.map_field(WithMethodFieldListFieldCorrectSerializer().fields['data'])


def test_check_annotations_success_case_list_field(settings):
    settings.API_STRICT_SCHEMA_VALIDATION = True
    schema = RestDoctorSchema()

    schema.map_field(WithMethodFieldListFieldIncorrectSerializer().fields['data'])


def test_check_annotations_fail_case_multiple_choice_field(settings):
    settings.API_STRICT_SCHEMA_VALIDATION = True
    schema = RestDoctorSchema()

    with pytest.raises(ImproperlyConfigured):
        schema.map_field(WithMethodFieldMultipleChoiceFieldCorrectSerializer().fields['data'])


def test_check_annotations_success_case_multiple_choice_field(settings):
    settings.API_STRICT_SCHEMA_VALIDATION = True
    schema = RestDoctorSchema()

    schema.map_field(WithMethodFieldMultipleChoiceFieldIncorrectSerializer().fields['data'])
