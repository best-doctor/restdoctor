from __future__ import annotations

import enum

from yaml import Dumper, Node


def enum_representer(dumper: Dumper, data: enum.Enum) -> Node:
    representer = dumper.yaml_representers.get(type(data.value))
    if representer is not None:
        return representer(dumper, data.value)

    return dumper.represent_str(str(data.value))
