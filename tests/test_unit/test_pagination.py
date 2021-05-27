import pytest
from rest_framework.exceptions import NotFound
from rest_framework.request import Request

from restdoctor.constants import DEFAULT_MAX_PAGE_SIZE, DEFAULT_PAGE_SIZE


@pytest.mark.parametrize(
    'page,per_page,expected_size,expected_has_next,expected_has_prev',
    (
        (1, 0, 0, True, False),
        (1, 10, 10, True, False),
        (2, 10, 5, False, True),
        (2, 5, 5, True, True),
        (1, 200, 15, False, False),
        ('', 200, 15, False, False),
    ),
)
@pytest.mark.django_db
def test_page_number_pagination_paginate_queryset(
    mocker, n_models, rf, page_number_pagination, my_models_queryset, page, per_page,
    expected_size, expected_has_next, expected_has_prev,
):
    n_models(15)
    mocked_count = mocker.patch.object(my_models_queryset, 'count')
    mocked_count.return_value = 15
    request = Request(rf.get('/endpoint', data={'page': page, 'per_page': per_page}))

    paginated = page_number_pagination.paginate_queryset(my_models_queryset, request)
    paginated_response = page_number_pagination.get_paginated_response([])
    meta = paginated_response.meta

    assert len(paginated) == expected_size
    assert page_number_pagination.has_next == expected_has_next
    assert page_number_pagination.has_prev == expected_has_prev
    assert (meta['next_url'] is not None) == expected_has_next
    assert (meta['prev_url'] is not None) == expected_has_prev
    mocked_count.assert_called()


@pytest.mark.parametrize(
    'page,per_page,expected_size,expected_has_next,expected_has_prev',
    (
        (1, 10, 10, True, False),
        (2, 10, 5, False, True),
        (2, 5, 5, True, True),
        (1, 200, 15, False, False),
        ('', 200, 15, False, False),
    ),
)
@pytest.mark.django_db
def test_page_number_uncounted_pagination_paginate_queryset(
    mocker, n_models, rf, page_number_uncounted_pagination, my_models_queryset, page, per_page,
    expected_size, expected_has_next, expected_has_prev,
):
    n_models(15)
    mocked_count = mocker.patch.object(my_models_queryset, 'count')
    request = Request(rf.get('/endpoint', data={'page': page, 'per_page': per_page}))

    paginated = page_number_uncounted_pagination.paginate_queryset(my_models_queryset, request)

    assert len(paginated) == expected_size
    assert page_number_uncounted_pagination.has_next == expected_has_next
    assert page_number_uncounted_pagination.has_prev == expected_has_prev
    mocked_count.assert_not_called()


@pytest.mark.parametrize(
    'per_page,expected_per_page',
    (
        (10, 10),
        (100500, DEFAULT_MAX_PAGE_SIZE),
    ),
)
@pytest.mark.django_db
def test_max_per_page(rf, page_number_pagination, my_models_queryset, per_page, expected_per_page):
    request = Request(rf.get('/endpoint', data={'per_page': per_page}))

    _ = page_number_pagination.paginate_queryset(my_models_queryset, request)

    assert page_number_pagination.per_page == expected_per_page


@pytest.mark.django_db
def test_default_per_page(rf, page_number_pagination, my_models_queryset):
    request = Request(rf.get('/endpoint'))

    _ = page_number_pagination.paginate_queryset(my_models_queryset, request)

    assert page_number_pagination.per_page == DEFAULT_PAGE_SIZE


@pytest.mark.parametrize(
    'per_page',
    (
        ('',),
        ('None',),
    ),
)
@pytest.mark.django_db
def test_null_per_page(rf, page_number_pagination, my_models_queryset, per_page):
    request = Request(rf.get('/endpoint', data={'per_page': per_page}))

    _ = page_number_pagination.paginate_queryset(my_models_queryset, request)

    assert page_number_pagination.per_page == DEFAULT_PAGE_SIZE


@pytest.mark.parametrize(
    'page,expected_page',
    (
        (-1, 1),
        (0, 1),
        (1, 1),
        (2, 2),
    ),
)
@pytest.mark.django_db
def test_page_succes_case(rf, n_models, page_number_pagination, my_models_queryset, page, expected_page):
    n_models(15)
    request = Request(rf.get('/endpoint', data={'page': page, 'per_page': 10}))

    _ = page_number_pagination.paginate_queryset(my_models_queryset, request)

    assert page_number_pagination.page == expected_page


@pytest.mark.django_db
def test_incorrect_page_fail_case(rf, n_models, page_number_pagination, my_models_queryset):
    n_models(15)
    request = Request(rf.get('/endpoint', data={'page': 3, 'per_page': 10}))

    with pytest.raises(NotFound):
        _ = page_number_pagination.paginate_queryset(my_models_queryset, request)


@pytest.mark.django_db
def test_default_page(rf, page_number_pagination, my_models_queryset):
    request = Request(rf.get('/endpoint'))

    _ = page_number_pagination.paginate_queryset(my_models_queryset, request)

    assert page_number_pagination.page == 1


@pytest.mark.parametrize(
    'page',
    (
        ('',),
        ('None',),
    ),
)
@pytest.mark.django_db
def test_null_page(rf, page_number_pagination, my_models_queryset, page):
    request = Request(rf.get('/endpoint', data={'page': page}))

    _ = page_number_pagination.paginate_queryset(my_models_queryset, request)

    assert page_number_pagination.page == 1


