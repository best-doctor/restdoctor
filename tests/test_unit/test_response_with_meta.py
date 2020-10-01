from rest_framework.renderers import JSONRenderer

from restdoctor.rest_framework.response import ResponseWithMeta


def test_response_with_meta_getstate():
    response = ResponseWithMeta(data={}, meta={})
    response.renderer_context = {}
    response.accepted_renderer = JSONRenderer()
    response.accepted_media_type = 'application/json'
    response.render()

    state = response.__getstate__()

    assert 'meta' not in state
    assert 'data' in state
