from __future__ import annotations
from typing import TYPE_CHECKING

from rest_framework.parsers import JSONParser

if TYPE_CHECKING:
    from restdoctor.utils.custom_types import GenericContext


class BestDoctorParser(JSONParser):
    def __init__(self, media_type: str, api_params: GenericContext) -> None:
        self.media_type = media_type
        self.api_params = api_params