@pytest.mark.parametrize(
    'per_page,expected_size,expected_has_next',
    (
        (0, 0, True),
        (10, 10, True),
        (5, 5, True),
        (200, 15, False),
    ),
)
@pytest.mark.django_db
def test_cursor_uuid_pagination_paginate_queryset(
    n_models, rf, cursor_uuid_pagination, my_models_queryset, per_page,
    expected_size, expected_has_next,
):
    n_models(15)
    request = Request(rf.get('/endpoint', data={'per_page': per_page}))

    paginated = cursor_uuid_pagination.paginate_queryset(my_models_queryset, request)

    assert len(paginated) == expected_size
    assert cursor_uuid_pagination.has_next == expected_has_next


@pytest.mark.django_db
def test_cursor_uuid_pagination_paginate_before_empty(
    n_models, rf, cursor_uuid_pagination, my_models_queryset,
):
    n_models(15)
    request = Request(rf.get('/endpoint', data={'before': ''}))

    paginated = cursor_uuid_pagination.paginate_queryset(my_models_queryset, request)

    assert len(paginated) == 15
    assert paginated[0].timestamp > paginated[-1].timestamp


@pytest.mark.django_db
def test_cursor_uuid_pagination_paginate_after(
    n_models, rf, cursor_uuid_pagination, my_models_queryset,
):
    n_models(15)
    request = Request(rf.get('/endpoint', data={'after': ''}))

    paginated = cursor_uuid_pagination.paginate_queryset(my_models_queryset, request)

    assert len(paginated) == 15
    assert paginated[0].timestamp < paginated[-1].timestamp


@pytest.mark.parametrize(
    'order,expected_count',
    (
        ('after', 14),
        ('before', 0),
    ),
)
@pytest.mark.django_db
def test_cursor_uuid_pagination_paginate_related_first(
    n_models, rf, cursor_uuid_pagination, my_models_queryset, order, expected_count,
):
    messages = n_models(15)
    request = Request(rf.get('/endpoint', data={order: messages[0].uuid}))

    paginated = cursor_uuid_pagination.paginate_queryset(my_models_queryset, request)

    assert len(paginated) == expected_count


@pytest.mark.parametrize(
    'order,expected_count',
    (
        ('after', 0),
        ('before', 14),
    ),
)
@pytest.mark.django_db
def test_cursor_uuid_pagination_paginate_related_last(
    n_models, rf, cursor_uuid_pagination, my_models_queryset, order, expected_count,
):
    messages = n_models(15)
    request = Request(rf.get('/endpoint', data={order: messages[-1].uuid}))

    paginated = cursor_uuid_pagination.paginate_queryset(my_models_queryset, request)

    assert len(paginated) == expected_count


@pytest.mark.parametrize(
    'index',
    (
        1, 7, 13,
    ),
)
@pytest.mark.django_db
def test_cursor_uuid_pagination_get_paginated_response_after_success_case(
    n_models, rf, cursor_uuid_pagination, my_models_queryset, index,
):
    order = 'after'
    messages = n_models(15)
    msg_uuid = messages[index].uuid
    request = Request(rf.get('/endpoint', data={order: msg_uuid}))

    _ = cursor_uuid_pagination.paginate_queryset(my_models_queryset, request)
    paginated_response = cursor_uuid_pagination.get_paginated_response([])
    boundaries = (
        str(messages[index + 1].uuid),
        str(messages[-1].uuid),
    )
    meta = paginated_response.meta

    assert order in meta
    assert meta[order] == messages[index].uuid
    assert 'after_url' in meta
    assert boundaries[-1] in meta['after_url']
    assert 'before_url' in meta
    assert boundaries[0] in meta['before_url']


@pytest.mark.parametrize(
    'index',
    (
        1, 7, 13,
    ),
)
@pytest.mark.django_db
def test_cursor_uuid_pagination_get_paginated_response_before_success_case(
    n_models, rf, cursor_uuid_pagination, my_models_queryset, index,
):
    order = 'before'
    messages = n_models(15)
    msg_uuid = messages[index].uuid
    request = Request(rf.get('/endpoint', data={order: msg_uuid}))

    _ = cursor_uuid_pagination.paginate_queryset(my_models_queryset, request)
    paginated_response = cursor_uuid_pagination.get_paginated_response([])
    boundaries = (
        str(messages[0].uuid),
        str(messages[index - 1].uuid),
    )
    meta = paginated_response.meta

    assert order in meta
    assert meta[order] == messages[index].uuid
    assert 'after_url' in meta
    assert boundaries[-1] in meta['after_url']
    assert 'before_url' in meta
    assert boundaries[0] in meta['before_url']


@pytest.mark.parametrize(
    'order',
    (
        'after',
        'before',
    ),
)
@pytest.mark.django_db
def test_cursor_uuid_pagination_get_paginated_response_no_uuid_specified_success_case(
    n_models, rf, cursor_uuid_pagination, my_models_queryset, order,
):
    messages = n_models(15)
    request = Request(rf.get('/endpoint', data={order: ''}))

    _ = cursor_uuid_pagination.paginate_queryset(my_models_queryset, request)
    paginated_response = cursor_uuid_pagination.get_paginated_response([])
    boundaries = (
        str(messages[0].uuid),
        str(messages[-1].uuid),
    )
    meta = paginated_response.meta

    assert order in meta
    assert meta[order] is None
    assert 'after_url' in meta
    assert boundaries[1] in meta['after_url']
    assert 'before_url' in meta
    assert boundaries[0] in meta['before_url']


@pytest.mark.django_db
def test_cursor_uuid_pagination_get_empty_response_success_case(
    n_models, rf, cursor_uuid_pagination, my_models_queryset,
):
    n_models(0)
    request = Request(rf.get('/endpoint'))

    _ = cursor_uuid_pagination.paginate_queryset(my_models_queryset, request)
    paginated_response = cursor_uuid_pagination.get_paginated_response([])
    meta = paginated_response.meta

    assert 'after_url' in meta
    assert 'before_url' in meta
    assert 'after' in meta['after_url']
    assert 'before' in meta['before_url']
