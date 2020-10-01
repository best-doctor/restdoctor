from typing import List

from django.db.models import Model


def get_model_sensitive_fields(model: Model) -> List[str]:
    try:
        return model.SensitiveData.include
    except AttributeError:
        return []


def is_model_field_sensitive(model: Model, field_path: str) -> bool:
    field_name, *related_field_name = field_path.split('.', 1)
    if related_field_name:
        try:
            return is_model_field_sensitive(
                getattr(model, field_name).field.related_model, related_field_name[0],
            )
        except AttributeError:
            return False
    else:
        return field_name in get_model_sensitive_fields(model)
