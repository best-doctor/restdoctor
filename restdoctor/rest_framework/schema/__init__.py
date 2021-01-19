from __future__ import annotations

from restdoctor.rest_framework.schema.generators import RefsSchemaGenerator
from restdoctor.rest_framework.schema.openapi import RestDoctorSchema
from restdoctor.rest_framework.schema.refs_registry import LocalRefsRegistry
from restdoctor.rest_framework.schema.resources import ResourceSchema
from restdoctor.rest_framework.schema.wrappers import SchemaWrapper

__all__ = [
    'RefsSchemaGenerator', 'RestDoctorSchema', 'LocalRefsRegistry', 'ResourceSchema', 'SchemaWrapper',
]
