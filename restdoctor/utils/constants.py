import re


IDENTIFIER_REGEX = re.compile(r'^[^\d\W]\w*$', re.UNICODE)

DEFAULT_MAPPING_SET = {'list', 'retrieve', 'create', 'update', 'partial_update', 'destroy'}
