from __future__ import annotations

import pytest
from rest_framework.request import Request


@pytest.mark.parametrize('page,per_page', ((1, 10),))
@pytest.mark.django_db
def test_retrieve(mocker, n_models, rf, page_number_uncounted_pagination, my_models_queryset):
    n_models(1)
    mocked_count = mocker.patch.object(my_models_queryset, 'count')
    request = Request(rf.get('/endpoint'))

    paginated = page_number_uncounted_pagination.paginate_queryset(my_models_queryset, request)

    mocked_count.assert_not_called()
