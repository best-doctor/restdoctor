from __future__ import annotations

from restdoctor.rest_framework.schema.generators import NewRefsSchemaGenerator, RefsSchemaGenerator
from restdoctor.rest_framework.schema.openapi import RestDoctorSchema
from restdoctor.rest_framework.schema.refs_registry import LocalRefsRegistry
from restdoctor.rest_framework.schema.resources import ResourceSchema
from restdoctor.rest_framework.schema.wrappers import SchemaWrapper

__all__ = [
    'RefsSchemaGenerator', 'NewRefsSchemaGenerator',
    'RestDoctorSchema', 'LocalRefsRegistry', 'ResourceSchema', 'SchemaWrapper',
]
