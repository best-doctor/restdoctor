from __future__ import annotations

import typing

from django.core.management.base import BaseCommand, CommandParser
from django.utils.module_loading import import_string
from rest_framework import renderers

from restdoctor.rest_framework.schema import RefsSchemaGenerator
from restdoctor.rest_framework.schema.custom_types import SchemaGenerator


class Command(BaseCommand):
    help = 'Generates configured API schema for project.'  # noqa: A003, VNE003

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('--title', dest='title', default='', type=str)
        parser.add_argument('--url', dest='url', default=None, type=str)
        parser.add_argument('--description', dest='description', default=None, type=str)
        parser.add_argument(
            '--format',
            dest='format',
            choices=['openapi', 'openapi-json'],
            default='openapi',
            type=str,
        )
        parser.add_argument('--urlconf', dest='urlconf', default=None, type=str)
        parser.add_argument('--accept', dest='accept', default=None, type=str)
        parser.add_argument('--generator_class', dest='generator_class', default=None, type=str)
        parser.add_argument('--file', dest='file', default=None, type=str)

    def handle(self, *args: typing.Any, **options: typing.Any) -> None:
        if options['generator_class']:
            generator_class = import_string(options['generator_class'])
        else:
            generator_class = self.get_generator_class()
        generator = generator_class(
            url=options['url'],
            title=options['title'],
            description=options['description'],
            urlconf=options['urlconf'],
            accept=options['accept'],
        )
        schema = generator.get_schema(request=None, public=True)
        renderer = self.get_renderer(options['format'])
        output = renderer.render(schema, renderer_context={})

        if options['file']:
            with open(options['file'], 'wb') as output:
                output.write(output)
        else:
            self.stdout.write(output.decode())

    def get_renderer(self, fmt: str) -> renderers.BaseRenderer:
        renderer_cls = {
            'openapi': renderers.OpenAPIRenderer,
            'openapi-json': renderers.JSONOpenAPIRenderer,
        }[fmt]
        return renderer_cls()

    def get_generator_class(self) -> typing.Type[SchemaGenerator]:
        return RefsSchemaGenerator
