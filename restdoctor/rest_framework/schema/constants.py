from __future__ import annotations
import typing

if typing.TYPE_CHECKING:
    from restdoctor.rest_framework.schema.utils import ActionCodesMap


# True и False - относится ли action к коллекции или отдельному элементу
ACTIONS_MAP = {
    True: {'get': 'list', 'post': 'create'},
    False: {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'},
}

ACTION_CODES_MAP: ActionCodesMap = {
    'default': {
        '400': ('Ошибка валидации запроса.', {'$ref': '#/components/schemas/ErrorResponseSchema'}),
        '404': ('Ресурс не найден.', {'$ref': '#/components/schemas/NotFoundResponseSchema'}),
    },
    'get': {
        '200': 'Успешный запрос.'},
    'post': {
        '200': 'Успешный запрос.'},
    'patch': {
        '200': 'Успешный запрос.'},
    'put': {
        '200': 'Успешный запрос.'},
    'delete': {
        '204': 'Успешный запрос.'},
    'list': {
        '200': 'Успешный запрос коллекции.',
        '400': None,
        '404': None,
    },
    'retrieve': {
        '200': 'Успешный запрос объекта.'},
    'update': {
        '200': 'Успешное изменение объекта.'},
    'partial_update': {
        '200': 'Успешное изменение объекта.'},
    'create': {
        '201': 'Успешное создание объекта.'},
    'destroy': {
        '204': ('Успешное удаление объекта.', {}),
        '400': None,
    },
}
